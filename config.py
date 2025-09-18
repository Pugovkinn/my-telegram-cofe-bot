import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMINS = [int(os.getenv('ADMIN_CHAT_ID'))] if os.getenv('ADMIN_CHAT_ID') else []

# Настройки YooKassa (пока заглушки)
#YOOKASSA_SHOP_ID = os.getenv('YOOKASSA_SHOP_ID', 'test_shop_id')
#YOOKASSA_SECRET_KEY = os.getenv('YOOKASSA_SECRET_KEY', 'test_secret_key')
DEMO_MODE = True  # Флаг демо-режима

# Настройки БД
DB_PATH = 'data/database.db'