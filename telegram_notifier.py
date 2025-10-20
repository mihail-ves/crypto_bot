# telegram_notifier.py
import requests
from logger import log_error, log_info
from config.config_loader import CONFIG  # Централізоване джерело конфігурації

TELEGRAM_TOKEN = CONFIG.get("BOT_TOKEN", "")
CHAT_ID = CONFIG.get("CHAT_ID", "")

# === Надсилання текстового повідомлення ===
def send_telegram_message(message):
    """
    Надсилає текстове повідомлення в Telegram-чат.

    Аргументи:
        message (str): Текст повідомлення.
    """
    if not TELEGRAM_TOKEN or not CHAT_ID:
        log_error("❌ Telegram токен або chat_id не задано")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        'chat_id': CHAT_ID,
        'text': message,
        'parse_mode': 'HTML'
    }
    try:
        response = requests.post(url, data=payload)
        if response.status_code != 200:
            log_error(f"Telegram message error: {response.text}")
        else:
            log_info(f"📨 Надіслано повідомлення: {message}")
    except Exception as e:
        log_error(f"Telegram exception: {e}")

# === Надсилання зображення ===
def send_telegram_image(image_path, caption=""):
    """
    Надсилає зображення в Telegram-чат з опціональним підписом.

    Аргументи:
        image_path (str): Шлях до файлу зображення.
        caption (str): Підпис до фото.
    """
    if not TELEGRAM_TOKEN or not CHAT_ID:
        log_error("❌ Telegram токен або chat_id не задано")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"
    try:
        with open(image_path, 'rb') as img:
            payload = {
                'chat_id': CHAT_ID,
                'caption': caption
            }
            files = {'photo': img}
            response = requests.post(url, data=payload, files=files)
            if response.status_code != 200:
                log_error(f"Telegram image error: {response.text}")
            else:
                log_info(f"🖼 Надіслано зображення: {image_path} з підписом: {caption}")
    except Exception as e:
        log_error(f"Telegram image exception: {e}")
