# chart_generator.py
import matplotlib.pyplot as plt
from io import BytesIO
from logger import log_info, log_error

def generate_chart(prices, signals):
    """
    Генерує графік ціни з позначками BUY/SELL.

    Аргументи:
        prices (list): Історія цін.
        signals (list): Історія сигналів ("BUY", "SELL", "SKIPPED_BUY", "SKIPPED_SELL", "NONE").

    Результат:
        Повертає BytesIO-об'єкт з PNG-графіком.
    """
    try:
        if len(prices) == 0 or len(signals) == 0:
            log_error("❌ Неможливо побудувати графік — порожні дані.")
            return None

        plt.figure(figsize=(10, 5))
        plt.plot(prices, label='Price', color='blue')

        for i, signal in enumerate(signals):
            if i >= len(prices):
                continue

            if signal == 'BUY':
                plt.plot(i, prices[i], 'go', label='BUY' if i == 0 else "")
            elif signal == 'SELL':
                plt.plot(i, prices[i], 'ro', label='SELL' if i == 0 else "")
            elif signal == 'SKIPPED_BUY':
                plt.plot(i, prices[i], 'yo', label='SKIPPED_BUY' if i == 0 else "")
            elif signal == 'SKIPPED_SELL':
                plt.plot(i, prices[i], 'mo', label='SKIPPED_SELL' if i == 0 else "")
            elif signal == 'NONE':
                plt.plot(i, prices[i], 'ko', label='NONE' if i == 0 else "")

        plt.xlabel("Ітерація")
        plt.ylabel("Ціна")
        plt.title("📈 Графік ціни з торговими сигналами")
        plt.legend(loc='upper left')
        plt.grid(True)
        plt.tight_layout()

        buf = BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        plt.close()

        log_info("✅ Графік згенеровано як BytesIO")
        return buf

    except Exception as e:
        log_error(f"❌ Помилка при побудові графіку: {e}")
        return None


def generate_pnl_chart(pnl_history: list):
    """
    Генерує графік реалізованого PnL по угодах.

    Аргументи:
        pnl_history (list): Список записів з ключами 'pnl'

    Результат:
        BytesIO-об'єкт з PNG-графіком
    """
    try:
        if not pnl_history:
            log_error("❌ Немає даних для побудови PnL-графіка.")
            return None

        x = list(range(1, len(pnl_history) + 1))
        y = [record["pnl"] for record in pnl_history]

        plt.figure(figsize=(8, 4))
        plt.plot(x, y, marker='o', linestyle='-', color='green')
        plt.title("📈 Реалізований PnL")
        plt.xlabel("Угода")
        plt.ylabel("USDT")
        plt.grid(True)
        plt.tight_layout()

        buf = BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        plt.close()

        log_info("✅ PnL-графік згенеровано як BytesIO")
        return buf

    except Exception as e:
        log_error(f"❌ Помилка при побудові PnL-графіка: {e}")
        return None
