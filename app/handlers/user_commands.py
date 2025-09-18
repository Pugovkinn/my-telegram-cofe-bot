from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import CommandStart, Command
from app.keyboards.main_kb import get_main_keyboard
from app.models.database import get_db_session, User  # Импортируем get_db_session

user_router = Router()

@user_router.message(CommandStart())
async def cmd_start(message: Message):
    session = get_db_session()  # Создаем сессию здесь
    try:
        user = session.query(User).filter(User.tg_id == message.from_user.id).first()
        if not user:
            new_user = User(
                tg_id=message.from_user.id,
                username=message.from_user.username,
                first_name=message.from_user.first_name
            )
            session.add(new_user)
            session.commit()
            await message.answer(
                "☕ Добро пожаловать в CoffeeBot 24/7!\n\n"
                "Мы готовы принять ваш заказ в любое время дня и ночи!\n"
                "Нажмите '☕ Меню' чтобы начать заказ.",
                reply_markup=get_main_keyboard()
            )
        else:
            await message.answer(
                "С возвращением! Готовы продолжить заказ?",
                reply_markup=get_main_keyboard()
            )
    finally:
        session.close()  # Закрываем сессию

@user_router.message(F.text == "📞 Контакты")
async def show_contacts(message: Message):
    await message.answer(
        "🏠 Наш адрес: ул. Кофейная, 1\n"
        "📞 Телефон: +7 (999) 123-45-67\n"
        "⏰ Часы работы: круглосуточно!"
    )

@user_router.message(F.text == "ℹ️ О нас")
async def show_about(message: Message):
    await message.answer(
        "CoffeeBot 24/7 - первый телеграм-бот для заказа кофе и десертов!\n"
        "Мы работаем круглосуточно, чтобы вы могли наслаждаться любимыми напитками в любое время!"
    )
    
@user_router.message(F.text == "📦 Мои заказы")
async def show_orders_placeholder(message: Message):
    await message.answer("📦 Функция просмотра заказов скоро будет доступна!")