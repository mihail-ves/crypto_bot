import time
import pandas as pd
from binance_api import get_price
from strategy import should_buy, should_sell  # залишено для mock
from logger import log_info, log_error
from telegram_notifier import send_telegram_message
from analytics import atr, breakout, btc_eth_ratio
from order_logger import log_order_to_csv, log_trade_to_csv
from trade_config import load_config
from mock_trading import simulate_buy, simulate_sell, get_mock_balance
from core.binance_api import place_order
from core.trade_control import can_trade_now, update_trade_time
from core.state import MODE, trading_enabled
from core.portfolio_state import update_entry
from core.market_state import update_price

# === Глобальний стан ===
price_history = []
signal_history = []

# === Сигнал на основі RSI, ATR, Breakout ===
def detect_signal(prices: list) -> str:
    if len(prices) < 20:
        return "NO_SIGNAL"

    df = pd.DataFrame(prices, columns=["price"])
    df["returns"] = df["price"].pct_change()

    delta = df["price"].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(window=14).mean()
    avg_loss = loss.rolling(window=14).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    latest_rsi = rsi.iloc[-1]

    df["high"] = df["price"]
    df["low"] = df["price"]
    df["close"] = df["price"]
    df["tr"] = df["high"] - df["low"]
    atr_value = df["tr"].rolling(window=14).mean().iloc[-1]

    breakout_signal = df["price"].iloc[-1] > df["price"].rolling(window=20).max().iloc[-2]

    if breakout_signal and latest_rsi < 70:
        return "BUY"
    elif latest_rsi > 80:
        return "SELL"
    return "NO_SIGNAL"

# === Один торговий цикл ===
def run_trading_cycle():
    if not trading_enabled:
        return

    try:
        symbol, amount = load_config()
        price = get_price(symbol)
        if price is None:
            log_error(f"❌ Ціна недоступна для {symbol}")
            return

        update_price(symbol, price)
        price_history.append(price)
        log_info(f"📈 Поточна ціна {symbol}: {price}")

        if len(price_history) >= 6:
            btc_price = get_price("BTCUSDT")
            eth_price = get_price("ETHUSDT")

            if btc_price is None or eth_price is None:
                log_error("❌ Не вдалося отримати BTC або ETH для аналітики")
                return

            update_price("BTCUSDT", btc_price)
            update_price("ETHUSDT", eth_price)

            ratio = btc_eth_ratio(btc_price, eth_price)
            volatility = atr(price_history)
            is_breakout = breakout(price_history)
            log_info(f"📊 BTC/ETH: {ratio:.2f}, ATR: {volatility:.2f}, Breakout: {'Yes' if is_breakout else 'No'}")
        else:
            log_info("ℹ️ Недостатньо історії для аналітики")
            return

        signal = detect_signal(price_history)
        signal_history.append(signal)
        log_info(f"📡 Сигнал: {signal}")

        asset = symbol.replace("USDT", "")

        if signal == "BUY":
            usdt_balance = get_mock_balance("USDT") if MODE == "mock" else None
            cost = amount * price

            if MODE == "mock" and usdt_balance < cost:
                send_telegram_message(f"⚠️ Недостатньо USDT: потрібно {cost:.2f}, є {usdt_balance:.2f}")
                signal_history.append("SKIPPED_BUY")
                return

            if MODE == "live" and not can_trade_now():
                signal_history.append("SKIPPED_BUY")
                return

            if MODE == "mock":
                simulate_buy(symbol, amount)
                log_order_to_csv(symbol, "BUY", amount, {"id": "SIM_BUY"})
                log_trade_to_csv(symbol, "BUY", amount, price, "Simulated")
                send_telegram_message(f"✅ Simulated BUY {amount} {symbol} @ {price}")
            else:
                result = place_order(symbol, "BUY", amount)
                print(f"[INFO] Order result: {result}")
                log_order_to_csv(symbol, "BUY", amount, result)
                log_trade_to_csv(symbol, "BUY", amount, price, "Live")
                send_telegram_message(f"✅ Live BUY {amount} {symbol} @ {price}")
                update_trade_time()
                update_entry(asset, price, amount, "BUY")

        elif signal == "SELL":
            asset_balance = get_mock_balance(asset) if MODE == "mock" else None

            if MODE == "mock" and asset_balance < amount:
                send_telegram_message(f"⚠️ Недостатньо {asset}: потрібно {amount}, є {asset_balance:.4f}")
                signal_history.append("SKIPPED_SELL")
                return

            if MODE == "live" and not can_trade_now():
                signal_history.append("SKIPPED_SELL")
                return

            if MODE == "mock":
                simulate_sell(symbol, amount)
                log_order_to_csv(symbol, "SELL", amount, {"id": "SIM_SELL"})
                log_trade_to_csv(symbol, "SELL", amount, price, "Simulated")
                send_telegram_message(f"✅ Simulated SELL {amount} {symbol} @ {price}")
            else:
                result = place_order(symbol, "SELL", amount)
                print(f"[INFO] Order result: {result}")
                log_order_to_csv(symbol, "SELL", amount, result)
                log_trade_to_csv(symbol, "SELL", amount, price, "Live")
                send_telegram_message(f"✅ Live SELL {amount} {symbol} @ {price}")
                update_trade_time()
                update_entry(asset, price, amount, "SELL")

        else:
            log_info("⚪ No actionable signal")
            signal_history.append("NONE")

    except Exception as e:
        log_error(f"❌ Помилка в торговому циклі: {e}")
        send_telegram_message(f"❌ Error: {e}")
