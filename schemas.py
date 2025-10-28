from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

# Базова схема для користувача
class UserBase(BaseModel):
    firstName: str
    lastName: str
    email: EmailStr

# Схема для створення користувача (отримуємо пароль)
class UserCreate(UserBase):
    password: str

# Схема для повернення даних про користувача (пароль не повертаємо)
class User(UserBase):
    id: int
    role: str
    registration_date: datetime

    class Config:
        orm_mode = True # Дозволяє Pydantic працювати з моделями SQLAlchemy
