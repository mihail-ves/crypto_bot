import json, os
from logger import log_info, log_error
from core.price_feed import get_price  # ← без циклічного імпорту

DATA_DIR = "user_data"

# === Шлях до балансу користувача ===
def get_balance_path(user_id):
    os.makedirs(DATA_DIR, exist_ok=True)
    return os.path.join(DATA_DIR, f"{user_id}_balance.json")

# === Оновлення балансу ===
def update_mock_balance(user_id, asset, amount):
    path = get_balance_path(user_id)
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except:
        data = {}

    data[asset] = data.get(asset, 0.0) + amount

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    log_info(f"💰 [{user_id}] Баланс оновлено: {asset} {'+' if amount >= 0 else ''}{amount:.4f}")

# === Отримання балансу ===
def get_mock_balance(user_id, asset):
    path = get_balance_path(user_id)
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get(asset, 0.0)
    except:
        return 0.0

# === Симуляція покупки ===
def simulate_buy(user_id, symbol, amount):
    if not symbol.endswith("USDT"):
        log_error(f"❌ [{user_id}] Неправильний формат символу: {symbol}")
        return

    asset = symbol.replace("USDT", "")
    price = get_price(symbol)
    if price is None:
        log_error(f"❌ [{user_id}] Ціна недоступна для {symbol}")
        return

    cost = amount * price
    usdt_balance = get_mock_balance(user_id, "USDT")
    if usdt_balance < cost:
        log_error(f"❌ [{user_id}] Недостатньо USDT для покупки {amount} {asset}. Потрібно {cost:.2f}, є {usdt_balance:.2f}")
        return

    update_mock_balance(user_id, asset, amount)
    update_mock_balance(user_id, "USDT", -cost)
    log_info(f"🟢 [{user_id}] Симульовано покупку: {amount:.4f} {asset} @ {price:.4f}, списано {cost:.2f} USDT")

# === Симуляція продажу ===
def simulate_sell(user_id, symbol, amount):
    if not symbol.endswith("USDT"):
        log_error(f"❌ [{user_id}] Неправильний формат символу: {symbol}")
        return False, "Неправильний формат символу"

    asset = symbol.replace("USDT", "")
    price = get_price(symbol)
    if price is None:
        log_error(f"❌ [{user_id}] Ціна недоступна для {symbol}")
        return False, "Ціна недоступна"

    path = get_balance_path(user_id)
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except:
        data = {}

    current = data.get(asset, 0.0)
    if current < amount:
        log_error(f"❌ [{user_id}] Недостатньо {asset} для продажу. Є лише {current:.4f}")
        return False, f"Недостатньо {asset} для продажу. Є лише {current:.4f}"

    data[asset] = current - amount
    revenue = amount * price
    data["USDT"] = data.get("USDT", 0.0) + revenue

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    log_info(f"🔻 [{user_id}] Симульовано продаж: {amount:.4f} {asset} @ {price:.4f}, отримано {revenue:.2f} USDT")
    return True, f"🔻 Симульовано продаж: {amount:.4f} {asset} @ {price:.4f}"
