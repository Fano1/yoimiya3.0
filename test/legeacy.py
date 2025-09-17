import asyncio
import socketio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from socketio.asgi import ASGIApp
import uvicorn
import edge_tts
from pydub import AudioSegment
from pydub.playback import _play_with_simpleaudio
import io
import random

# -------------------- Setup --------------------
sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")
app = FastAPI()
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)
asgi_app = ASGIApp(sio, other_asgi_app=app)

# -------------------- Default controls --------------------
controls = {
    "headX": 0, "headY": 0, "headZ": 0,
    "spineX": 0, "spineY": 0, "spineZ": 0,
    "leftArmX": 0, "leftArmY": 0, "leftArmZ": 0,
    "rightArmX": 0, "rightArmY": 0, "rightArmZ": 0,
    "leftLegX": 0, "leftLegY": 0, "leftLegZ": 0,
    "rightLegX": 0, "rightLegY": 0, "rightLegZ": 0,
    "blinkToggle": True, "blinkIntensity": 0.8, "emotionIntensity": 0.8,
    "emotions": {"angry": False, "fun": False, "joy": False, "sorrow": False, "surprised": False},
    "mouth": {"A": 0, "I": 0, "U": 0, "E": 0, "O": 0}
}

# -------------------- Letter-to-viseme mapping --------------------
def text_to_viseme(char):
    char = char.lower()
    if char in "aáàâä":
        return "A"
    elif char in "iíìîïy":
        return "I"
    elif char in "uúùûü":
        return "U"
    elif char in "eéèêë":
        return "E"
    elif char in "oóòôö":
        return "O"
    else:
        return None

# -------------------- Speak text with MP3 and animate mouth --------------------
async def speak_text(text):
    visemes = ["A", "I", "U", "E", "O"]
    current = {v: 0 for v in visemes}

    tts = edge_tts.Communicate(text, voice="en-US-JennyNeural")
    mp3_bytes = b""
    async for chunk in tts.stream():
        if chunk.get("type") == "audio":
            mp3_bytes += chunk.get("audio") or chunk.get("data") or b""

    audio = AudioSegment.from_file(io.BytesIO(mp3_bytes), format="mp3")
    play_obj = _play_with_simpleaudio(audio)

    # animate mouth (letter-to-viseme)
    for char in text:
        target_viseme = text_to_viseme(char)
        target = {v: 0 for v in visemes}
        if target_viseme:
            target[target_viseme] = 1.0
        steps = 5
        for _ in range(steps):
            for v in visemes:
                current[v] += (target[v] - current[v]) * 0.5
            controls["mouth"] = current.copy()
            await sio.emit("update_controls", controls)
            await asyncio.sleep(0.05)

    controls["mouth"] = {v: 0 for v in visemes}
    await sio.emit("update_controls", controls)
    play_obj.wait_done()


# -------------------- Idle mouth --------------------
async def idle_mouth_loop():
    visemes = ["A", "I", "U", "E", "O"]
    current = {v: 0 for v in visemes}
    while True:
        new_viseme = random.choice(visemes)
        target = {v: 0 for v in visemes}
        target[new_viseme] = random.uniform(0.3, 0.8)
        steps = 10
        for _ in range(steps):
            for v in visemes:
                current[v] += (target[v] - current[v]) * 0.3
            controls["mouth"] = current.copy()
            await sio.emit("update_controls", controls)
            await asyncio.sleep(0.05)
        await asyncio.sleep(random.uniform(0.3, 0.8))

# -------------------- Socket.IO Events --------------------
@sio.event
async def connect(sid, environ):
    print(f"Client connected: {sid}")
    await sio.emit("update_controls", controls, room=sid)

@sio.event
async def disconnect(sid):
    print(f"Client disconnected: {sid}")

@sio.event
async def hello_world(sid, data):
    text = data.get("text", "")
    if text.strip():
        print(f"SPEAK: {text}")
        await speak_text(text)

@sio.event
async def controls_update(sid, data):
    controls.update(data)
    await sio.emit("update_controls", controls)

# -------------------- Startup Hook --------------------
@app.on_event("startup")
async def start_background_tasks():
    # asyncio.create_task(idle_mouth_loop())
    pass

# -------------------- Run --------------------
if __name__ == "__main__":
    uvicorn.run(asgi_app, host="0.0.0.0", port=5000)
