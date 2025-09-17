#await sio.emit("update_controls", controls)

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
