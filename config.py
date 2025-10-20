# config.py
import json

with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

API_KEY = config["API_KEY"]
API_SECRET = config["API_SECRET"]
SYMBOL = config["SYMBOL"]
TRADE_AMOUNT = config["TRADE_AMOUNT"]
LOSS_LIMIT = config["LOSS_LIMIT"]
MODE = config["MODE"]

BASE_URL = 'https://testnet.binance.vision'  # Testnet для спотової торгівлі
SYMBOL = 'BTCUSDT'
TRADE_AMOUNT = 0.001

TELEGRAM_TOKEN = '8440251961:AAG3SM_iUWj6rsrsti5IG06yX2syLah2BLs'
CHAT_ID = '1394001618'

