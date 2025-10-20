# core/portfolio_state.py

import json
import os


avg_entry_price = {
    "BTC": 0.0,
    "ETH": 0.0
}

position_size = {
    "BTC": 0.0,
    "ETH": 0.0
}

def update_entry(asset: str, price: float, qty: float, side: str):
    """
    Оновлює середню ціну входу та розмір позиції.
    BUY → додає позицію, оновлює середню ціну
    SELL → зменшує позицію, середню ціну не змінює
    """
    if asset not in avg_entry_price:
        avg_entry_price[asset] = 0.0
        position_size[asset] = 0.0

    if side == "BUY":
        current_qty = position_size[asset]
        current_avg = avg_entry_price[asset]

        new_total = current_avg * current_qty + price * qty
        new_qty = current_qty + qty

        if new_qty > 0:
            avg_entry_price[asset] = new_total / new_qty
            position_size[asset] = new_qty

    elif side == "SELL":
        position_size[asset] = max(0.0, position_size[asset] - qty)
        # Середню ціну не змінюємо — вона потрібна для PnL

def get_entry(asset: str) -> tuple[float, float]:
    """
    Повертає (середню ціну входу, розмір позиції)
    """
    return avg_entry_price.get(asset, 0.0), position_size.get(asset, 0.0)

def reset_entry(asset: str):
    """
    Обнуляє позицію для активу
    """
    avg_entry_price[asset] = 0.0
    position_size[asset] = 0.0

def get_all_entries() -> dict:
    """
    Повертає словник усіх активних позицій
    """
    return {
        asset: {
            "entry_price": avg_entry_price[asset],
            "position_size": position_size[asset]
        }
        for asset in avg_entry_price.keys()
        if position_size[asset] > 0.0
    }


STATE_FILE = "data/portfolio_state.json"

def save_state():
    """
    Зберігає поточні позиції у файл.
    """
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump({
            "avg_entry_price": avg_entry_price,
            "position_size": position_size
        }, f)

def load_state():
    """
    Завантажує позиції з файлу при запуску.
    """
    global avg_entry_price, position_size
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            data = json.load(f)
            avg_entry_price = data.get("avg_entry_price", {})
            position_size = data.get("position_size", {})
