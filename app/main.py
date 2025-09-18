import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from app.handlers import user_commands, menu_handlers, cart_handlers, order_handlers
from config import BOT_TOKEN

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    # Создаем бота и диспетчер
    bot = Bot(token=BOT_TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    # Регистрируем роутеры
    dp.include_router(user_commands.user_router)
    dp.include_router(menu_handlers.menu_router)
    dp.include_router(cart_handlers.cart_router)
    dp.include_router(order_handlers.order_router)
    # Другие роутеры добавим позже

    logger.info("Бот запущен! Нажмите Ctrl+C для остановки")
    
    try:
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}")
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())