print("🧭 Запущено bot_control з головної папки")
import json, time
from telegram import Update, InputFile
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from logger import log_info, log_error
from config.config_loader import CONFIG
from chart_generator import generate_chart, generate_pnl_chart
from telegram_notifier import send_telegram_image
from analytics import atr, breakout, btc_eth_ratio
import trader
from mock_trading import update_mock_balance, get_mock_balance, simulate_buy, simulate_sell
from trade_config import load_config, save_config, current_symbol, current_amount, update_symbol
from order_logger import read_last_log_entries
from trader import price_history, signal_history
from core.state import MODE, trading_enabled
import core.state as state
from core.portfolio_state import (
    avg_entry_price, position_size,
    update_entry, get_entry, get_all_entries,
    load_state, save_state
)
from core.market_api import get_price
from core.pnl_storage import save_pnl_history, load_pnl_history
import matplotlib.pyplot as plt
from io import BytesIO
from mock_trading import simulate_buy, simulate_sell
from trade_memory import record_buy, is_profitable_sell
from risk_guard import track_asset, evaluate_risk
from core.price_feed import get_price


CONFIG_PATH = "config.json"
BALANCE_FILE = "mock_balance.json"
ORDERS_FILE = "mock_orders.json"

load_state()
state.MODE = "live"
state.trading_enabled = False

# === Глобальна історія PnL ===
pnl_history = load_pnl_history()

# === Запис ордера ===
def record_order(order_type: str, asset: str, amount: float, price: float):
    try:
        with open(ORDERS_FILE, "r", encoding="utf-8") as f:
            orders = json.load(f)
    except:
        orders = []

    orders.append({
        "type": order_type,
        "symbol": asset + "USDT",
        "asset": asset,
        "amount": amount,
        "price": price,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    })

    with open(ORDERS_FILE, "w", encoding="utf-8") as f:
        json.dump(orders, f, indent=2)

# === Команди: баланс і зарахування ===
async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    asset = context.args[0].upper() if context.args else "USDT"
    amount = get_mock_balance(asset)
    await update.message.reply_text(f"💰 Баланс {asset}: {amount}")

async def fund(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        asset = context.args[0].upper() if len(context.args) >= 1 else "USDT"
        amount = float(context.args[1]) if len(context.args) >= 2 else 1000
        update_mock_balance(asset, amount)
        await update.message.reply_text(f"💧 Імітовано зарахування: {amount} {asset}")
    except Exception as e:
        await update.message.reply_text(f"❌ Помилка при зарахуванні: {e}")



# === Команди: симуляція BUY/SELL ===



async def simulate_buy_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = str(update.effective_user.id)
        asset = context.args[0].upper()
        amount = float(context.args[1])
        symbol = asset + "USDT"
        price = get_price(symbol)

        track_asset(symbol)  # 🛡 Активуємо моніторинг ризику

        if price is None:
            await update.message.reply_text(f"❌ Ціна недоступна для {symbol}")
            return

        simulate_buy(user_id, symbol, amount)
        record_buy(symbol, price)

        await update.message.reply_text(f"🟢 [{user_id}] Симульовано покупку: {amount} {asset} @ {price:.4f}")
    except Exception as e:
        await update.message.reply_text(f"❌ Помилка при симуляції покупки: {e}")


async def simulate_sell_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = str(update.effective_user.id)
        asset = context.args[0].upper()
        amount = float(context.args[1])
        symbol = asset + "USDT"
        price = get_price(symbol)

        if price is None:
            await update.message.reply_text(f"❌ Ціна недоступна для {symbol}")
            return

        # 🛡 Перевірка ризику
        trigger, reason = evaluate_risk(symbol)
        if trigger:
            await update.message.reply_text(f"⚠️ Ризик-триггер: {reason}\nРекомендується продати {symbol}")

        # 🧠 Перевірка прибутковості
        if not is_profitable_sell(symbol, price, min_margin=0.002):
            await update.message.reply_text(f"⛔ Продаж не вигідний: {price:.4f}")
            return

        success, message = simulate_sell(user_id, symbol, amount)
        await update.message.reply_text(message)
    except Exception as e:
        await update.message.reply_text(f"❌ Помилка при симуляції продажу: {e}")


# === Команди: ордери і портфель ===
async def orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        with open(ORDERS_FILE, "r", encoding="utf-8") as f:
            orders = json.load(f)
        if not orders:
            await update.message.reply_text("📭 Ордерів поки немає.")
            return

        last_orders = orders[-5:]
        message = "📜 Останні ордери:\n" + "\n".join(
            [f"{o['timestamp']}: {o['price']:.2f} {o['type']} {o['amount']} {o['asset']}" for o in last_orders]
        )
        await update.message.reply_text(message)
    except Exception as e:
        await update.message.reply_text(f"❌ Помилка при запиті ордерів: {e}")

async def portfolio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        with open(BALANCE_FILE, "r", encoding="utf-8") as f:
            balances = json.load(f)

        non_zero_assets = [
            f"{asset}: {amount}" for asset, amount in balances.items()
            if float(amount) > 0
        ]

        if not non_zero_assets:
            await update.message.reply_text("📭 Портфель порожній.")
        else:
            message = "💼 Портфель:\n" + "\n".join(non_zero_assets)
            await update.message.reply_text(message)
    except Exception as e:
        await update.message.reply_text(f"❌ Помилка при запиті портфеля: {e}")

async def summary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        with open(BALANCE_FILE, "r", encoding="utf-8") as f:
            balances = json.load(f)

        prices = {
            "USDT": 1.0,
            "BTC": get_price("BTCUSDT"),
            "ETH": get_price("ETHUSDT"),
            "JUP": get_price("JUPUSDT")
        }

        for asset in ["BTC", "ETH"]:
            if prices[asset] is None:
                await update.message.reply_text(f"❌ Не вдалося отримати ціну для {asset}")
                return

        total_usdt = 0.0
        lines = []

        for asset, amount in balances.items():
            price = prices.get(asset, 0)
            value = amount * price
            total_usdt += value
            lines.append(f"{asset}: {amount:.4f} × {price:.2f} = {value:.2f} USDT")

        message = (
            "📊 Портфель:\n" +
            "\n".join(lines) +
            f"\n\n💰 Загальна вартість: {total_usdt:.2f} USDT"
        )
        await update.message.reply_text(message)

    except Exception as e:
        await update.message.reply_text(f"❌ Помилка при підрахунку портфеля: {e}")

# === Торгові команди ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    trader.trading_enabled = True
    await update.message.reply_text("✅ Торгівля активована.")

async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    trader.trading_enabled = False
    await update.message.reply_text("⛔ Торгівля зупинена.")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    state_text = "активна" if trader.trading_enabled else "вимкнена"
    await update.message.reply_text(f"📊 Торгівля зараз: {state_text}")

# === Аналітика та графік ===
async def chart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if not args:
        await update.message.reply_text("❗ Вкажіть символ: /chart BTCUSDT")
        return

    symbol = args[0].upper()
    history = trader.price_history

    if not history or len(history) < 2:
        await update.message.reply_text(f"ℹ️ Недостатньо даних для {symbol}")
        return

    try:
        image = generate_chart(history, symbol)
        await update.message.reply_photo(photo=image)
    except Exception as e:
        await update.message.reply_text(f"❌ Помилка при побудові графіку: {e}")

async def analytics(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        btc = trader.get_price("BTCUSDT")
        eth = trader.get_price("ETHUSDT")
        message = (
            f"📊 ATR: {atr(trader.price_history):.2f}\n"
            f"📈 Breakout: {breakout(trader.price_history)}\n"
            f"🔗 BTC/ETH Ratio: {btc_eth_ratio(btc, eth):.2f}"
        )
        await update.message.reply_text(message)
    except Exception as e:
        await update.message.reply_text(f"❌ Помилка аналітики: {e}")

async def signal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if trader.signal_history:
        await update.message.reply_text(f"📍 Останній сигнал: {trader.signal_history[-1]}")
    else:
        await update.message.reply_text("ℹ️ Сигналів поки немає.")

async def log(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        entries = read_last_log_entries(10)

        if not entries:
            await update.message.reply_text("ℹ️ Журнал порожній або ще не створено.")
            return

        response = "🧾 Останні записи:\n"
        for line in entries:
            timestamp, symbol, side, amount, note = line.strip().split(",")
            response += f"{timestamp}: {side} {amount} {symbol} — {note}\n"

        await update.message.reply_text(response)

    except Exception as e:
        await update.message.reply_text(f"❌ Помилка при читанні журналу: {e}")
# === Конфігурація ===
async def config(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"⚙️ Актив: {current_symbol}\nОбсяг: {current_amount}")

async def set(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        key = context.args[0].upper()
        value = context.args[1]

        if key == "SYMBOL":
            update_symbol(value.upper())
            price_history.clear()
            signal_history.clear()
            await update.message.reply_text(f"✅ SYMBOL оновлено: {value.upper()}")

        elif key == "AMOUNT":
            from trade_config import current_symbol
            amount = float(value)
            save_config(current_symbol, amount)
            await update.message.reply_text(f"✅ AMOUNT оновлено: {amount}")

        else:
            await update.message.reply_text("❌ Невідомий параметр. Використовуйте SYMBOL або AMOUNT.")
    except Exception as e:
        await update.message.reply_text(f"❌ Помилка при оновленні конфігурації: {e}")

async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    save_config("BTCUSDT", 0.01)
    await update.message.reply_text("🔄 Конфігурацію скинуто до стандартної.")

async def mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global MODE
    args = context.args
    if args:
        new_mode = args[0].lower()
        if new_mode in ["mock", "live"]:
            MODE = new_mode
            await update.message.reply_text(f"🔄 Режим змінено на: {MODE.upper()}")
        else:
            await update.message.reply_text("⚠️ Невідомий режим. Використовуйте /mode mock або /mode live")
    else:
        await update.message.reply_text(f"⚙️ Поточний режим: {MODE.upper()}")

# === Автоторгівля ===
async def auto_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    price = price_history[-1] if price_history else "Немає даних"
    signal = signal_history[-1] if signal_history else "Немає сигналу"
    history_len = len(price_history)

    usdt = get_mock_balance("USDT")
    eth = get_mock_balance("ETH")
    btc = get_mock_balance("BTC")

    btc_price = get_price("BTCUSDT")
    eth_price = get_price("ETHUSDT")

    usdt_value = usdt
    eth_value = eth * eth_price
    btc_value = btc * btc_price
    total_value = usdt_value + eth_value + btc_value

    text = (
        f"⚙️ Режим: {state.MODE.upper()}\n"
        f"📈 Поточна ціна: {price}\n"
        f"📡 Останній сигнал: {signal}\n"
        f"📊 Довжина історії: {history_len}\n\n"
        f"💼 Портфель:\n"
        f"USDT: {usdt:.2f} × 1.0 = {usdt_value:.2f} USDT\n"
        f"ETH: {eth:.4f} × {eth_price:.2f} = {eth_value:.2f} USDT\n"
        f"BTC: {btc:.4f} × {btc_price:.2f} = {btc_value:.2f} USDT\n"
        f"\n🔢 Загальна вартість: {total_value:.2f} USDT"
    )
    await update.message.reply_text(text)

async def auto_toggle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global trading_enabled
    args = context.args
    if args:
        cmd = args[0].lower()
        if cmd == "on":
            trading_enabled = True
            await update.message.reply_text("✅ Автоторгівля УВІМКНЕНА")
        elif cmd == "off":
            trading_enabled = False
            await update.message.reply_text("⛔ Автоторгівля ВИМКНЕНА")
        else:
            await update.message.reply_text("⚠️ Використовуйте /auto_toggle on або /auto_toggle off")
    else:
        status = "УВІМКНЕНА" if trading_enabled else "ВИМКНЕНА"
        await update.message.reply_text(f"⚙️ Автоторгівля зараз: {status}")
# === PnL та позиції ===
async def pnl(update: Update, context: ContextTypes.DEFAULT_TYPE):
    btc_price = get_price("BTCUSDT")
    eth_price = get_price("ETHUSDT")

    btc_pnl = (btc_price - avg_entry_price["BTC"]) * position_size["BTC"]
    eth_pnl = (eth_price - avg_entry_price["ETH"]) * position_size["ETH"]

    text = (
        f"📊 Нереалізований PnL:\n"
        f"BTC: {position_size['BTC']:.4f} @ {avg_entry_price['BTC']:.2f} → {btc_price:.2f}\n"
        f"➡️ PnL: {btc_pnl:.2f} USDT\n\n"
        f"ETH: {position_size['ETH']:.4f} @ {avg_entry_price['ETH']:.2f} → {eth_price:.2f}\n"
        f"➡️ PnL: {eth_pnl:.2f} USDT"
    )
    await update.message.reply_text(text)

async def entry_status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    entries = get_all_entries()
    if not entries:
        await update.message.reply_text("ℹ️ Немає відкритих позицій.")
        return

    lines = ["📊 Активні позиції:"]
    for asset, data in entries.items():
        lines.append(f"{asset}: {data['position_size']:.4f} @ {data['entry_price']:.2f}")
    await update.message.reply_text("\n".join(lines))

async def pnl_history_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not pnl_history:
        await update.message.reply_text("ℹ️ Історія PnL порожня.")
        return

    lines = ["📈 Історія реалізованого PnL:"]
    for i, record in enumerate(pnl_history[-10:], 1):
        lines.append(f"{i}. {record['asset']} {record['amount']} @ {record['entry']:.2f} → {record['exit']:.2f} = {record['pnl']:.2f} USDT")
    await update.message.reply_text("\n".join(lines))

async def pnl_chart_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chart = generate_pnl_chart(pnl_history)
    if chart is None:
        await update.message.reply_text("ℹ️ Історія PnL порожня.")
        return

    await update.message.reply_photo(photo=InputFile(chart), caption="📊 Графік реалізованого PnL")

# === Help ===
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📘 Доступні команди:\n"
        "/start — активувати торгівлю\n"
        "/stop — призупинити торгівлю\n"
        "/status — переглянути стан\n"
        "/chart — отримати графік монети прик JUPUSDT\n"
        "/analytics — переглянути аналітику\n"
        "/signal — останній торговий сигнал\n"
        "/log — останні 10 рядків з журналу\n"
        "/config — переглянути конфігурацію\n"
        "/set SYMBOL BTCUSDT — змінити актив\n"
        "/set AMOUNT 0.01 — змінити обсяг\n"
        "/reset — скинути конфігурацію\n"
        "/balance USDT — перевірити баланс\n"
        "/fund USDT 1000 — зарахувати тестові кошти\n"
        "/portfolio — показати всі активи\n"
        "/summary — загальна вартість портфеля\n"
        "/simulate_buy BTCUSDT 0.01 — симулювати покупку\n"
        "/simulate_sell BTCUSDT 0.01 — симулювати продаж\n"
        "/orders — показати останні ордери\n"
        "/mode mock → повертає в симуляцію\n"
        "/mode live → перемикає на реальну торгівлю\n"
        "/auto_status — стан автоторгівлі\n"
        "/auto_toggle — показує статус\n"
        "/auto_toggle on — вмикає автоторгівлю\n"
        "/auto_toggle off — вимикає\n"
        "/pnl — покаже наскільки бот в плюсах\n"
        "/entry_status — показує всі відкриті позиції\n"
        "/pnl_history — історія реалізованого PnL\n"
        "/pnl_chart — графік\n"
        "/help — список команд"
    )

# === Побудова Telegram-бота ===
def build_bot():
    app = ApplicationBuilder().token(CONFIG.get("BOT_TOKEN", "")).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stop", stop))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("chart", chart))
    app.add_handler(CommandHandler("analytics", analytics))
    app.add_handler(CommandHandler("signal", signal))
    app.add_handler(CommandHandler("log", log))
    app.add_handler(CommandHandler("config", config))
    app.add_handler(CommandHandler("set", set))
    app.add_handler(CommandHandler("reset", reset))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("balance", balance))
    app.add_handler(CommandHandler("fund", fund))
    app.add_handler(CommandHandler("portfolio", portfolio))
    app.add_handler(CommandHandler("summary", summary))
    app.add_handler(CommandHandler("simulate_buy", simulate_buy_command))
    app.add_handler(CommandHandler("simulate_sell", simulate_sell_command))
    app.add_handler(CommandHandler("orders", orders))
    app.add_handler(CommandHandler("mode", mode))
    app.add_handler(CommandHandler("auto_status", auto_status))
    app.add_handler(CommandHandler("auto_toggle", auto_toggle))
    app.add_handler(CommandHandler("pnl", pnl))
    app.add_handler(CommandHandler("entry_status", entry_status_command))
    app.add_handler(CommandHandler("pnl_history", pnl_history_command))
    app.add_handler(CommandHandler("pnl_chart", pnl_chart_command))

    return app
