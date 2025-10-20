# trade_config.py
import json
from logger import log_info, log_error

CONFIG_PATH = "config.json"

# === Завантаження конфігурації ===
def load_config():
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("SYMBOL", "BTCUSDT"), data.get("TRADE_AMOUNT", 0.01)
    except Exception as e:
        log_error(f"❌ Помилка при завантаженні конфігурації: {e}")
        return "BTCUSDT", 0.01

# === Збереження конфігурації ===
def save_config(symbol, amount):
    try:
        # Завантажити існуючий конфіг
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Оновити лише потрібні поля
        data["SYMBOL"] = symbol
        data["TRADE_AMOUNT"] = amount

        # Зберегти назад
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        log_info(f"⚙️ Збережено конфігурацію: {symbol}, {amount}")
    except Exception as e:
        log_error(f"❌ Помилка при збереженні конфігурації: {e}")

# === Оновлення символу ===
def update_symbol(symbol):
    """
    Оновлює символ у конфігурації та глобальну змінну current_symbol.
    """
    global current_symbol, current_amount
    save_config(symbol, current_amount)
    current_symbol, current_amount = load_config()
    log_info(f"🔄 SYMBOL оновлено на {symbol}")

# === Глобальні змінні ===
current_symbol, current_amount = load_config()
