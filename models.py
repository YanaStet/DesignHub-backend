# ... (існуючі імпорти) ...
from sqlalchemy import (Column, Integer, String, Text, DateTime, ForeignKey, 
                        DECIMAL, Table, func)
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

# --- Основні Моделі ---

class User(Base):
    __tablename__ = "User"
    id = Column(Integer, primary_key=True, index=True)
    firstName = Column(String(50), nullable=False)
    lastName = Column(String(50), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    role = Column(String(20), nullable=False, default='user')
    password_hash = Column(String(255), nullable=False)
    registration_date = Column(DateTime, server_default=func.now())

    # --- Зв'язки ---
    designer_profile = relationship("Designer_Profile", back_populates="designer", uselist=False, cascade="all, delete-orphan")
    works = relationship("Work", back_populates="designer", cascade="all, delete-orphan")
    comments_sent = relationship("Comment", back_populates="designer", foreign_keys="[Comment.designer_id]")
    comments_received = relationship("Comment", back_populates="receiver", foreign_keys="[Comment.receiver_id]")

class Designer_Profile(Base):
    __tablename__ = "Designer_Profile"
    designer_id = Column(Integer, ForeignKey("User.id"), primary_key=True)
    specialization = Column(String(100))
    bio = Column(Text)
    experience = Column(Integer) # Роки досвіду
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
    image_url = Column(String(512)) # URL до зображення (напр., S3)

    # --- Зв'язки ---
    designer = relationship("User", back_populates="works")
    comments = relationship("Comment", back_populates="work", cascade="all, delete-orphan")
    
    # Зв'язки Many-to-Many
    categories = relationship("Category", secondary=WorkCategory, back_populates="works")
    tags = relationship("Tag", secondary=WorkTag, back_populates="works")

class Category(Base):
    __tablename__ = "Category"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, index=True, nullable=False)

    # --- Зв'язок ---
    works = relationship("Work", secondary=WorkCategory, back_populates="categories")

class Tag(Base):
    __tablename__ = "Tag"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, index=True, nullable=False)

    # --- Зв'язок ---
    works = relationship("Work", secondary=WorkTag, back_populates="tags")

class Comment(Base):
    __tablename__ = "Comment"
    id = Column(Integer, primary_key=True, index=True)
    designer_id = Column(Integer, ForeignKey("User.id"), nullable=False)
    work_id = Column(Integer, ForeignKey("Work.id"), nullable=False)
    receiver_id = Column(Integer, ForeignKey("User.id"), nullable=False) # Власник роботи
    
    rating_score = Column(Integer) # 1-5
    comment_text = Column(Text, nullable=False)
    review_date = Column(DateTime, server_default=func.now())

    # --- Зв'язки ---
    work = relationship("Work", back_populates="comments")
    designer = relationship("User", back_populates="comments_sent", foreign_keys=[designer_id])
    receiver = relationship("User", back_populates="comments_received", foreign_keys=[receiver_id])

