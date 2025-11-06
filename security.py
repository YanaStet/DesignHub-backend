from datetime import datetime, timedelta, timezone
from typing import Optional
from passlib.context import CryptContext
from jose import JWTError, jwt
from config import settings # Імпортуємо наші налаштування
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session 
import schemas 
from database import get_db # <--- ІМПОРТУЄМО get_db ТУТ


# === Налаштування Passlib ===
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# === Налаштування OAuth2 ===
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# === Налаштування JWT ===
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
# === Кінець налаштувань ===


# === Функції безпеки ===

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    password_bytes = password.encode('utf-8')
    print('not passed')
    print(len(password_bytes))
    if len(password_bytes) > 72:
        print('passed')
        password = password_bytes[:72].decode('utf-8', 'ignore')
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        # Використовуємо налаштування за замовчуванням
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(
    db: Session = Depends(get_db), # <--- ВИПРАВЛЕНО: Використовуємо імпортовану функцію
    token: str = Depends(oauth2_scheme)
):
    # Імпортуємо тут, щоб уникнути циклічних імпортів
    import crud 
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = schemas.TokenData(email=email)
    except JWTError:
        raise credentials_exception
    
    user = crud.get_user_by_email(db, email=token_data.email)
    if user is None:
        raise credentials_exception
    return user

