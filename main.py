from fastapi import FastAPI
# Додаємо імпорт для CORSMiddleware
from fastapi.middleware.cors import CORSMiddleware

from database import engine, Base
from routers import users

# Створюємо всі таблиці в базі даних
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="DesignHub API",
    description="API для сайту-портфоліо дизайнерів.",
    version="1.0.0",
)

# Список адрес (origins), з яких дозволено робити запити
# 5500 - стандартний порт для Live Server у VS Code
# 3000 - стандартний порт для React
origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://127.0.0.1:5500",
    "http://localhost:5173"
]

# Додаємо Middleware для CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,       # Дозволити запити з цих джерел
    allow_credentials=True,      # Дозволити кукі (credentials)
    allow_methods=["*"],         # Дозволити всі методи (GET, POST, etc.)
    allow_headers=["*"],         # Дозволити всі заголовки
)

# Підключаємо роутер для користувачів
app.include_router(users.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the DesignHub API!"}