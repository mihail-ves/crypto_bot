# core/binance_api.py
import requests
import time
import hmac
import hashlib
from config.config_loader import CONFIG

API_KEY = CONFIG["API_KEY"]
API_SECRET = CONFIG["API_SECRET"]
BASE_URL = "https://api.binance.com"

def sign(params: dict) -> dict:
    query_string = "&".join([f"{k}={v}" for k, v in params.items()])
    signature = hmac.new(API_SECRET.encode(), query_string.encode(), hashlib.sha256).hexdigest()
    params["signature"] = signature
    return params

def get_headers():
    return {
        "X-MBX-APIKEY": API_KEY
    }

def place_order(symbol: str, side: str, quantity: float) -> dict:
    """
    Створює ринковий ордер BUY або SELL.
    """
    url = f"{BASE_URL}/api/v3/order"
    timestamp = int(time.time() * 1000)
    params = {
        "symbol": symbol,
        "side": side,
        "type": "MARKET",
        "quantity": quantity,
        "timestamp": timestamp
    }
    signed_params = sign(params)
    try:
        response = requests.post(url, headers=get_headers(), params=signed_params)
        data = response.json()
        print(f"[BINANCE] Ордер виконано: {data}")
        return data
    except Exception as e:
        print(f"[BINANCE] Помилка ордера: {e}")
        return {}

def get_balance(asset: str = "USDT") -> float:
    """
    Повертає баланс вказаного активу.
    """
    url = f"{BASE_URL}/api/v3/account"
    timestamp = int(time.time() * 1000)
    params = {
        "timestamp": timestamp
    }
    signed_params = sign(params)
    try:
        response = requests.get(url, headers=get_headers(), params=signed_params)
        data = response.json()
        for balance in data["balances"]:
            if balance["asset"] == asset:
                return float(balance["free"])
        return 0.0
    except Exception as e:
        print(f"[BINANCE] Помилка балансу: {e}")
        return 0.0
