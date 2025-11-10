from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from models import UserRole # <--- 1. Імпортуємо наш Enum

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

# --- Схеми для Користувача (User) ---
# Ці схеми потрібні, щоб `Work` міг показувати, хто дизайнер
class UserBase(BaseModel):
    email: str
    firstName: str
    lastName: str
    # --- 2. Використовуємо Enum тут ---
    # Pydantic автоматично валідує, що рядок є одним зі значень Enum
    role: UserRole = UserRole.designer 

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    registration_date: datetime
    # works: List['Work'] = [] # Можна додати, якщо потрібен зворотний зв'язок

    class Config:
        from_attributes = True

# --- Схеми для Робіт (Work) ---
class WorkBase(BaseModel):
    title: str
    description: Optional[str] = None
    image_url: Optional[str] = None 

class WorkCreate(WorkBase):
    # При створенні ми приймаємо ID категорій та назви тегів
    categories_ids: List[int] = []
    tags_names: List[str] = []

class Work(WorkBase):
    id: int
    designer_id: int
    upload_date: datetime
    views_count: int
    
    # Вкладені схеми для зручності фронтенду
    designer: User
    categories: List[Category] = []
    tags: List[Tag] = []

    class Config:
        from_attributes = True

# --- Схеми для Автентифікації ---
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# --- Схеми для Профілю Дизайнера ---
class DesignerProfileBase(BaseModel):
    specialization: Optional[str] = None
    bio: Optional[str] = None
    experience: Optional[int] = 0

class DesignerProfileCreate(DesignerProfileBase):
    pass

class DesignerProfile(DesignerProfileBase):
    designer_id: int
    rating: float
    views_count: int
    work_amount: int

    class Config:
        from_attributes = True

# Додаємо зворотне посилання для User, щоб уникнути помилок визначення
User.model_rebuild()