from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# URL для підключення до вашої бази даних PostgreSQL
# Формат: "postgresql://user:password@host:port/dbname"
DATABASE_URL = "postgresql://postgres:YANA2580@localhost:5432/DesignHub"

# Створюємо "двигун" SQLAlchemy
engine = create_engine(DATABASE_URL)

# Створюємо фабрику сесій
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Базовий клас для декларативних моделей
Base = declarative_base()

# Функція-залежність для отримання сесії БД у ендпоінтах
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
