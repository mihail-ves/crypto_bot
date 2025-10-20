import csv
import os
from datetime import datetime
from logger import log_info, log_error

LOG_FILE = "trade_log.csv"
ORDER_LOG_FILE = "orders.csv"

# === Ініціалізація trade_log.csv ===
if not os.path.exists(LOG_FILE):
    try:
        with open(LOG_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["timestamp", "symbol", "side", "amount", "price", "note"])
        log_info("📁 Створено trade_log.csv з заголовками")
    except Exception as e:
        log_error(f"❌ Помилка при створенні trade_log.csv: {e}")

# === Запис ордера в orders.csv ===
def log_order_to_csv(symbol, side, quantity, result):
    """
    Логує торговий ордер у файл orders.csv.
    result — словник з інформацією про ордер, очікується ключ 'id'.
    """
    try:
        with open(ORDER_LOG_FILE, mode="a", newline='', encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow([
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                symbol,
                side,
                f"{quantity:.4f}",
                result.get('id', 'N/A')
            ])
        log_info(f"🧾 Ордер записано: {side} {quantity} {symbol}")
    except Exception as e:
        log_error(f"❌ Помилка при записі ордера: {e}")

# === Запис торгової дії в trade_log.csv ===
def log_trade_to_csv(symbol, side, amount, price, note):
    """
    Записує торгову дію в trade_log.csv з ціною.
    """
    try:
        with open(LOG_FILE, mode="a", newline='', encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow([
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                symbol,
                side,
                f"{amount:.4f}",
                f"{price:.2f}",
                note
            ])
        log_info(f"📘 Запис у журнал: {side} {amount} {symbol} @ {price} — {note}")
    except Exception as e:
        log_error(f"❌ Помилка при записі в журнал: {e}")

# === Читання останніх записів з trade_log.csv ===
def read_last_log_entries(n=10):
    """
    Повертає останні n записів з trade_log.csv у вигляді списку рядків.
    """
    if not os.path.exists(LOG_FILE):
        log_info("ℹ️ Журнал ще не створено")
        return []

    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()

        if len(lines) <= 1:
            log_info("ℹ️ Журнал порожній")
            return []

        entries = lines[1:]  # пропускаємо заголовок
        return entries[-n:]

    except Exception as e:
        log_error(f"❌ Помилка при читанні журналу: {e}")
        return []
