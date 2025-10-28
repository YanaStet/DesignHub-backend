from sqlalchemy.orm import Session
import models, schemas
from passlib.context import CryptContext

# Створюємо контекст для хешування паролів
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

def get_user(db: Session, user_id: int):
    """Отримати користувача за ID"""
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    """Отримати користувача за email"""
    return db.query(models.User).filter(models.User.email == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    """Отримати список користувачів з пагінацією"""
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate):
    """Створити нового користувача"""
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        email=user.email,
        firstName=user.firstName,
        lastName=user.lastName,
        password_hash=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user