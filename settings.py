import json
import os

SETTINGS_PATH = "data/tutor_settings.json"

DEFAULT_SETTINGS = {
    "language": "RO",
    "depth": "medium",
    "model": "gpt-4o-mini",
    "temperature": 0.5,
    "max_tokens": 300
}

def load_settings():
    if not os.path.exists(SETTINGS_PATH):
        save_settings(DEFAULT_SETTINGS)
        return DEFAULT_SETTINGS
    with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_settings(data):
    with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
