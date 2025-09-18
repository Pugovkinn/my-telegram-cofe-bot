from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup, KeyboardButton
from app.keyboards.main_kb import get_main_keyboard
from app.keyboards.inline_kb import get_item_action_kb
from app.models.database import get_db_session, User, CartItem, Item
import logging

logger = logging.getLogger(__name__)
cart_router = Router()

# Показать корзину
@cart_router.message(F.text == "🛒 Корзина")
async def show_cart(message: Message):
    logger.info("Кнопка Корзина нажата!")
    print("DEBUG: Кнопка Корзина нажата!")
    
    session = get_db_session()
    try:
        user = session.query(User).filter(User.tg_id == message.from_user.id).first()
        print(f"DEBUG: User found: {user}")
        
        if not user or not user.cart:
            print("DEBUG: Cart is empty")
            await message.answer("🛒 Ваша корзина пуста\n\nВернитесь в меню чтобы добавить товары ☕")
            return
        
        print(f"DEBUG: Cart items: {len(user.cart)}")
        
        total = 0
        cart_text = "🛒 <b>Ваша корзина:</b>\n\n"
        
        for i, cart_item in enumerate(user.cart, 1):
            item_total = cart_item.item.price * cart_item.quantity
            cart_text += f"{i}. {cart_item.item.name} x{cart_item.quantity} - {int(item_total)}₽\n"
            total += item_total
        
        cart_text += f"\n💵 Итого: {int(total)}₽"
        print(f"DEBUG: Cart text: {cart_text}")
        
        # Создаем клавиатуру для корзины
        cart_keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="📦 Оформить заказ")],
                [KeyboardButton(text="↩️ Назад в меню")]
            ],
            resize_keyboard=True
        )
        
        print("DEBUG: Sending message...")
        await message.answer(cart_text, reply_markup=cart_keyboard, parse_mode="HTML")
        print("DEBUG: Message sent successfully!")
        
    except Exception as e:
        logger.error(f"Error in show_cart: {e}")
        print(f"ERROR in show_cart: {e}")
        await message.answer("❌ Ошибка при загрузке корзины")
    finally:
        session.close()

# Заглушка для кнопки "Мои заказы"
@cart_router.message(F.text == "📦 Мои заказы")
async def show_orders_placeholder(message: Message):
    await message.answer("📦 Функция просмотра заказов скоро будет доступна!")

# Обработка кнопки "Назад в меню"
@cart_router.message(F.text == "↩️ Назад в меню")
async def back_to_menu(message: Message):
    await message.answer("Возвращаемся в главное меню:", reply_markup=get_main_keyboard())

# Добавить товар в корзину
@cart_router.callback_query(F.data.startswith("add_"))
async def add_to_cart(callback: CallbackQuery):
    session = get_db_session()
    try:
        item_id = int(callback.data.split("_")[1])
        
        user = session.query(User).filter(User.tg_id == callback.from_user.id).first()
        item = session.query(Item).filter(Item.id == item_id).first()
        
        if not user or not item:
            await callback.answer("❌ Ошибка добавления в корзину")
            return
        
        # Проверяем, есть ли уже товар в корзине
        cart_item = session.query(CartItem).filter(
            CartItem.user_id == user.id,
            CartItem.item_id == item_id
        ).first()
        
        if cart_item:
            # Если товар уже есть - увеличиваем количество
            cart_item.quantity += 1
        else:
            # Если товара нет - создаем новую запись
            new_cart_item = CartItem(user_id=user.id, item_id=item_id, quantity=1)
            session.add(new_cart_item)
        
        session.commit()
        
        # Обновляем сообщение с товаром
        text = f"<b>{item.name}</b>\n\n{item.description}\n\nЦена: <b>{int(item.price)}₽</b>"
        
        await callback.message.edit_text(
            text,
            reply_markup=get_item_action_kb(item_id, True)
        )
        
        await callback.answer(f"✅ {item.name} добавлен в корзину!")
        
    except Exception as e:
        session.rollback()
        await callback.answer("❌ Ошибка при добавлении в корзину")
        print(f"Error adding to cart: {e}")
    finally:
        session.close()

# Удалить товар из корзины
@cart_router.callback_query(F.data.startswith("remove_"))
async def remove_from_cart(callback: CallbackQuery):
    session = get_db_session()
    try:
        item_id = int(callback.data.split("_")[1])
        user = session.query(User).filter(User.tg_id == callback.from_user.id).first()
        item = session.query(Item).filter(Item.id == item_id).first()
        
        if not user or not item:
            await callback.answer("❌ Товар не найден")
            return
        
        cart_item = session.query(CartItem).filter(
            CartItem.user_id == user.id,
            CartItem.item_id == item_id
        ).first()
        
        if cart_item:
            session.delete(cart_item)
            session.commit()
            
            # Обновляем сообщение - товар больше не в корзине
            text = f"<b>{item.name}</b>\n\n{item.description}\n\nЦена: <b>{int(item.price)}₽</b>"
            await callback.message.edit_text(
                text,
                reply_markup=get_item_action_kb(item_id, False)
            )
            
            await callback.answer("🗑️ Товар удален из корзины")
        else:
            await callback.answer("❌ Товар не найден в корзине")
            
    except Exception as e:
        session.rollback()
        await callback.answer("❌ Ошибка")
        print(f"Error removing from cart: {e}")
    finally:
        session.close()