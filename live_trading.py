# live_trading.py
import time
from binance_api import get_price, get_balance, place_order
from strategy import should_buy, should_sell
from analytics import atr, breakout, btc_eth_ratio
from telegram_notifier import send_telegram_message
from order_logger import log_order_to_csv
from logger import log_info, log_error
from config.config_loader import CONFIG

# === Параметри з конфігурації ===
SYMBOL = CONFIG.get("SYMBOL", "BTCUSDT")
TRADE_AMOUNT = CONFIG.get("TRADE_AMOUNT", 0.01)
INTERVAL = CONFIG.get("INTERVAL", 30)  # секунд між циклами

# === Історія для аналітики ===
price_history = []
signal_history = []
trading_enabled = True

# === Основний торговий цикл ===
def trading_loop():
    """
    Запускає нескінченний цикл реальної торгівлі через Binance.

    Кожен цикл:
        - Отримує поточну ціну
        - Оновлює історію
        - Аналізує сигнал BUY/SELL
        - Виконує ордер
        - Логує результат
        - Надсилає повідомлення в Telegram
    """
    global price_history, signal_history

    log_info("📡 Запуск live_trading циклу...")
    send_telegram_message("📡 Live-трейдинг запущено.")

    while True:
        try:
            if not trading_enabled:
                time.sleep(INTERVAL)
                continue

            price = get_price(SYMBOL)
            if price is None:
                time.sleep(INTERVAL)
                continue

            price_history.append(price)
            if len(price_history) > 100:
                price_history = price_history[-100:]

            # === Визначення сигналу ===
            if should_buy(price_history):
                signal = "BUY"
                result = place_order(SYMBOL, "BUY", TRADE_AMOUNT)
            elif should_sell(price_history):
                signal = "SELL"
                result = place_order(SYMBOL, "SELL", TRADE_AMOUNT)
            else:
                signal = "NONE"
                result = None

            signal_history.append(signal)
            if len(signal_history) > 100:
                signal_history = signal_history[-100:]

            # === Логування та повідомлення ===
            if result:
                log_order_to_csv(SYMBOL, signal, TRADE_AMOUNT, result)
                send_telegram_message(f"📈 {signal} {TRADE_AMOUNT} {SYMBOL} @ {result.get('price', 'N/A')}")
            else:
                log_info(f"⏸ Без сигналу: {price}")

            # === Аналітика (опційно)
            if len(price_history) >= 6:
                atr_val = atr(price_history)
                breakout_val = breakout(price_history)
                ratio_val = btc_eth_ratio(get_price("BTCUSDT"), get_price("ETHUSDT"))
                log_info(f"📊 ATR: {atr_val:.2f}, Breakout: {breakout_val}, BTC/ETH: {ratio_val:.2f}")

            time.sleep(INTERVAL)

        except Exception as e:
            log_error(f"❌ Помилка в live_trading: {e}")
            send_telegram_message(f"❌ Live-трейдинг аварійно завершився: {e}")
            time.sleep(60)
