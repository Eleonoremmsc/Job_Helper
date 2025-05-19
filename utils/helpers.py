import json
import os

DATA_FILE = "user_data.json"

def load_user_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_user_data(all_data):
    with open(DATA_FILE, "w") as f:
        json.dump(all_data, f, indent=2)
