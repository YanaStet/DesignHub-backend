from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from datetime import timedelta # <--- ОСЬ ВИПРАВЛЕННЯ

import crud, models, schemas, security, config
from database import SessionLocal, engine, get_db 
from routers import users, works, categories, tags 

# Створюємо всі таблиці в базі даних (якщо їх ще немає)
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# === Налаштування CORS ===
origins = [
    "http://localhost:3000",
    "http://localhost:5173", 
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# === Кінець налаштування CORS ===


# === Роутер для логіну ===
@app.post("/token", response_model=schemas.Token)
def login_for_access_token(
    db: Session = Depends(get_db), 
    form_data: OAuth2PasswordRequestForm = Depends()
):
    """
    Отримує email (в полі username) та пароль,
    повертає JWT токен.
    """
    user = crud.authenticate_user(db, email=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # Тепер 'timedelta' буде визначено
    access_token_expires = timedelta(minutes=config.settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
# === Кінець роутера логіну ===


# === Підключення роутерів ===
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(works.router, prefix="/works", tags=["Works"])
app.include_router(categories.router, prefix="/categories", tags=["Categories"])
app.include_router(tags.router, prefix="/tags", tags=["Tags"])
# === Кінець підключення ===


@app.get("/")
def read_root():
    return {"message": "Welcome to the Designer Portfolio API!"}

