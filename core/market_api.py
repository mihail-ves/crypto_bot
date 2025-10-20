# core/market_api.py
# market_api.py — альтернативний API
from core.state import MODE
from logger import log_error, log_info
from telegram_notifier import send_telegram_message
from trader import price_history  # якщо не створює циклічний імпорт
from core.market_state import get_latest_price

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
    """
    Повертає фіксований тестовий баланс.
    """
    return 1000.0

def place_order(symbol, side, quantity):
    """
    Симулює виконання ордера.
    """
    return {
        "id": "MOCK_ORDER",
        "price": get_price(symbol),
        "status": "FILLED"
    }
