# backend.py
import os
import time
import tempfile
import asyncio
from flask import Flask, send_file, request
from flask_socketio import SocketIO
import edge_tts
# backend.py
from flask_cors import CORS
from random import random


# Flask + SocketIO
app = Flask(__name__)
CORS(app)  # add this after Flask app creation
app.config["SECRET_KEY"] = "secret!"
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

# viseme Mapping
def char_to_viseme(c):
    c = c.lower()
    if c in "aáàâä": return "A"
    if c in "iíìîïy": return "I"
    if c in "uúùûü": return "U"
    if c in "eéèêë": return "E"
    if c in "oóòôö": return "O"
    return None

def compute_visemes(text):
    visemes = []
    for char in text:
        v = char_to_viseme(char)
        visemes.append({"mouth": {v: 1} if v else {}})
    return visemes

# ---------------- TTS ----------------
def generate_tts_file(text):
    """Generate MP3 using Edge TTS and return filename"""
    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tmp_file.close()

    async def gen():
        communicate = edge_tts.Communicate(text, voice="en-US-JennyNeural")
        await communicate.save(tmp_file.name)

    asyncio.run(gen())
    return tmp_file.name

@app.route("/tts", methods=["GET"])
def tts():
    rawText = request.args.get("text", "").strip()
    if not rawText:
        return "No text provided", 400

    # Cerate temp file
    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tmp_file.close()

    llmText = f"Here is a random number: {random()}.\nAlso, the text you provided is: {rawText}"

    async def gen():
        communicate = edge_tts.Communicate(llmText, voice="en-US-AriaNeural")
        await communicate.save(tmp_file.name)

    # run async TTS syncronously
    asyncio.run(gen())

    # Send the file (do not delete immediately, Windows will fucking lock it)
    response = send_file(tmp_file.name, mimetype="audio/mpeg")
    return response


#  SocketIO
@socketio.on("connect")
def on_connect():
    print("[Socket.IO] Client connected")

@socketio.on("disconnect")
def on_disconnect():
    print("[Socket.IO] Client disconnected")

@socketio.on("hello_world")
def on_hello_world(data):
    text = data.get("text", "").strip()
    if not text:
        return

    #Generate visemes sequence
    viseme_sequence = compute_visemes(text)

    #Generate audio file
    tmp_file = generate_tts_file(text)

    #Notify frontend to play audio and start visemes
    socketio.emit("play_audio", {"audio_url": f"/tts?file={os.path.basename(tmp_file)}", "visemes": viseme_sequence})


    print(f"[Socket.IO] SPEAK: {text}")
    viseme_sequence = compute_visemes(text)
    for vis in viseme_sequence:
        socketio.emit("update_controls", vis)
        time.sleep(0.2)  # 50ms per char

# Run Server
if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000)
