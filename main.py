from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from datetime import timedelta
from fastapi.staticfiles import StaticFiles
import os

# Імпортуємо всі наші модулі
import crud, models, schemas, security, config
from database import SessionLocal, engine, get_db 

# Імпортуємо всі наші роутери
from routers import users, works, categories, tags, uploads, designer_profiles 

# --- Створення таблиць ---
# Ця команда наказує SQLAlchemy створити всі таблиці
# (визначені як класи, що наслідують Base у models.py)
# у базі даних, до якої підключений engine.
models.Base.metadata.create_all(bind=engine)
# --- Кінець створення таблиць ---

app = FastAPI()

# --- Монтування статичної папки ---
# Це робить папку /static доступною для веб-браузера
# Будь-який файл у папці 'static/images/...' буде доступний 
# за URL-адресою 'http://localhost:8000/static/images/...'
static_dir = "static"
os.makedirs(static_dir, exist_ok=True) # Переконуємося, що папка існує
app.mount("/static", StaticFiles(directory=static_dir), name="static")
# --- Кінець монтування ---


# === Налаштування CORS ===
# Список джерел (ваших фронтенд-додатків), яким дозволено 
# робити запити до цього бекенду.
origins = [
    "http://localhost:3000",  # (для React, за замовчуванням)
    "http://localhost:5173",  # (для Vite + React, за замовчуванням)
    "http://127.0.0.1:5173", # (альтернативна адреса Vite)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,       # Дозволити лише ці джерела
    allow_credentials=True,    # Дозволити надсилання cookies/токенів
    allow_methods=["*"],       # Дозволити всі методи (GET, POST, PUT, DELETE)
    allow_headers=["*"],       # Дозволити всі заголовки
)
# === Кінець налаштування CORS ===


# === Роутер для логіну ===
# Цей ендпоінт знаходиться тут, а не в routers/users.py,
# тому що він є центральним для всієї системи автентифікації.
@app.post("/token", response_model=schemas.Token)
def login_for_access_token(
    db: Session = Depends(get_db), 
    form_data: OAuth2PasswordRequestForm = Depends()
):
    """
    Отримує email (в полі username) та пароль з form-data,
    перевіряє їх і повертає JWT токен.
    """
    user = crud.authenticate_user(db, email=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Визначаємо час життя токена з налаштувань
    access_token_expires = timedelta(minutes=config.settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    # Створюємо сам токен
    access_token = security.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
# === Кінець роутера логіну ===


# === Підключення роутерів ===
# Підключаємо всі наші ендпоінти з папки /routers
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(works.router, prefix="/works", tags=["Works"])
app.include_router(categories.router, prefix="/categories", tags=["Categories"])
app.include_router(tags.router, prefix="/tags", tags=["Tags"])
app.include_router(uploads.router, tags=["Uploads"])
app.include_router(designer_profiles.router, prefix="/profiles", tags=["Designer Profiles"])
# === Кінець підключення ===


# === Кореневий ендпоінт ===
# Простий ендпоінт, щоб перевірити, чи сервер працює
@app.get("/")
def read_root():
    return {"message": "Welcome to the Designer Portfolio API!"}