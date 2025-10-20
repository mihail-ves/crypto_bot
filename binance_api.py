# binance_api.py
from binance.client import Client
from telegram_notifier import send_telegram_message
from logger import log_info, log_error
from config.config_loader import CONFIG
from core.price_feed import get_price  # ← новий імпорт

# === Конфігурація ===
API_KEY = CONFIG.get("API_KEY", "")
API_SECRET = CONFIG.get("API_SECRET", "")
MODE = CONFIG.get("MODE", "test")  # "live" або "test"

# === Перевірка ключів ===
if MODE == "live" and (not API_KEY or not API_SECRET):
    log_error("❌ Відсутні API-ключі для live-режиму")
    send_telegram_message("❌ Binance API: ключі не задані")
    raise ValueError("API credentials missing")

# === Ініціалізація клієнта Binance ===
client = Client(API_KEY, API_SECRET) if MODE == "live" else None

# === Отримати баланс активу ===
def get_balance(asset):
    """
    Повертає баланс активу.
    """
    try:
        if MODE == "live":
            info = client.get_asset_balance(asset=asset)
            balance = float(info["free"])
            log_info(f"💰 Баланс {asset}: {balance}")
            return balance
        else:
            log_error("❌ get_balance не підтримується в mock-режимі через циклічний імпорт")
            return 0.0
    except Exception as e:
        log_error(f"❌ Binance get_balance помилка: {e}")
        send_telegram_message(f"❌ Binance API get_balance помилка: {e}")
        return 0.0

# === Виконати ордер ===
def place_order(symbol, side, quantity):
    """
    Виконує ордер BUY або SELL через Binance API.
    """
    price = get_price(symbol)

    if price is None:
        return {"id": "ERROR", "price": "N/A", "status": "FAILED", "message": "Ціна недоступна"}

    try:
        if MODE == "live":
            order = client.create_order(
                symbol=symbol,
                side=side,
                type="MARKET",
                quantity=quantity
            )
            fills = order.get("fills", [])
            fill_price = fills[0]["price"] if fills else "N/A"

            log_info(f"✅ LIVE ордер {side} {symbol} @ {fill_price}")
            return {
                "id": order.get("orderId", "N/A"),
                "price": fill_price,
                "status": order.get("status", "UNKNOWN")
            }

        else:
            log_error("❌ place_order не підтримується в mock-режимі — використовуйте simulate_buy/sell у bot_control.py")
            return {"id": "SIM_DISABLED", "price": price, "status": "SKIPPED", "message": "Mock mode: use simulate_buy/sell"}

    except Exception as e:
        log_error(f"❌ Binance place_order помилка: {e}")
        send_telegram_message(f"❌ Binance API place_order помилка: {e}")
        return {"id": "ERROR", "price": "N/A", "status": "FAILED", "message": str(e)}
