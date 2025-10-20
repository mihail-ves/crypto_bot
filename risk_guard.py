import json, time
from logger import log_info, log_error
from core.price_feed import get_price
from trade_memory import get_last_buy_price

RISK_FILE = "risk_guard.json"

# === Завантажити ризик-параметри ===
def load_risk_config():
    try:
        with open(RISK_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

# === Зберегти ризик-параметри ===
def save_risk_config(data):
    with open(RISK_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

# === Ініціалізувати монету для моніторингу ===
def track_asset(symbol):
    config = load_risk_config()
    if symbol not in config:
        config[symbol] = {
            "start_time": time.time(),
            "last_price": get_price(symbol),
            "max_drawdown": 0.0
        }
        save_risk_config(config)
        log_info(f"🛡 Ризик-моніторинг активовано для {symbol}")

# === Оцінити ризик по монеті ===
def evaluate_risk(symbol, max_hold_hours=6, max_drawdown_pct=10):
    config = load_risk_config()
    if symbol not in config:
        log_error(f"⚠️ {symbol} не відстежується")
        return False, "Монета не відстежується"

    now = time.time()
    entry_time = config[symbol]["start_time"]
    hold_duration = (now - entry_time) / 3600

    current_price = get_price(symbol)
    last_buy = get_last_buy_price(symbol)
    if last_buy is None or current_price is None:
        return False, "Немає даних для оцінки"

    drawdown = ((last_buy - current_price) / last_buy) * 100
    config[symbol]["max_drawdown"] = max(config[symbol]["max_drawdown"], drawdown)
    save_risk_config(config)

    if drawdown >= max_drawdown_pct:
        return True, f"🔻 Просадка {drawdown:.2f}% ≥ {max_drawdown_pct}%"

    if hold_duration >= max_hold_hours:
        return True, f"⏳ Утримання {hold_duration:.2f} год ≥ {max_hold_hours} год"

    return False, f"✅ Ризик в межах норми: просадка {drawdown:.2f}%, час {hold_duration:.2f} год"
