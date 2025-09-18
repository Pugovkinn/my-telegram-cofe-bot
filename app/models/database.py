from sqlalchemy import create_engine, Column, Integer, String, Float, Text, DateTime, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from datetime import datetime
import os

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    tg_id = Column(Integer, unique=True, nullable=False)
    username = Column(String(100))
    first_name = Column(String(100))
    phone = Column(String(20))
    cart = relationship("CartItem", back_populates="user", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="user")

class Category(Base):
    __tablename__ = 'categories'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    items = relationship("Item", back_populates="category")

class Item(Base):
    __tablename__ = 'items'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    price = Column(Float, nullable=False)
    category_id = Column(Integer, ForeignKey('categories.id'))
    category = relationship("Category", back_populates="items")

class CartItem(Base):
    __tablename__ = 'cart_items'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    item_id = Column(Integer, ForeignKey('items.id'))
    quantity = Column(Integer, default=1)
    user = relationship("User", back_populates="cart")
    item = relationship("Item")

class Order(Base):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    amount = Column(Float, nullable=False)
    status = Column(String(50), default='ожидает оплаты')
    created_at = Column(DateTime, default=datetime.utcnow)
    items = Column(Text)
    user = relationship("User", back_populates="orders")
    payment_id = Column(String(100))

# Путь к БД
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'database.db')
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

# Создаем движок БД
engine = create_engine(f'sqlite:///{DB_PATH}', echo=True)

# Создаем фабрику сессий
SessionLocal = sessionmaker(bind=engine)

# Функция для получения сессии
def get_db_session():
    return SessionLocal()

# Создаем таблицы
Base.metadata.create_all(engine)