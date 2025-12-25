# utils/file_storage.py
import json
import os

TICKET_MAP_PATH = "ticket_map.json"

def load_ticket_map():
    if os.path.exists(TICKET_MAP_PATH):
        with open(TICKET_MAP_PATH, "r") as f:
            return json.load(f)
    return {}

def save_ticket_map(data):
    with open(TICKET_MAP_PATH, "w") as f:
        json.dump(data, f, indent=4)
