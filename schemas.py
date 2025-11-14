from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from models import UserRole # Імпортуємо Enum

# === Базові Схеми (для вкладених об'єктів) ===

class UserBase(BaseModel):
    id: int
    firstName: str
    lastName: str
    
    class Config:
        from_attributes = True # Pydantic v2 (orm_mode)

class TagBase(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True

class CategoryBase(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True

# === Схеми Користувача (User) ===

class UserCreate(BaseModel):
    email: str
    firstName: str
    lastName: str
    password: str
    role: UserRole # Використовуємо Enum

class UserLogin(BaseModel):
    email: str
    password: str

class User(UserBase):
    email: str
    role: UserRole
    registration_date: datetime

# === Схеми Категорій (Category) ===

class CategoryCreate(BaseModel):
    name: str

class Category(CategoryBase):
    pass # Наразі не має додаткових полів

# === Схеми Тегів (Tag) ===

class TagCreate(BaseModel):
    name: str

class Tag(TagBase):
    pass # Наразі не має додаткових полів

# === Схеми Робіт (Work) ===

class WorkBase(BaseModel):
    title: str
    description: Optional[str] = None
    image_url: Optional[str] = None

class WorkCreate(WorkBase):
    # При створенні ми очікуємо списки ID/назв
    categories_ids: List[int] = []
    tags_names: List[str] = []

class Work(WorkBase):
    id: int
    designer_id: int
    upload_date: datetime
    views_count: int
    
    # Вкладені об'єкти для читання
    designer: UserBase
    categories: List[CategoryBase] = []
    tags: List[TagBase] = []
    
    class Config:
        from_attributes = True

# === Схеми Профілю Дизайнера ===

class DesignerProfileBase(BaseModel):
    specialization: Optional[str] = None
    bio: Optional[str] = None
    experience: Optional[int] = 0

class DesignerProfileCreate(DesignerProfileBase):
    pass

class DesignerProfile(DesignerProfileBase):
    designer_id: int
    rating: float # Використовуємо float, а не Decimal
    views_count: int
    work_amount: int

    class Config:
        from_attributes = True
        
# === НОВІ СХЕМИ ДЛЯ КОМЕНТАРІВ ===

class CommentBase(BaseModel):
    comment_text: str
    rating_score: Optional[int] = None # Рейтинг не обов'язковий при кожному коментарі

class CommentCreate(CommentBase):
    work_id: int # При створенні коментаря, ми маємо знати, до якої роботи він

class CommentUpdate(BaseModel):
    # При оновленні, дозволяємо змінювати лише ці поля
    comment_text: Optional[str] = None
    rating_score: Optional[int] = None

class Comment(CommentBase):
    id: int
    author_id: int
    work_id: int
    review_date: datetime
    
    # Включаємо базову інформацію про автора
    author: UserBase 

    class Config:
        from_attributes = True

# === Схеми для Токенів (Token) ===

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None