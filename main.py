# main.py
from trader import run_trading_cycle
import time

while True:
    run_trading_cycle()
    time.sleep(60)  # кожну хвилину

