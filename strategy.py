# strategy.py

MIN_HISTORY = 6  # Мінімальна кількість точок для аналізу

def should_buy(price_history):
    """
    Визначає, чи варто купувати актив на основі падіння ціни.

    Логіка:
        - Якщо поточна ціна нижча за ціну 5 кроків назад більш ніж на 0.5% — сигнал BUY.
    """
    if len(price_history) < MIN_HISTORY:
        return False
    current = price_history[-1]
    previous = price_history[-5]
    return current < previous * 0.995  # падіння >0.5%

def should_sell(price_history):
    """
    Визначає, чи варто продавати актив на основі зростання ціни.

    Логіка:
        - Якщо поточна ціна вища за ціну 5 кроків назад більш ніж на 0.5% — сигнал SELL.
    """
    if len(price_history) < MIN_HISTORY:
        return False
    current = price_history[-1]
    previous = price_history[-5]
    return current > previous * 1.005  # зростання >0.5%
