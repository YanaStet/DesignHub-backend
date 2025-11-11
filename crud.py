from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
import models, schemas, security
from typing import List

# === CRUD для Користувачів ===
# ... (весь існуючий код для get_user, get_user_by_email, get_users, create_user, delete_user, authenticate_user) ...
def get_user(db: Session, user_id: int):
    """Отримує одного користувача за ID."""
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    """Отримує одного користувача за email."""
    return db.query(models.User).filter(models.User.email == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    """Отримує список користувачів з пагінацією."""
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate):
    """Створює нового користувача."""
    
    # Використовуємо функцію з security.py для хешування
    # Вона вже містить виправлення для довжини пароля
    hashed_password = security.get_password_hash(user.password)
    
    # Створюємо об'єкт моделі User
    # `user.role` вже буде об'єктом Enum завдяки Pydantic
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

def delete_user(db: Session, user_id: int):
    """Видаляє користувача за ID."""
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user:
        db.delete(db_user)
        db.commit()
    return db_user

def authenticate_user(db: Session, email: str, password: str):
    """
    Перевіряє email та пароль користувача.
    Повертає об'єкт User у разі успіху, інакше None.
    """
    user = get_user_by_email(db, email=email)
    if not user:
        return None
    if not security.verify_password(password, user.password_hash):
        return None
    return user

# === CRUD для Категорій ===
# ... (весь існуючий код для get_categories, create_category, get_category_by_name) ...
def get_categories(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Category).offset(skip).limit(limit).all()

def create_category(db: Session, category: schemas.CategoryCreate):
    db_category = models.Category(name=category.name)
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

def get_category_by_name(db: Session, name: str):
    return db.query(models.Category).filter(models.Category.name == name).first()

# === CRUD для Тегів ===
# ... (весь існуючий код для get_tags, get_tag_by_name, create_tag) ...
def get_tags(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Tag).offset(skip).limit(limit).all()

def get_tag_by_name(db: Session, name: str):
    return db.query(models.Tag).filter(func.lower(models.Tag.name) == func.lower(name)).first()

def create_tag(db: Session, tag: schemas.TagCreate):
    db_tag = models.Tag(name=tag.name)
    db.add(db_tag)
    db.commit()
    db.refresh(db_tag)
    return db_tag

# === CRUD для Робіт ===
# ... (весь існуючий код для get_works, get_work, create_work, delete_work) ...
def get_works(db: Session, skip: int = 0, limit: int = 100):
    """
    Отримує список робіт, одразу підтягуючи пов'язані дані
    (дизайнера, категорії, теги) для уникнення N+1 запитів.
    """
    return (
        db.query(models.Work)
        .options(
            joinedload(models.Work.designer),
            joinedload(models.Work.categories),
            joinedload(models.Work.tags)
        )
        .offset(skip)
        .limit(limit)
        .all()
    )

def get_work(db: Session, work_id: int):
    """Отримує одну роботу за ID, одразу підтягуючи пов'язані дані."""
    return (
        db.query(models.Work)
        .options(
            joinedload(models.Work.designer),
            joinedload(models.Work.categories),
            joinedload(models.Work.tags)
        )
        .filter(models.Work.id == work_id)
        .first()
    )

def create_work(db: Session, work: schemas.WorkCreate, designer_id: int):
    """Створює нову роботу, пов'язуючи її з категоріями та тегами."""
    
    # 1. Створюємо основний об'єкт роботи
    db_work = models.Work(
        title=work.title,
        description=work.description,
        image_url=work.image_url, # <--- Зберігаємо URL картинки
        designer_id=designer_id
    )
    
    # 2. Обробляємо категорії (які передаються по ID)
    if work.categories_ids:
        db_categories = db.query(models.Category).filter(
            models.Category.id.in_(work.categories_ids)
        ).all()
        db_work.categories = db_categories

    # 3. Обробляємо теги (які передаються по іменах)
    if work.tags_names:
        tags_to_add = []
        for tag_name in work.tags_names:
            # Перевіряємо, чи існує тег (без врахування регістру)
            db_tag = get_tag_by_name(db, tag_name)
            if not db_tag:
                # Якщо тега немає, створюємо його
                db_tag = create_tag(db, schemas.TagCreate(name=tag_name))
            tags_to_add.append(db_tag)
        db_work.tags = tags_to_add

    # 4. Зберігаємо все в базі
    db.add(db_work)
    db.commit()
    db.refresh(db_work)
    return db_work

def delete_work(db: Session, work_id: int):
    """Видаляє роботу за ID."""
    db_work = db.query(models.Work).filter(models.Work.id == work_id).first()
    if db_work:
        db.delete(db_work)
        db.commit()
    return db_work

# === НОВИЙ БЛОК: CRUD для Профілю Дизайнера ===

def get_designer_profile(db: Session, user_id: int):
    """Отримує профіль дизайнера за ID користувача."""
    # Ми можемо додати .options(joinedload(models.Designer_Profile.designer))
    # але оскільки ми шукаємо по user_id, ми вже знаємо, хто дизайнер.
    return db.query(models.Designer_Profile).filter(models.Designer_Profile.designer_id == user_id).first()

def upsert_designer_profile(db: Session, user_id: int, profile_data: schemas.DesignerProfileCreate):
    """
    Оновлює профіль, якщо він існує, або створює, якщо ні (upsert).
    """
    # 1. Шукаємо існуючий профіль
    db_profile = get_designer_profile(db, user_id)
    
    # 2. Отримуємо дані з Pydantic-схеми
    # exclude_unset=True означає, що ми будемо оновлювати лише ті поля,
    # які користувач явно передав у JSON.
    update_data = profile_data.model_dump(exclude_unset=True)

    if db_profile:
        # === ОНОВЛЕННЯ (UPDATE) ===
        for key, value in update_data.items():
            setattr(db_profile, key, value)
    else:
        # === СТВОРЕННЯ (CREATE) ===
        # Перевіряємо, чи користувач, якому ми створюємо профіль, є дизайнером
        user = get_user(db, user_id)
        if not user or user.role.value != 'designer':
            # Це не має статися, якщо ендпоінт захищений, але це гарна перевірка
            return None 
            
        db_profile = models.Designer_Profile(
            **update_data,
            designer_id=user_id
        )
        db.add(db_profile)
        
    # 3. Зберігаємо зміни
    db.commit()
    db.refresh(db_profile)
    return db_profile