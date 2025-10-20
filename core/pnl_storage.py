import json
import os

PNL_FILE = "data/pnl_history.json"

def save_pnl_history(pnl_history: list):
    os.makedirs(os.path.dirname(PNL_FILE), exist_ok=True)
    with open(PNL_FILE, "w") as f:
        json.dump(pnl_history, f)

def load_pnl_history() -> list:
    if os.path.exists(PNL_FILE):
        with open(PNL_FILE, "r") as f:
            return json.load(f)
    return []
