import requests
from logger import log_error

def get_price(symbol: str) -> float:
    """
    Отримує поточну ціну для заданого символу з Binance.
    """
    try:
        url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
        response = requests.get(url)
        data = response.json()
        return float(data["price"])
    except Exception as e:
        log_error(f"❌ Помилка при отриманні ціни для {symbol}: {e}")
        return None
