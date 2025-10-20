# logger.py
import logging

# === Налаштування логера ===
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("bot.log", encoding="utf-8"),  # Запис у файл
        logging.StreamHandler()                            # Вивід у консоль
    ]
)

# === Інформаційне повідомлення ===
def log_info(message):
    """
    Логує інформаційне повідомлення (INFO).

    Аргументи:
        message (str): Текст повідомлення.
    """
    logging.info(message)

# === Повідомлення про помилку ===
def log_error(message):
    """
    Логує повідомлення про помилку (ERROR).

    Аргументи:
        message (str): Текст повідомлення.
    """
    logging.error(message)

# === Попередження ===
def log_warning(message):
    """
    Логує попередження (WARNING).

    Аргументи:
        message (str): Текст повідомлення.
    """
    logging.warning(message)
