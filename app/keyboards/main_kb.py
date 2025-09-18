from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_main_keyboard():
    kb = [
        [KeyboardButton(text="☕ Меню")],
        [KeyboardButton(text="🛒 Корзина"), KeyboardButton(text="📦 Мои заказы")],
        [KeyboardButton(text="📞 Контакты"), KeyboardButton(text="ℹ️ О нас")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)