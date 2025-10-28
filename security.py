import models
import crud
from database import SessionLocal
from config import settings
from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

# --- Контекст хешування паролів ---
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --- Схема OAuth2 ---
# "tokenUrl" вказує на ендпоінт, де фронтенд буде отримувати токен
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_db():
    """Залежність для отримання сесії бази даних."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Перевіряє, чи збігається пароль з хешем."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Повертає хеш пароля."""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """Створює JWT Access Token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        # Використовуємо налаштування з .env
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def get_current_user(
    token: str = Depends(oauth2_scheme), 
    db: Session = Depends(get_db)
) -> models.User:
    """
    Залежність (Dependency) для FastAPI.
    Розшифровує токен, перевіряє його та повертає поточного користувача.
    Якщо токен невалідний, генерує виняток HTTPException.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Розшифровуємо токен
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        # "sub" (subject) - це email, який ми закодували при створенні токена
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    # Отримуємо користувача з бази даних
    user = crud.get_user_by_email(db, email=email)
    if user is None:
        raise credentials_exception
    
    return user
