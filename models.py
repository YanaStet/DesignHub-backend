import datetime
from sqlalchemy import (Column, Integer, String, Text, DateTime, ForeignKey,
                        DECIMAL, Table)
# ВИПРАВЛЕНО: Забираємо back_populates з імпорту
from sqlalchemy.orm import relationship
from database import Base

# Зв'язок "багато-до-багатьох" між Work та Category
work_category_association = Table('Work_Category', Base.metadata,
    Column('work_id', Integer, ForeignKey('Work.id'), primary_key=True),
    Column('category_id', Integer, ForeignKey('Category.id'), primary_key=True)
)

# Зв'язок "багато-до-багатьох" між Work та Tag
work_tag_association = Table('Work_Tag', Base.metadata,
    Column('work_id', Integer, ForeignKey('Work.id'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('Tag.id'), primary_key=True)
)

class User(Base):
    __tablename__ = "User"
    id = Column(Integer, primary_key=True, index=True)
    firstName = Column(String(100), nullable=False)
    lastName = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    role = Column(String(50), default='designer')
    password_hash = Column(String(255), nullable=False)
    registration_date = Column(DateTime(timezone=True), default=datetime.datetime.utcnow)
    
    # Зв'язки
    profile = relationship("DesignerProfile", back_populates="user", cascade="all, delete-orphan", uselist=False)
    works = relationship("Work", back_populates="designer", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="author", foreign_keys='Comment.author_id', cascade="all, delete-orphan")

class DesignerProfile(Base):
    __tablename__ = "Designer_Profile"
    designer_id = Column(Integer, ForeignKey("User.id"), primary_key=True)
    specialization = Column(String(255))
    bio = Column(Text)
    experience = Column(Integer, default=0)
    rating = Column(DECIMAL(3, 2), default=0.0)
    views_count = Column(Integer, default=0)
    work_amount = Column(Integer, default=0)

    # Зв'язки
    user = relationship("User", back_populates="profile")

class Work(Base):
    __tablename__ = "Work"
    id = Column(Integer, primary_key=True, index=True)
    designer_id = Column(Integer, ForeignKey("User.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    upload_date = Column(DateTime(timezone=True), default=datetime.datetime.utcnow)
    views_count = Column(Integer, default=0)
    image_url = Column(String(255))

    # Зв'язки
    designer = relationship("User", back_populates="works")
    comments = relationship("Comment", back_populates="work", cascade="all, delete-orphan")
    categories = relationship("Category", secondary=work_category_association, back_populates="works")
    tags = relationship("Tag", secondary=work_tag_association, back_populates="works")

class Category(Base):
    __tablename__ = "Category"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    
    works = relationship("Work", secondary=work_category_association, back_populates="categories")

class Tag(Base):
    __tablename__ = "Tag"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)

    works = relationship("Work", secondary=work_tag_association, back_populates="tags")

class Comment(Base):
    __tablename__ = "Comment"
    id = Column(Integer, primary_key=True, index=True)
    author_id = Column(Integer, ForeignKey("User.id"), nullable=False)
    work_id = Column(Integer, ForeignKey("Work.id"), nullable=False)
    rating_score = Column(Integer)
    comment_text = Column(Text, nullable=False)
    review_date = Column(DateTime(timezone=True), default=datetime.datetime.utcnow)

    # Зв'язки
    author = relationship("User", back_populates="comments", foreign_keys=[author_id])
    work = relationship("Work", back_populates="comments")

