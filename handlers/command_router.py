# handlers/command_router.py
from telegram.ext import CommandHandler
from handlers.bot_control import (
    start,
    stop,
    status_command,
    chart,
    analytics,
    signal,
    log,
    config,
    reset,
    help_command,
    balance,
    fund,
    portfolio,
    summary,
    simulate_buy,
    orders,
    simulate_sell_command,
    confirm_live_command,
    simulate_buy_command,
    toggle_auto_command,
    auto_status_command,
    signal_summary_command
)

def register_commands(app):
    app.add_handler(CommandHandler("toggle_auto", toggle_auto_command))
    app.add_handler(CommandHandler("auto_status", auto_status_command))
    app.add_handler(CommandHandler("signal_summary", signal_summary_command))

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stop", stop))
    app.add_handler(CommandHandler("status", status_command))
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
    app.add_handler(CommandHandler("orders", orders))
    app.add_handler(CommandHandler("simulate_sell", simulate_sell_command))
    app.add_handler(CommandHandler("confirm_live", confirm_live_command))
