import json
from logger import log_info, log_error

MEMORY_FILE = "trade_memory.json"

# === Завантажити пам'ять ===
def load_memory():
    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

# === Зберегти пам'ять ===
def save_memory(data):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

# === Записати останню купівлю ===
def record_buy(symbol, price):
    memory = load_memory()
    memory[symbol] = {
        "last_buy_price": price
    }
    save_memory(memory)
    log_info(f"🧠 Записано покупку {symbol} @ {price:.4f}")

# === Отримати останню купівлю ===
def get_last_buy_price(symbol):
    memory = load_memory()
    return memory.get(symbol, {}).get("last_buy_price", None)

# === Перевірити чи продаж прибутковий ===
def is_profitable_sell(symbol, current_price, min_margin=0.002):
    last_price = get_last_buy_price(symbol)
    if last_price is None:
        log_info(f"ℹ️ Немає даних про останню купівлю {symbol}")
        return True  # дозволити продаж

    required_price = last_price * (1 + min_margin)
    if current_price >= required_price:
        log_info(f"✅ Продаж вигідний: {current_price:.4f} ≥ {required_price:.4f}")
        return True
    else:
        log_info(f"⛔ Продаж НЕ вигідний: {current_price:.4f} < {required_price:.4f}")
        return False
