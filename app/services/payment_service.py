import asyncio
from datetime import datetime

class DemoPaymentService:
    """Демо-сервис для имитации платежей в портфолио"""
    
    @staticmethod
    async def create_payment(amount, description, order_id):
        """
        Создает демо-платеж (в реальности это делал бы YooKassa)
        """
        # Имитируем задержку как при реальном API
        await asyncio.sleep(1)
        
        # Генерируем демо-данные
        payment_data = {
            "id": f"demo_payment_{order_id}_{datetime.now().timestamp()}",
            "status": "pending",
            "amount": amount,
            "description": description,
            "confirmation_url": f"https://t.me/your_bot?start=payment_{order_id}",
            "demo": True  # Помечаем как демо-платеж
        }
        
        return payment_data
    
    @staticmethod
    async def check_payment_status(payment_id):
        """
        Проверяет статус демо-платежа
        """
        # Имитируем проверку статуса
        await asyncio.sleep(0.5)
        
        # В демо-режиме всегда возвращаем "success"
        # В реальном проекте здесь был бы запрос к API YooKassa
        return "succeeded"
    
    @staticmethod
    def get_demo_payment_keyboard(order_id):
        """
        Создает клавиатуру для демо-оплаты
        """
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        
        return InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="💳 Демо-оплата (1 рубль)", 
                    callback_data=f"demo_pay_{order_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="✅ Я оплатил", 
                    callback_data=f"check_payment_{order_id}"
                )
            ]
        ])
def get_demo_payment_keyboard_enhanced(order_id):
    """
    Создает улучшенную клавиатуру для демо-оплаты
    с переходом на красивую страницу
    """
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="💳 Перейти к демо-оплате", 
                callback_data=f"demo_page_{order_id}"
            )
        ],
        [
            InlineKeyboardButton(
                text="✅ Я оплатил", 
                callback_data=f"check_payment_{order_id}"
            )
        ]
    ])
# Создаем экземпляр сервиса
payment_service = DemoPaymentService()