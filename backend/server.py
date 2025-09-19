# backend.py
import os
import time
import tempfile
import asyncio
from flask import Flask, send_file, request
from flask_socketio import SocketIO
import edge_tts
from flask_cors import CORS

from simple import init, aiMsg  # LLM wrapper
from protocol import secrete

#    Flask + SocketIO   
app = Flask(__name__)
toolBind = init()
CORS(app)
app.config["SECRET_KEY"] = secrete
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

#    Viseme mapping   
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

#    TTS   
def generate_tts_file(text, voice="en-US-AriaNeural"):
    """Generate MP3 using Edge TTS and return filename"""
    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tmp_file.close()

    async def gen():
        communicate = edge_tts.Communicate(text, voice=voice)
        await communicate.save(tmp_file.name)

    asyncio.run(gen())
    return tmp_file.name

#    SocketIO   
@socketio.on("connect")
def on_connect():
    print("[Socket.IO] Client connected")

@socketio.on("disconnect")
def on_disconnect():
    print("[Socket.IO] Client disconnected")

@socketio.on("hello_world")
def on_hello_world(data):
    rawtext = data.get("text", "").strip()
    if not rawtext:
        return

    llm_output = aiMsg(toolBind, rawtext)
    print(f"[Socket.IO] LLM OUTPUT: {llm_output}")
    viseme_sequence = compute_visemes(llm_output)
    tmp_file = generate_tts_file(llm_output)
    socketio.emit("play_audio", {
        "audio_url": f"/audio/{os.path.basename(tmp_file)}",
        "visemes": viseme_sequence
    })

# Serve generated audio 
@app.route("/audio/<filename>")
def serve_audio(filename):
    path = os.path.join(tempfile.gettempdir(), filename)
    if not os.path.exists(path):
        return "File not found", 404
    return send_file(path, mimetype="audio/mpeg")

# Run server 
if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000)
