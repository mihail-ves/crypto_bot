# market_api.py
import json
from binance.client import Client

with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

API_KEY = config["API_KEY"]
API_SECRET = config["API_SECRET"]
MODE = config["MODE"]

client = Client(API_KEY, API_SECRET) if MODE == "live" else None

def get_price(symbol):
    """
    Повертає поточну ринкову ціну для заданого символу.
    """
    try:
        if MODE == "live":
            ticker = client.get_symbol_ticker(symbol=symbol)
            price = float(ticker["price"])
            log_info(f"📈 Ціна {symbol}: {price}")
            return price

        # === MOCK режим: використовує останню збережену ціну ===
        price = get_latest_price(symbol)
        if price is not None:
            log_info(f"📊 MOCK ціна {symbol}: {price}")
            return price

        return 100.0  # fallback для невідомих символів

    except Exception as e:
        log_error(f"❌ Binance get_price помилка: {e}")
        send_telegram_message(f"❌ Binance API get_price помилка: {e}")
        return None


def get_balance(asset):
    if MODE == "live":
        info = client.get_asset_balance(asset=asset)
        return float(info["free"])
    else:
        return 1000.0
