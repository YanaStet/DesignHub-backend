from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from config import settings # Імпортуємо наші налаштування

# Використовуємо DATABASE_URL з settings
DATABASE_URL = settings.DATABASE_URL

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# === ПЕРЕМІЩЕНА ФУНКЦІЯ ===
# Функція-генератор для створення сесії бази даних
def get_db():
    """
    Залежність (Dependency) для отримання сесії бази даних.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

