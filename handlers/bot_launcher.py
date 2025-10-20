# handlers/bot_launcher.py
# bot_launcher.py альтернатива build_bot()
from telegram.ext import ApplicationBuilder
from bot_control import build_bot

if __name__ == "__main__":
    app = build_bot()
    app.run_polling()
