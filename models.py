import enum
from sqlalchemy import (Column, Integer, String, Text, DateTime, ForeignKey, 
                        DECIMAL, Table, func, Enum as saEnum)
from sqlalchemy.orm import relationship
from database import Base

# --- Асоціативні таблиці ---
WorkCategory = Table('Work_Category', Base.metadata,
    Column('work_id', Integer, ForeignKey('Work.id'), primary_key=True),
    Column('category_id', Integer, ForeignKey('Category.id'), primary_key=True)
)

WorkTag = Table('Work_Tag', Base.metadata,
    Column('work_id', Integer, ForeignKey('Work.id'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('Tag.id'), primary_key=True)
)

class UserRole(str, enum.Enum):
    designer = "designer"
    admin = "admin"
    moderator = "moderator"

# --- Моделі ---

class User(Base):
    __tablename__ = "User"
    id = Column(Integer, primary_key=True, index=True)
    firstName = Column(String(100), nullable=False)
    lastName = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    role = Column(saEnum(UserRole), nullable=False, default=UserRole.designer)
    password_hash = Column(String(255), nullable=False)
    registration_date = Column(DateTime, server_default=func.now())

    designer_profile = relationship("Designer_Profile", back_populates="designer", uselist=False, cascade="all, delete-orphan")
    works = relationship("Work", back_populates="designer", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="author", foreign_keys="[Comment.author_id]", cascade="all, delete-orphan")
    
    # Зв'язок для історії переглядів
    viewed_works = relationship("WorkView", back_populates="user", cascade="all, delete-orphan")

class Designer_Profile(Base):
    __tablename__ = "Designer_Profile"
    designer_id = Column(Integer, ForeignKey("User.id"), primary_key=True)
    specialization = Column(String(255))
    bio = Column(Text)
    experience = Column(Integer, default=0) 
    rating = Column(DECIMAL(3, 2), default=0.00)
    views_count = Column(Integer, default=0)
    work_amount = Column(Integer, default=0)
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

    designer = relationship("User", back_populates="works")
    comments = relationship("Comment", back_populates="work", cascade="all, delete-orphan")
    categories = relationship("Category", secondary=WorkCategory, back_populates="works")
    tags = relationship("Tag", secondary=WorkTag, back_populates="works")
    
    # === ОСЬ ЦЕЙ РЯДОК КРИТИЧНО ВАЖЛИВИЙ ===
    # Він має бути тут, щоб WorkView міг на нього посилатися
    views = relationship("WorkView", back_populates="work", cascade="all, delete-orphan")

class Category(Base):
    __tablename__ = "Category"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    works = relationship("Work", secondary=WorkCategory, back_populates="categories")

class Tag(Base):
    __tablename__ = "Tag"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    works = relationship("Work", secondary=WorkTag, back_populates="tags")

class Comment(Base):
    __tablename__ = "Comment"
    id = Column(Integer, primary_key=True, index=True)
    author_id = Column(Integer, ForeignKey("User.id"), nullable=False)
    work_id = Column(Integer, ForeignKey("Work.id"), nullable=False)
    rating_score = Column(Integer) 
    comment_text = Column(Text, nullable=False)
    review_date = Column(DateTime, server_default=func.now())
    work = relationship("Work", back_populates="comments")
    author = relationship("User", back_populates="comments")

# === НОВА ТАБЛИЦЯ: Історія переглядів ===
class WorkView(Base):
    __tablename__ = "Work_View"
    id = Column(Integer, primary_key=True, index=True)
    work_id = Column(Integer, ForeignKey("Work.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("User.id"), nullable=False)
    viewed_at = Column(DateTime, server_default=func.now())

    # Зв'язки
    # Тут ми посилаємось на "Work.views", тому у класі Work має бути атрибут views
    work = relationship("Work", back_populates="views")
    user = relationship("User", back_populates="viewed_works")