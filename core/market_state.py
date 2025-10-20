# core/market_state.py

latest_prices = {}

def update_price(symbol: str, price: float):
    latest_prices[symbol] = price

def get_latest_price(symbol: str) -> float:
    return latest_prices.get(symbol)
