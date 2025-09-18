from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from app.models.database import get_db_session, Category, Item

def get_categories_kb():
    session = get_db_session()
    try:
        categories = session.query(Category).all()
        buttons = []
        for cat in categories:
            buttons.append([InlineKeyboardButton(text=cat.name, callback_data=f"category_{cat.id}")])
        return InlineKeyboardMarkup(inline_keyboard=buttons)
    finally:
        session.close()

def get_items_kb(category_id):
    session = get_db_session()
    try:
        items = session.query(Item).filter(Item.category_id == category_id).all()
        buttons = []
        for item in items:
            buttons.append([InlineKeyboardButton(text=f"{item.name} - {int(item.price)}₽", callback_data=f"item_{item.id}")])
        buttons.append([InlineKeyboardButton(text="↩️ Назад", callback_data="back_to_categories")])
        return InlineKeyboardMarkup(inline_keyboard=buttons)
    finally:
        session.close()

def get_item_action_kb(item_id, in_cart=False):
    buttons = []
    if not in_cart:
        buttons.append([InlineKeyboardButton(text="🛒 Добавить в корзину", callback_data=f"add_{item_id}")])
    else:
        # УБИРАЕМ кнопки ➖ и ➕, оставляем только удаление
        buttons.append([InlineKeyboardButton(text="🗑️ Удалить из корзины", callback_data=f"remove_{item_id}")])
    buttons.append([InlineKeyboardButton(text="↩️ В меню", callback_data="back_to_categories")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)