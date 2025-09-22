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

default = {
    "headX": 0, "headY": 0, "headZ": 0,
    "spineX": 0, "spineY": 0, "spineZ": 0,
    "leftArmX": 0, "leftArmY": 0, "leftArmZ": -1,
    "rightArmX": 0, "rightArmY": 0, "rightArmZ": 1,
    "leftLegX": 0, "leftLegY": 0, "leftLegZ": 0,
    "rightLegX": 0, "rightLegY": 0, "rightLegZ": 0,
    "blinkToggle": False, "blinkIntensity": 0.8, "emotionIntensity": 0.28,
    "emotions": {"angry": False, "fun": False, "joy": False, "sorrow": False, "surprised": False},
    "mouth": {"A": 0, "I": 0, "U": 0, "E": 0, "O": 0}
}

emo = {
    "neutral" : {
        "headX": 0, "headY": 0, "headZ": 0,
        "spineX": 0, "spineY": 0, "spineZ": 0,
        "leftArmX": 0, "leftArmY": 0, "leftArmZ": -1,
        "rightArmX": 0, "rightArmY": 0, "rightArmZ": 1,
        "leftLegX": 0, "leftLegY": 0, "leftLegZ": 0,
        "rightLegX": 0, "rightLegY": 0, "rightLegZ": 0,
        "blinkToggle": False, "blinkIntensity": 0.8, "emotionIntensity": 0.28,
        "emotions": {"angry": False, "fun": False, "joy": False, "sorrow": False, "surprised": False},
        "mouth": {"A": 0, "I": 0, "U": 0, "E": 0, "O": 0}
    },

    "angry" : {
        "headX": 0, "headY": 0, "headZ": 0,
        "spineX": 0, "spineY": 0, "spineZ": 0,
        "leftArmX": 0, "leftArmY": 0, "leftArmZ": -1,
        "rightArmX": 0, "rightArmY": 0, "rightArmZ": 1,
        "leftLegX": 0, "leftLegY": 0, "leftLegZ": 0,
        "rightLegX": 0, "rightLegY": 0, "rightLegZ": 0,
        "blinkToggle": False, "blinkIntensity": 0.8, "emotionIntensity": 0.28,
        "emotions": {"angry": True, "fun": False, "joy": False, "sorrow": False, "surprised": False},
        "mouth": {"A": 0, "I": 0, "U": 0, "E": 0, "O": 0}
    },

    "fun" : {
        "headX": 0, "headY": 0, "headZ": 0,
        "spineX": 0, "spineY": 0, "spineZ": 0,
        "leftArmX": 0, "leftArmY": 0, "leftArmZ": -1,
        "rightArmX": 0, "rightArmY": 0, "rightArmZ": 1,
        "leftLegX": 0, "leftLegY": 0, "leftLegZ": 0,
        "rightLegX": 0, "rightLegY": 0, "rightLegZ": 0,
        "blinkToggle": False, "blinkIntensity": 0.8, "emotionIntensity": 0.28,
        "emotions": {"angry": False, "fun": True, "joy": False, "sorrow": False, "surprised": False},
        "mouth": {"A": 0, "I": 0, "U": 0, "E": 0, "O": 0}
    },

    "joy" : {
        "headX": 0, "headY": 0, "headZ": 0,
        "spineX": 0, "spineY": 0, "spineZ": 0,
        "leftArmX": 0, "leftArmY": 0, "leftArmZ": -1,
        "rightArmX": 0, "rightArmY": 0, "rightArmZ": 1,
        "leftLegX": 0, "leftLegY": 0, "leftLegZ": 0,
        "rightLegX": 0, "rightLegY": 0, "rightLegZ": 0,
        "blinkToggle": False, "blinkIntensity": 0.8, "emotionIntensity": 0.28,
        "emotions": {"angry": False, "fun": False, "joy": True, "sorrow": False, "surprised": False},
        "mouth": {"A": 0, "I": 0, "U": 0, "E": 0, "O": 0}
    },

    "sorrow" : {
        "headX": 0, "headY": 0, "headZ": 0,
        "spineX": 0, "spineY": 0, "spineZ": 0,
        "leftArmX": 0, "leftArmY": 0, "leftArmZ": -1,
        "rightArmX": 0, "rightArmY": 0, "rightArmZ": 1,
        "leftLegX": 0, "leftLegY": 0, "leftLegZ": 0,
        "rightLegX": 0, "rightLegY": 0, "rightLegZ": 0,
        "blinkToggle": False, "blinkIntensity": 0.8, "emotionIntensity": 0.28,
        "emotions": {"angry": False, "fun": False, "joy": False, "sorrow": True, "surprised": False},
        "mouth": {"A": 0, "I": 0, "U": 0, "E": 0, "O": 0}
    },

    "surprised" : {
        "headX": 0, "headY": 0, "headZ": 0,
        "spineX": 0, "spineY": 0, "spineZ": 0,
        "leftArmX": 0, "leftArmY": 0, "leftArmZ": -1,
        "rightArmX": 0, "rightArmY": 0, "rightArmZ": 1,
        "leftLegX": 0, "leftLegY": 0, "leftLegZ": 0,
        "rightLegX": 0, "rightLegY": 0, "rightLegZ": 0,
        "blinkToggle": False, "blinkIntensity": 0.8, "emotionIntensity": 0.28,
        "emotions": {"angry": False, "fun": False, "joy": False, "sorrow": False, "surprised": True},
        "mouth": {"A": 0, "I": 0, "U": 0, "E": 0, "O": 0}
    },

    "flirty" : {
        "headX": 0, "headY": 0, "headZ": 0,
        "spineX": 0, "spineY": 0, "spineZ": 0,
        "leftArmX": 0, "leftArmY": 0, "leftArmZ": -1,
        "rightArmX": 0, "rightArmY": 0, "rightArmZ": 1,
        "leftLegX": 0, "leftLegY": 0, "leftLegZ": 0,
        "rightLegX": 0, "rightLegY": 0, "rightLegZ": 0,
        "blinkToggle": True, "blinkIntensity": 0.16, "emotionIntensity": 0.21,
        "emotions": {"angry": False, "fun": True, "joy": False, "sorrow": False, "surprised": False},
        "mouth": {"A": 0.19, "I": 0.58, "U": 0, "E": 0, "O": 0}
    },

    "extremespicy" : {
        "headX": 0, "headY": 0, "headZ": 0,
        "spineX": 0, "spineY": 0, "spineZ": 0,
        "leftArmX": 0, "leftArmY": 0, "leftArmZ": -1,
        "rightArmX": 0, "rightArmY": 0, "rightArmZ": 1,
        "leftLegX": 0, "leftLegY": 0, "leftLegZ": 0,
        "rightLegX": 0, "rightLegY": 0, "rightLegZ": 0,
        "blinkToggle": True, "blinkIntensity": 0.18, "emotionIntensity": 0.45,
        "emotions": {"angry": False, "fun": True, "joy": False, "sorrow": False, "surprised": False},
        "mouth": {"A": 0.19, "I": 0.58, "U": 0, "E": 0, "O": 0}
    }
}

def emotionParser(key):
    return emo.get(key.lower(), emo["neutral"])
