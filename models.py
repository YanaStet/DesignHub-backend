import enum # <--- 1. Імпортуємо enum
from sqlalchemy import (Column, Integer, String, Text, DateTime, ForeignKey, 
                        DECIMAL, Table, func, Enum as saEnum) # <--- 2. Імпортуємо Enum з SQLAlchemy
from sqlalchemy.orm import relationship
from database import Base

# --- Асоціативні таблиці для зв'язків Many-to-Many ---

# Зв'язок між Work та Category
WorkCategory = Table('Work_Category', Base.metadata,
    Column('work_id', Integer, ForeignKey('Work.id'), primary_key=True),
    Column('category_id', Integer, ForeignKey('Category.id'), primary_key=True)
)

# Зв'язок між Work та Tag
WorkTag = Table('Work_Tag', Base.metadata,
    Column('work_id', Integer, ForeignKey('Work.id'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('Tag.id'), primary_key=True)
)

# --- 3. Створюємо Python Enum для Ролей ---
class UserRole(str, enum.Enum):
    designer = "designer"
    admin = "admin"
    moderator = "moderator"


# --- Основні Моделі ---

class User(Base):
    __tablename__ = "User"
    id = Column(Integer, primary_key=True, index=True)
    firstName = Column(String(100), nullable=False)
    lastName = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    
    # --- 4. Використовуємо Enum у моделі ---
    role = Column(saEnum(UserRole), nullable=False, default=UserRole.designer)
    
    password_hash = Column(String(255), nullable=False)
    registration_date = Column(DateTime, server_default=func.now())

    # --- Зв'язки ---
    designer_profile = relationship("Designer_Profile", back_populates="designer", uselist=False, cascade="all, delete-orphan")
    works = relationship("Work", back_populates="designer", cascade="all, delete-orphan")
    # Виправляємо зв'язки для коментарів на основі sql_schema
    comments = relationship("Comment", back_populates="author", foreign_keys="[Comment.author_id]", cascade="all, delete-orphan")

class Designer_Profile(Base):
    __tablename__ = "Designer_Profile"
    designer_id = Column(Integer, ForeignKey("User.id"), primary_key=True)
    specialization = Column(String(255))
    bio = Column(Text)
    experience = Column(Integer, default=0) 
    rating = Column(DECIMAL(3, 2), default=0.00)
    views_count = Column(Integer, default=0)
    work_amount = Column(Integer, default=0)

    # --- Зв'язок ---
    designer = relationship("User", back_populates="designer_profile")

class Work(Base):
    __tablename__ = "Work"
    id = Column(Integer, primary_key=True, index=True)
    designer_id = Column(Integer, ForeignKey("User.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    upload_date = Column(DateTime, server_default=func.now())
    views_count = Column(Integer, default=0)
    image_url = Column(String(255)) 

    # --- Зв'язки ---
    designer = relationship("User", back_populates="works")
    comments = relationship("Comment", back_populates="work", cascade="all, delete-orphan")
    
    # Зв'язки Many-to-Many
    categories = relationship("Category", secondary=WorkCategory, back_populates="works")
    tags = relationship("Tag", secondary=WorkTag, back_populates="works")

class Category(Base):
    __tablename__ = "Category"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)

    # --- Зв'язок ---
    works = relationship("Work", secondary=WorkCategory, back_populates="categories")

class Tag(Base):
    __tablename__ = "Tag"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)

    # --- Зв'язок ---
    works = relationship("Work", secondary=WorkTag, back_populates="tags")

class Comment(Base):
    __tablename__ = "Comment"
    id = Column(Integer, primary_key=True, index=True)
    author_id = Column(Integer, ForeignKey("User.id"), nullable=False) # Автор коментаря
    work_id = Column(Integer, ForeignKey("Work.id"), nullable=False)   # Робота, яку коментують
    
    rating_score = Column(Integer) # 1-5
    comment_text = Column(Text, nullable=False)
    review_date = Column(DateTime, server_default=func.now())

    # --- Зв'язки ---
    work = relationship("Work", back_populates="comments")
    author = relationship("User", back_populates="comments") # Зв'язок з автором