# analytics.py

def atr(prices, period=5):
    """
    Обчислює середній істинний діапазон (ATR) — показник волатильності.

    Аргументи:
        prices (list): Історія цін.
        period (int): Кількість періодів для розрахунку.

    Повертає:
        float: Середнє абсолютне відхилення за останні N періодів.
    """
    if len(prices) < period + 1:
        return 0.0

    diffs = [abs(prices[i] - prices[i - 1]) for i in range(1, len(prices))]
    return sum(diffs[-period:]) / period


def breakout(prices):
    """
    Визначає, чи поточна ціна перевищує локальний максимум останніх 4 періодів.

    Аргументи:
        prices (list): Історія цін.

    Повертає:
        bool: True, якщо breakout; False — інакше.
    """
    if len(prices) < 5:
        return False
    return prices[-1] > max(prices[-5:-1])


def btc_eth_ratio(btc_price, eth_price):
    """
    Обчислює співвідношення ціни BTC до ETH.

    Аргументи:
        btc_price (float): Поточна ціна BTC.
        eth_price (float): Поточна ціна ETH.

    Повертає:
        float: Округлене співвідношення BTC/ETH.
    """
    if eth_price == 0:
        return 0.0
    return round(btc_price / eth_price, 2)
