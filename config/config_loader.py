# config_loader.py
import json

CONFIG_PATH = "config.json"

# === Завантаження конфігурації ===
try:
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        CONFIG = json.load(f)
except Exception as e:
    CONFIG = {}
    print(f"❌ Помилка при завантаженні конфігурації: {e}")
