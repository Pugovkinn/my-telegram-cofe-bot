from aiogram.fsm.state import State, StatesGroup

class OrderState(StatesGroup):
    choosing_delivery = State()      # Выбор способа получения
    choosing_time = State()          # Выбор времени
    entering_phone = State()         # Ввод телефона
    confirming_order = State()       # Подтверждение заказа