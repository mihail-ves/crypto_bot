# core/trade_control.py
import time
from core.state import trading_enabled

# Перемикач автоматичної торгівлі
auto_trade_enabled = True

# Мінімальний інтервал між ордерами (в секундах)
min_interval_between_trades = 15 * 60  # 15 хвилин

# Час останньої торгівлі
last_trade_time = 0

def can_trade_now():
    if not trading_enabled or not auto_trade_enabled:
        return False
    return time.time() - last_trade_time >= min_interval_between_trades

def update_trade_time():
    global last_trade_time
    last_trade_time = time.time()

def toggle_auto_trade():
    global auto_trade_enabled
    auto_trade_enabled = not auto_trade_enabled
    return auto_trade_enabled


def get_auto_trade_status():
    from core.state import signal_history, price_history
    from datetime import datetime

    last_signal = signal_history[-1] if signal_history else "—"
    last_price = price_history[-1] if price_history else "—"
    last_time = datetime.fromtimestamp(last_trade_time).strftime("%Y-%m-%d %H:%M:%S") if last_trade_time else "—"
    status = "✅ Увімкнено" if auto_trade_enabled else "⛔️ Вимкнено"

    return {
        "status": status,
        "last_time": last_time,
        "last_signal": last_signal,
        "last_price": round(last_price, 2) if isinstance(last_price, (int, float)) else last_price
    }
