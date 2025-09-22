import os
import json
import tempfile
import asyncio
from flask import Flask, send_file, request
from flask_socketio import SocketIO
import edge_tts
from flask_cors import CORS
from simple import init, aiMsg  # Updated LLM wrapper
from protocol import secrete, initDB, saveMSG, loadBuffer
from collection import emotionParser

# Flask + SocketIO  
app = Flask(__name__)
tool_model, structured_model = init()
CORS(app)
app.config["SECRET_KEY"] = secrete
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")
initDB()  # sets up DB with WAL and index

def char_to_viseme(c):
    c = c.lower()
    if c in "aáàâä": return "A"
    if c in "iíìîïy": return "I"
    if c in "uúùûü": return "U"
    if c in "eéèêë": return "E"
    if c in "oóòôö": return "O"
    return None

def compute_visemes(text, char_time=0.09):
    visemes = []
    current_time = 0
    for char in text:
        v = char_to_viseme(char)
        visemes.append({"time": current_time, "mouth": {v: 1} if v else {}})
        current_time += char_time
    return visemes

# TTS  
def generate_tts_file(text, voice="en-US-AriaNeural"):
    """Generate MP3 using Edge TTS and return filename"""
    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tmp_file.close()
    
    async def gen():
        communicate = edge_tts.Communicate(text, voice=voice)
        await communicate.save(tmp_file.name)
    
    asyncio.run(gen())
    return tmp_file.name

# SocketIO  
@socketio.on("connect")
def on_connect():
    print(f"[Socket.IO] Client connected: {request.sid}")

@socketio.on("disconnect")
def on_disconnect():
    print(f"[Socket.IO] Client disconnected: {request.sid}")

@socketio.on("hello_world")
def on_hello_world(data):
    session_id = request.sid  # unique per client
    rawtext = data.get("text", "").strip()
    
    if not rawtext:
        print("[Socket.IO] Empty message received")
        return

    print(f"[Socket.IO] Processing message for session {session_id}: {rawtext}")
    
    saveMSG(session_id, "user", rawtext)
    
    conversation_history = loadBuffer(session_id, limit=10)  
    
    llm_output_raw = aiMsg(tool_model, structured_model, rawtext, session_id=session_id, history=conversation_history)
    
    try:
        llm_output_json = json.loads(llm_output_raw)
        llm_output = llm_output_json["reply"]
        emotion = emotionParser(llm_output_json["emotion"])
        
        # svae assistant response
        saveMSG(session_id, "assistant", llm_output)
        
        print(f"[Socket.IO] LLM OUTPUT: {llm_output}")
        print(f"[Socket.IO] Emotion: {emotion}")
        
        # Esnd emotion update
        socketio.emit("update_controls", emotion, room=session_id)
        
        # Generate visemses and TTS
        viseme_sequence = compute_visemes(llm_output)
        tmp_file = generate_tts_file(llm_output)
        
        # Send audio and visemses
        socketio.emit("play_audio", {
            "audio_url": f"/audio/{os.path.basename(tmp_file)}",
            "visemes": viseme_sequence
        }, room=session_id)
        
    except json.JSONDecodeError as e:
        print(f"[Socket.IO] JSON decode error: {e}")
        print(f"[Socket.IO] Raw output: {llm_output_raw}")
        
        # Fallback response
        socketio.emit("play_audio", {
            "audio_url": None,
            "visemes": [],
            "error": "Failed to process response"
        }, room=session_id)
    
    except Exception as e:
        print(f"[Socket.IO] Unexpected error: {e}")
        socketio.emit("play_audio", {
            "audio_url": None,
            "visemes": [],
            "error": "Server error occurred"
        }, room=session_id)

@app.route("/audio/<filename>")
def serve_audio(filename):
    path = os.path.join(tempfile.gettempdir(), filename)
    if not os.path.exists(path):
        print(f"[Audio] File not found: {path}")
        return "File not found", 404
    return send_file(path, mimetype="audio/mpeg")

if __name__ == "__main__":
    print("[Server] Starting with session-aware LLM...")
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)