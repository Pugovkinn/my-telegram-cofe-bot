from app.models.database import get_db_session, Category, Item

def fill_test_data():
    session = get_db_session()
    
    # Очищаем старые данные (осторожно!)
    session.query(Item).delete()
    session.query(Category).delete()
    session.commit()
    
    # Создаем категории
    coffee_category = Category(name="☕ Кофе")
    tea_category = Category(name="🍵 Чай")
    desserts_category = Category(name="🍰 Десерты")
    
    session.add_all([coffee_category, tea_category, desserts_category])
    session.commit()
    
    # Создаем товары
    items = [
        Item(name="Эспрессо", description="Классический крепкий кофе", price=150.0, category_id=coffee_category.id),
        Item(name="Капучино", description="Кофе с молочной пенкой", price=200.0, category_id=coffee_category.id),
        Item(name="Латте", description="Нежный кофе с молоком", price=220.0, category_id=coffee_category.id),
        Item(name="Зеленый чай", description="Ароматный зеленый чай", price=100.0, category_id=tea_category.id),
        Item(name="Черный чай", description="Крепкий черный чай", price=100.0, category_id=tea_category.id),
        Item(name="Чизкейк", description="Нежный нью-йоркский чизкейк", price=250.0, category_id=desserts_category.id),
        Item(name="Тирамису", description="Итальянский десерт", price=280.0, category_id=desserts_category.id),
    ]
    
    session.add_all(items)
    session.commit()
    print("✅ Тестовые данные добавлены в БД!")
    
    # Проверяем
    categories = session.query(Category).all()
    print(f"Категории: {[cat.name for cat in categories]}")
    
    items = session.query(Item).all()
    print(f"Товары: {[item.name for item in items]}")

if __name__ == "__main__":
    fill_test_data()