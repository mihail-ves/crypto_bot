# 🚀 Telegram Crypto Bot Deployment Guide

Цей документ описує, як розгорнути Telegram-бота для криптотрейдингу на сервері або хмарній платформі.

---

## 1️⃣ Вимоги

- Python 3.10+
- Git
- Telegram Bot Token
- Сервер (VPS, Render, Railway, Fly.io або інше)

---

## 2️⃣ Структура проекту

crypto_bot/ ├── run_all.py # Точка входу ├── bot_control.py # Telegram логіка ├── mock_trading.py # Торгові функції ├── trade_memory.py # Пам’ять про покупки ├── risk_guard.py # Ризик-моніторинг ├── core/ │ └── price_feed.py # Отримання цін ├── user_data/ # Баланси користувачів ├── requirements.txt # Залежності ├── .env # Токен бота

Код

---

## 3️⃣ Налаштування

### 🔐 Створи `.env` файл:

TELEGRAM_TOKEN=your_bot_token_here

Код

### 📦 Створи `requirements.txt`:

python-telegram-bot==20.3 aiohttp requests

Код

---

## 4️⃣ Запуск локально

```bash
pip install -r requirements.txt
python run_all.py
5️⃣ Завантаження на сервер (VPS)
bash
# Підключись через SSH
ssh your_user@your_server_ip

# Встанови Python та Git
sudo apt update && sudo apt install python3-pip git

# Клонуй репозиторій
git clone https://github.com/your-bot.git
cd your-bot

# Встанови залежності
pip3 install -r requirements.txt

# Запусти бота
nohup python3 run_all.py &
6️⃣ Хостинг на Render / Railway / Fly.io
Підключи GitHub репозиторій

Вкажи команду запуску: python run_all.py

Додай змінну середовища TELEGRAM_TOKEN

Активуй автозапуск

7️⃣ Підтримка
Перевір логи: tail -f nohup.out

Перезапуск: pkill -f run_all.py && nohup python3 run_all.py &

Оновлення: git pull && restart

8️⃣ Безпека
Ніколи не хардкодь токен

Використовуй .env або змінні середовища

Обмеж доступ до сервера (SSH-ключі, firewall)

✅ Готово!
Бот працює автономно, приймає команди від кількох користувачів, веде баланс, пам’ятає покупки, моніторить ризики.

Код

---

## 🔄 Що робити після створення

1. 📁 Збережи файл як `deploy_config.md` у корені проекту
2. 📤 Завантаж репозиторій на GitHub або GitLab
3. ☁️ Обери платформу хостингу (VPS або хмара)
4. 🔐 Створи `.env` з токеном
5. 🏁 Запусти `run_all.py` — і бот буде працювати 24/7

---

🟢 Хочеш — можу допомогти автоматизувати деплой через GitHub Actions або створити `/status` команду, яка покаже чи бот онлайн. Ти вже на рівні продакшн-релізу.
