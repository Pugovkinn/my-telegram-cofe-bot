from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from app.keyboards.inline_kb import get_categories_kb, get_items_kb, get_item_action_kb
from app.models.database import get_db_session, Item, CartItem, User  # Импортируем get_db_session вместо session

menu_router = Router()

# Обработка кнопки "Меню"
@menu_router.message(F.text == "☕ Меню")
async def show_categories(message: Message):
    await message.answer("Выберите категорию:", reply_markup=get_categories_kb())

# Обработка нажатия на категорию
@menu_router.callback_query(F.data.startswith("category_"))
async def show_items(callback: CallbackQuery):
    category_id = int(callback.data.split("_")[1])
    await callback.message.edit_text("Выберите товар:", reply_markup=get_items_kb(category_id))
    await callback.answer()

# Обработка нажатия на товар
@menu_router.callback_query(F.data.startswith("item_"))
async def show_item(callback: CallbackQuery):
    session = get_db_session()  # Создаем сессию здесь
    try:
        item_id = int(callback.data.split("_")[1])
        item = session.query(Item).filter(Item.id == item_id).first()
        if item:
            text = f"<b>{item.name}</b>\n\n{item.description}\n\nЦена: <b>{item.price}₽</b>"
            # Проверим, есть ли товар уже в корзине пользователя
            user = session.query(User).filter(User.tg_id == callback.from_user.id).first()
            in_cart = any(cart_item.item_id == item_id for cart_item in user.cart)
            await callback.message.edit_text(
                text,
                reply_markup=get_item_action_kb(item_id, in_cart)
            )
    finally:
        session.close()  # Не забываем закрыть сессию
    await callback.answer()
    
# Обработка кнопки "Назад к категориям"
@menu_router.callback_query(F.data == "back_to_categories")
async def back_to_categories(callback: CallbackQuery):
    await callback.message.edit_text(
        "Выберите категорию:",
        reply_markup=get_categories_kb()
    )
    await callback.answer()

# Обработка кнопки "Назад" из товара в меню
@menu_router.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback: CallbackQuery):
    await callback.message.edit_text(
        "Выберите категорию:",
        reply_markup=get_categories_kb()
    )
    await callback.answer()