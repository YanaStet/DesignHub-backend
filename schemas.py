from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import List, Optional

# --- Схеми для Тегів ---

class TagBase(BaseModel):
    name: str

class TagCreate(TagBase):
    pass

class Tag(TagBase):
    id: int

    class Config:
        from_attributes = True

# --- Схеми для Категорій ---

class CategoryBase(BaseModel):
    name: str

class CategoryCreate(CategoryBase):
    pass

class Category(CategoryBase):
    id: int

    class Config:
        from_attributes = True

# --- Схеми для Користувача (оновлені) ---

class UserBase(BaseModel):
    email: EmailStr
    firstName: str
    lastName: str

class UserCreate(UserBase):
    password: str
    role: str = "user"

class User(UserBase):
    id: int
    role: str
    registration_date: datetime

    class Config:
        from_attributes = True

# --- Схеми для Робіт ---

class WorkBase(BaseModel):
    title: str
    description: Optional[str] = None
    image_url: Optional[str] = None

class WorkCreate(WorkBase):
    """Схема для СТВОРЕННЯ роботи. Приймає ID категорій та назви тегів."""
    category_ids: List[int] = []
    tag_names: List[str] = []

class Work(WorkBase):
    """Схема для ЧИТАННЯ роботи. Повертає повні об'єкти."""
    id: int
    upload_date: datetime
    views_count: int
    
    # Вкладені схеми для зв'язків
    designer: User # Повертає повний об'єкт User
    categories: List[Category] = [] # Повертає список об'єктів Category
    tags: List[Tag] = [] # Повертає список об'єктів Tag

    class Config:
        from_attributes = True

# --- Схеми для токена ---

class Token(BaseModel):
    access_token: str
    token_type: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

