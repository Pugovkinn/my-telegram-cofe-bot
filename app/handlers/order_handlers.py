from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from app.keyboards.main_kb import get_main_keyboard
from app.models.database import get_db_session, User, CartItem, Order
from app.utils.states import OrderState
from app.services.payment_service import payment_service

order_router = Router()

# Начало оформления заказа
@order_router.message(F.text == "📦 Оформить заказ")
async def start_order(message: Message, state: FSMContext):
    session = get_db_session()
    try:
        user = session.query(User).filter(User.tg_id == message.from_user.id).first()
        
        if not user or not user.cart:
            await message.answer("🛒 Ваша корзина пуста! Добавьте товары перед оформлением заказа.")
            return
        
        # Считаем общую сумму
        total = sum(item.item.price * item.quantity for item in user.cart)
        
        # Сохраняем данные в состоянии
        await state.update_data(total=total, user_id=user.id)
        
        # Предлагаем выбрать способ получения
        delivery_kb = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="🚗 Доставка")],
                [KeyboardButton(text="🏃‍♂️ Самовывоз")],
                [KeyboardButton(text="❌ Отмена")]
            ],
            resize_keyboard=True
        )
        
        await message.answer(
            f"🛒 Ваш заказ на сумму: {int(total)}₽\n\n"
            "Выберите способ получения:",
            reply_markup=delivery_kb
        )
        await state.set_state(OrderState.choosing_delivery)
        
    finally:
        session.close()

# Выбор способа доставки
@order_router.message(OrderState.choosing_delivery, F.text.in_(["🚗 Доставка", "🏃‍♂️ Самовывоз"]))
async def choose_delivery(message: Message, state: FSMContext):
    delivery_type = "доставка" if message.text == "🚗 Доставка" else "самовывоз"
    await state.update_data(delivery_type=delivery_type)
    
    # Запрос номера телефона
    phone_kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📞 Отправить номер", request_contact=True)],
            [KeyboardButton(text="❌ Отмена")]
        ],
        resize_keyboard=True
    )
    
    await message.answer(
        "📞 Пожалуйста, поделитесь вашим номером телефона для связи:",
        reply_markup=phone_kb
    )
    await state.set_state(OrderState.entering_phone)

# Обработка номера телефона
@order_router.message(OrderState.entering_phone, F.contact)
async def process_phone(message: Message, state: FSMContext):
    phone = message.contact.phone_number
    await state.update_data(phone=phone)
    
    # Переход к подтверждению заказа
    data = await state.get_data()
    total = data['total']
    delivery_type = data['delivery_type']
    
    confirm_kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="✅ Подтвердить заказ")],
            [KeyboardButton(text="❌ Отмена")]
        ],
        resize_keyboard=True
    )
    
    await message.answer(
        f"📋 <b>Подтверждение заказа:</b>\n\n"
        f"💵 Сумма: {int(total)}₽\n"
        f"🚚 Способ: {delivery_type}\n"
        f"📞 Телефон: {phone}\n\n"
        "Подтвердите оформление заказа:",
        reply_markup=confirm_kb,
        parse_mode="HTML"
    )
    await state.set_state(OrderState.confirming_order)

# Подтверждение заказа
@order_router.message(OrderState.confirming_order, F.text == "✅ Подтвердить заказ")
async def confirm_order(message: Message, state: FSMContext):
    session = get_db_session()
    try:
        data = await state.get_data()
        user_id = data['user_id']
        total = data['total']
        delivery_type = data['delivery_type']
        phone = data['phone']
        
        user = session.query(User).filter(User.id == user_id).first()
        
        # Формируем текст заказа
        order_text = f"📦 <b>Новый заказ!</b>\n\n"
        order_text += f"👤 Клиент: {user.first_name}\n"
        order_text += f"📞 Телефон: {phone}\n"
        order_text += f"🚚 Способ: {delivery_type}\n\n"
        order_text += "🛒 Состав заказа:\n"
        
        for i, item in enumerate(user.cart, 1):
            order_text += f"{i}. {item.item.name} x{item.quantity} - {int(item.item.price * item.quantity)}₽\n"
        
        order_text += f"\n💵 Итого: {int(total)}₽"
        
        # Создаем запись заказа в БД
        new_order = Order(
            user_id=user.id,
            amount=total,
            status='ожидает оплаты',
            items=order_text,
            created_at=datetime.utcnow()
        )
        session.add(new_order)
        session.commit()
        
        # ДЕМО-РЕЖИМ: Создаем демо-платеж
        payment = await payment_service.create_payment(
            amount=1.00,  # Всего 1 рубль для демо
            description=f"Демо-заказ #{new_order.id}",
            order_id=new_order.id
        )
        
        if payment:
            # Сохраняем ID платежа в заказе
            new_order.payment_id = payment['id']
            session.commit()
            
            await message.answer(
                f"✅ Заказ #{new_order.id} оформлен!\n\n"
                f"💵 К оплате: 1₽ (демо-режим)\n\n"
                "Для тестирования нажмите кнопку ниже:",
                reply_markup=payment_service.get_demo_payment_keyboard(new_order.id),
                parse_mode="HTML"
            )
        else:
            await message.answer(
                "❌ Ошибка при создании платежа",
                reply_markup=get_main_keyboard()
            )
        
        await state.clear()
        
    except Exception as e:
        session.rollback()
        await message.answer("❌ Ошибка при оформлении заказа")
        print(f"Order error: {e}")
    finally:
        session.close()

# Добавляем обработчик демо-оплаты
@order_router.callback_query(F.data.startswith("demo_pay_"))
async def process_demo_payment(callback: CallbackQuery):
    await callback.answer("💳 Демо-платеж обработан! Теперь нажмите 'Я оплатил'")

# Отмена заказа
@order_router.message(StateFilter(OrderState), F.text == "❌ Отмена")
async def cancel_order(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "❌ Оформление заказа отменено",
        reply_markup=get_main_keyboard()
    )
    
# ============================================================
# ДЕМО-СТРАНИЦА ОПЛАТЫ (КРАСИВАЯ ВЕРСИЯ)
# ============================================================

@order_router.callback_query(F.data.startswith("demo_page_"))
async def show_demo_payment_page(callback: CallbackQuery):
    """Показывает красивую демо-страницу оплаты"""
    order_id = callback.data.split("_")[2]
    
    demo_text = """
💳 <b>ДЕМО-СТРАНИЦА ОПЛАТЫ</b>
━━━━━━━━━━━━━━━━━━━━

🏪 <b>CoffeeBot 24/7</b>
📍 Заказ #{} · 1₽

┌─────────────────┐
│   💳 ОПЛАТА    │
├─────────────────┤
│  Карта: •••• 4444  │
│  Сумма: 1₽       │
│  Стату: Ожидание  │
└─────────────────┘

🔹 <b>Это демо-режим для портфолио</b>
🔹 В реальном проекте здесь была бы
   интеграция с YooKassa/CloudPayments
🔹 Для тестирования нажмите кнопку ниже
    """.format(order_id)
    
    demo_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="✅ Симулировать успешную оплату", 
            callback_data=f"demo_pay_success_{order_id}"
        )],
        [InlineKeyboardButton(
            text="❌ Симулировать ошибку оплаты", 
            callback_data=f"demo_pay_fail_{order_id}"
        )],
        [InlineKeyboardButton(
            text="↩️ Вернуться в бот", 
            callback_data=f"back_to_bot_{order_id}"
        )]
    ])
    
    try:
        await callback.message.edit_text(
            demo_text, 
            reply_markup=demo_kb, 
            parse_mode="HTML"
        )
    except Exception as e:
        await callback.message.answer(
            demo_text, 
            reply_markup=demo_kb, 
            parse_mode="HTML"
        )
    await callback.answer()

@order_router.callback_query(F.data.startswith("demo_pay_success_"))
async def process_demo_payment_success(callback: CallbackQuery):
    """Обработка успешной демо-оплаты"""
    order_id = callback.data.split("_")[3]
    
    success_text = """
✅ <b>ПЛАТЕЖ УСПЕШНО ОБРАБОТАН!</b>
━━━━━━━━━━━━━━━━━━━━

💳 Сумма: <b>1₽</b>
📦 Заказ: <b>#{}</b>
🕒 Время: <b>{}</b>
🔢 Код: <b>APPROVED</b>

Оплата прошла успешно! Теперь вернитесь в бот
и нажмите «Я оплатил» для завершения заказа.
    """.format(order_id, datetime.now().strftime("%H:%M:%S"))
    
    success_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="↩️ Вернуться в бот", 
            callback_data=f"back_to_bot_{order_id}"
        )]
    ])
    
    await callback.message.edit_text(
        success_text, 
        reply_markup=success_kb, 
        parse_mode="HTML"
    )
    await callback.answer("✅ Платеж успешно обработан!")

@order_router.callback_query(F.data.startswith("demo_pay_fail_"))
async def process_demo_payment_fail(callback: CallbackQuery):
    """Обработка неуспешной демо-оплаты"""
    order_id = callback.data.split("_")[3]
    
    fail_text = """
❌ <b>ОШИБКА ОПЛАТЫ</b>
━━━━━━━━━━━━━━━━━━━━

💳 Сумма: <b>1₽</b>
📦 Заказ: <b>#{}</b>
🕒 Время: <b>{}</b>
🔢 Код: <b>DECLINED</b>

⚠️ <b>Причина:</b> Недостаточно средств на карте

Попробуйте другую карту или обратитесь в банк.
    """.format(order_id, datetime.now().strftime("%H:%M:%S"))
    
    fail_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="🔄 Попробовать снова", 
            callback_data=f"demo_page_{order_id}"
        )],
        [InlineKeyboardButton(
            text="↩️ Вернуться в бот", 
            callback_data=f"back_to_bot_{order_id}"
        )]
    ])
    
    await callback.message.edit_text(
        fail_text, 
        reply_markup=fail_kb, 
        parse_mode="HTML"
    )
    await callback.answer("❌ Ошибка оплаты")

@order_router.callback_query(F.data.startswith("back_to_bot_"))
async def back_to_bot(callback: CallbackQuery):
    """Возврат в бот из демо-страницы"""
    order_id = callback.data.split("_")[3]
    
    await callback.message.edit_text(
        "🔙 <b>Возвращаемся в бот...</b>\n\n"
        "Теперь нажмите «✅ Я оплатил» для завершения демо-оплаты.",
        parse_mode="HTML"
    )
    await callback.answer()