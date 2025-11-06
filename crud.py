from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError
import models, schemas
from security import get_password_hash, verify_password
from typing import List, Optional

# --- CRUD для Користувачів (User) ---

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        email=user.email,
        firstName=user.firstName,
        lastName=user.lastName,
        password_hash=hashed_password,
        role=user.role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, email: str, password: str) -> Optional[models.User]:
    """
    Перевіряє email та пароль користувача.
    Повертає об'єкт User у разі успіху, або None у разі невдачі.
    """
    db_user = get_user_by_email(db, email=email)
    
    # Перевіряємо, чи існує користувач і чи збігається пароль
    if not db_user or not verify_password(password, db_user.password_hash):
        return None
    
    return db_user

# --- CRUD для Категорій (Category) ---

def get_category(db: Session, category_id: int):
    return db.query(models.Category).filter(models.Category.id == category_id).first()

def get_category_by_name(db: Session, name: str):
    return db.query(models.Category).filter(models.Category.name == name).first()

def get_categories(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Category).offset(skip).limit(limit).all()

def create_category(db: Session, category: schemas.CategoryCreate):
    db_category = models.Category(name=category.name)
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

# --- CRUD для Тегів (Tag) ---

def get_tag(db: Session, tag_id: int):
    return db.query(models.Tag).filter(models.Tag.id == tag_id).first()

def get_tag_by_name(db: Session, name: str):
    return db.query(models.Tag).filter(models.Tag.name == name).first()

def get_tags(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Tag).offset(skip).limit(limit).all()

def create_tag(db: Session, tag: schemas.TagCreate):
    db_tag = models.Tag(name=tag.name)
    db.add(db_tag)
    db.commit()
    db.refresh(db_tag)
    return db_tag

def get_or_create_tags(db: Session, tag_names: List[str]) -> List[models.Tag]:
    """Допоміжна функція: знаходить теги або створює їх, якщо не існують."""
    tags = []
    for name in tag_names:
        db_tag = get_tag_by_name(db, name=name)
        if not db_tag:
            try:
                db_tag = create_tag(db, schemas.TagCreate(name=name))
            except IntegrityError: # Обробка стану гонки (race condition)
                db.rollback()
                db_tag = get_tag_by_name(db, name=name)
        tags.append(db_tag)
    return tags

# --- CRUD для Робіт (Work) ---

def get_work(db: Session, work_id: int):
    """
    Отримує одну роботу, одразу підтягуючи зв'язані дані
    (дизайнера, категорії, теги) для уникнення N+1 запитів.
    """
    return db.query(models.Work).options(
        joinedload(models.Work.designer),
        joinedload(models.Work.categories),
        joinedload(models.Work.tags)
    ).filter(models.Work.id == work_id).first()

def get_works(db: Session, skip: int = 0, limit: int = 100):
    """
    Отримує список робіт, одразу підтягуючи зв'язані дані
    (дизайнера, категорії, теги).
    """
    return db.query(models.Work).options(
        joinedload(models.Work.designer),
        joinedload(models.Work.categories),
        joinedload(models.Work.tags)
    ).order_by(models.Work.upload_date.desc()).offset(skip).limit(limit).all()

def create_work(db: Session, work: schemas.WorkCreate, designer_id: int):
    """
    Створює нову роботу, знаходячи або створюючи пов'язані
    категорії та теги.
    """
    # 1. Отримуємо об'єкти Категорій за їх ID
    db_categories = db.query(models.Category).filter(
        models.Category.id.in_(work.category_ids)
    ).all()
    
    # 2. Отримуємо або створюємо об'єкти Тегів за їх назвами
    db_tags = get_or_create_tags(db, tag_names=work.tag_names)
    
    # 3. Створюємо саму роботу
    db_work = models.Work(
        title=work.title,
        description=work.description,
        image_url=work.image_url,
        designer_id=designer_id,
        categories=db_categories, # Призначаємо зв'язки
        tags=db_tags              # Призначаємо зв'язки
    )
    
    db.add(db_work)
    db.commit()
    db.refresh(db_work)
    return db_work

