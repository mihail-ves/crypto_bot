# run_all.py
import threading
import time
from bot_control import build_bot
from trader import run_trading_cycle
from telegram_notifier import send_telegram_message
from logger import log_info, log_error

# === Торговий цикл у окремому потоці ===
def trading_loop():
    """
    Запускає нескінченний торговий цикл у фоновому потоці.
    """
    while True:
        try:
            run_trading_cycle()
            time.sleep(30)  # або CONFIG.get("INTERVAL", 30)
        except Exception as e:
            log_error(f"❌ Помилка в trading_loop: {e}")
            send_telegram_message(f"❌ Торговий цикл аварійно завершився: {e}")
            time.sleep(60)

# === Головна точка запуску ===
def main():
    """
    Запускає Telegram-бота та торговий цикл паралельно.
    """
    try:
        log_info("🚀 Запуск торгового бота...")
        send_telegram_message("🤖 Бот запущено. Очікуємо сигнали...")

        # Запуск торгового циклу у фоновому потоці
        thread = threading.Thread(target=trading_loop, daemon=True)
        thread.start()

        # Запуск Telegram-бота (блокує головний потік)
        bot_app = build_bot()
        bot_app.run_polling()

    except Exception as e:
        log_error(f"❌ Помилка при запуску: {e}")
        send_telegram_message(f"❌ Бот аварійно завершив роботу: {e}")

# === Запуск ===
if __name__ == "__main__":
    main()
