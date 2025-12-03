# crud.py
from sqlalchemy.orm import Session, joinedload, subqueryload
from typing import List, Optional, Union
from sqlalchemy import func

import models, schemas, security

# === Функції для Користувача (User) ===

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
    """Створює нового користувача з хешованим паролем та порожнім профілем."""
    hashed_password = security.get_password_hash(user.password)
    
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
    
    # Автоматично створюємо порожній профіль для дизайнера
    if db_user.role == models.UserRole.designer:
        if not db_user.designer_profile:
            db_profile = models.Designer_Profile(designer_id=db_user.id)
            db.add(db_profile)
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
    """Перевіряє email та пароль користувача."""
    user = get_user_by_email(db, email=email)
    if not user:
        return False
    if not security.verify_password(password, user.password_hash):
        return False
    return user

# === Функції для Категорій (Category) ===

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

# === Функції для Тегів (Tag) ===

def get_tag(db: Session, tag_id: int):
    return db.query(models.Tag).filter(models.Tag.id == tag_id).first()

def get_tag_by_name(db: Session, name: str):
    return db.query(models.Tag).filter(models.Tag.name == name).first()

def get_tags(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Tag).offset(skip).limit(limit).all()

def create_tag_or_get(db: Session, tag_name: str) -> models.Tag:
    """Створює тег, якщо він не існує, або повертає існуючий."""
    db_tag = get_tag_by_name(db, name=tag_name)
    if db_tag:
        return db_tag
    db_tag = models.Tag(name=tag_name)
    db.add(db_tag)
    db.commit()
    db.refresh(db_tag)
    return db_tag

# === Функції для Робіт (Work) ===

def get_work(db: Session, work_id: int):
    """
    Отримує одну роботу за ID з усіма пов'язаними даними.
    """
    return (
        db.query(models.Work)
        .options(
            joinedload(models.Work.designer),
            joinedload(models.Work.categories),
            joinedload(models.Work.tags),
            subqueryload(models.Work.comments).joinedload(models.Comment.author)
        )
        .filter(models.Work.id == work_id)
        .first()
    )

def get_works(
    db: Session,
    skip: int = 0,
    limit: int = 20,
    categories_ids: Optional[List[int]] = None,
    tags_names: Optional[List[str]] = None,
    search_query: Optional[str] = None 
):
    """Отримує список робіт з фільтрацією, пошуком та пагінацією."""
    query = db.query(models.Work).options(
        joinedload(models.Work.designer),
        joinedload(models.Work.categories),
        joinedload(models.Work.tags),
        subqueryload(models.Work.comments).joinedload(models.Comment.author)
    )

    if categories_ids:
        query = query.join(models.WorkCategory).filter(
            models.WorkCategory.c.category_id.in_(categories_ids)
        )
    if tags_names:
        query = query.join(models.WorkTag).join(models.Tag).filter(
            models.Tag.name.in_(tags_names)
        )
        
    if search_query:
        search_pattern = f"%{search_query}%"
        query = query.filter(
            models.Work.title.ilike(search_pattern) | 
            models.Work.description.ilike(search_pattern)
        )

    works = (
        query.distinct() 
        .order_by(models.Work.upload_date.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return works


def get_works_by_designer(db: Session, designer_id: int, skip: int = 0, limit: int = 20):
    """Отримує список робіт конкретного дизайнера."""
    return (
        db.query(models.Work)
        .options(
            joinedload(models.Work.designer),
            joinedload(models.Work.categories),
            joinedload(models.Work.tags),
            subqueryload(models.Work.comments).joinedload(models.Comment.author)
        )
        .filter(models.Work.designer_id == designer_id)
        .order_by(models.Work.upload_date.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

def create_work(db: Session, work: schemas.WorkCreate, designer_id: int):
    """Створює нову роботу та збільшує лічильник робіт у профілі."""
    db_work = models.Work(
        title=work.title,
        description=work.description,
        image_url=work.image_url,
        designer_id=designer_id
    )
    if work.categories_ids:
        db_categories = db.query(models.Category).filter(
            models.Category.id.in_(work.categories_ids)
        ).all()
        db_work.categories = db_categories
    if work.tags_names:
        db_tags = []
        for tag_name in work.tags_names:
            db_tag = create_tag_or_get(db, tag_name=tag_name)
            db_tags.append(db_tag)
        db_work.tags = db_tags
        
    db.add(db_work)
    db.commit()
    
    # --- ОНОВЛЕННЯ: Збільшуємо кількість робіт у профілі ---
    db_profile = get_designer_profile(db, designer_id)
    if db_profile:
        db_profile.work_amount += 1
        db.add(db_profile)
        db.commit()
    # -----------------------------------------------------

    db.refresh(db_work)
    return get_work(db, work_id=db_work.id)

def delete_work(db: Session, work_id: int):
    """Видаляє роботу за ID та зменшує лічильник робіт."""
    db_work = db.query(models.Work).filter(models.Work.id == work_id).first()
    if db_work:
        designer_id = db_work.designer_id
        
        db.delete(db_work)
        db.commit()
        
        # --- ОНОВЛЕННЯ: Зменшуємо кількість робіт у профілі ---
        db_profile = get_designer_profile(db, designer_id)
        if db_profile and db_profile.work_amount > 0:
            db_profile.work_amount -= 1
            db.add(db_profile)
            db.commit()
        # -----------------------------------------------------

        # Запускаємо перерахунок рейтингу
        _recalculate_designer_rating(db, designer_id=designer_id)
        
    return db_work

def update_work(db: Session, db_work: models.Work, work_update: schemas.WorkUpdate):
    """
    Оновлює існуючу роботу.
    Змінює прості поля (назва, опис) та зв'язки Many-to-Many (категорії, теги).
    """
    # 1. Перетворюємо Pydantic-модель у словник, виключаючи пусті поля (None)
    update_data = work_update.model_dump(exclude_unset=True)

    # 2. Оновлення КАТЕГОРІЙ (Many-to-Many)
    # Якщо список категорій передано, ми повністю замінюємо старі категорії на нові
    if "categories_ids" in update_data:
        categories_ids = update_data.pop("categories_ids")
        # Знаходимо всі об'єкти категорій за переданими ID
        new_categories = db.query(models.Category).filter(
            models.Category.id.in_(categories_ids)
        ).all()
        # Присвоюємо список об'єктів. SQLAlchemy автоматично оновить проміжну таблицю.
        db_work.categories = new_categories

    # 3. Оновлення ТЕГІВ (Many-to-Many)
    # Аналогічно, якщо передано теги - замінюємо старий набір новим
    if "tags_names" in update_data:
        tags_names = update_data.pop("tags_names")
        new_tags = []
        for tag_name in tags_names:
            # Використовуємо твою існуючу функцію create_tag_or_get
            # щоб не дублювати теги, якщо вони вже є в базі
            tag = create_tag_or_get(db, tag_name=tag_name)
            new_tags.append(tag)
        db_work.tags = new_tags

    # 4. Оновлення простих полів (title, description, image_url)
    for key, value in update_data.items():
        setattr(db_work, key, value)

    db.add(db_work)
    db.commit()
    db.refresh(db_work)

    # Повертаємо об'єкт через get_work, щоб у відповіді 
    # точно були підвантажені всі зв'язки (автор, коментарі і т.д.)
    return get_work(db, work_id=db_work.id)

# === Функції для Профілю Дизайнера (Designer_Profile) ===

def get_designer_profile(db: Session, user_id: int):
    """Отримує профіль дизайнера за ID користувача."""
    return db.query(models.Designer_Profile).filter(models.Designer_Profile.designer_id == user_id).first()

# --- ЗМІНЕНО: Замість upsert тепер update, бо профіль створюється при реєстрації ---
def update_designer_profile(db: Session, user_id: int, profile_data: schemas.DesignerProfileUpdate):
    """
    Оновлює текстові поля профілю (bio, specialization, experience).
    """
    db_profile = get_designer_profile(db, user_id=user_id)
    
    if not db_profile:
        # Цього не мало б статися, але про всяк випадок
        return None

    # Оновлюємо тільки ті поля, що прийшли (exclude_unset=True)
    update_data = profile_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_profile, key, value)
        
    db.commit()
    db.refresh(db_profile)
    return db_profile

# --- НОВЕ: Спеціальна функція для оновлення картинки ---
def update_designer_header_image(db: Session, user_id: int, image_path: str):
    """
    Оновлює тільки шлях до шапки профілю.
    Викликається після успішного завантаження файлу.
    """
    db_profile = get_designer_profile(db, user_id)
    if db_profile:
        db_profile.header_image_url = image_path
        db.commit()
        db.refresh(db_profile)
    return db_profile

def update_designer_avatar(db: Session, user_id: int, image_path: str):
    """
    Оновлює тільки шлях до аватарки.
    """
    db_profile = get_designer_profile(db, user_id)
    if db_profile:
        db_profile.avatar_url = image_path
        db.commit()
        db.refresh(db_profile)
    return db_profile

# === Функції для Рейтингу (Внутрішні та Comments) ===

def _recalculate_designer_rating(db: Session, designer_id: int):
    """Перераховує середній рейтинг для профілю дизайнера."""
    new_rating_avg = (
        db.query(func.avg(models.Comment.rating_score))
        .join(models.Work, models.Work.id == models.Comment.work_id)
        .filter(models.Work.designer_id == designer_id)
        .filter(models.Comment.rating_score.isnot(None)) 
        .scalar()
    )
    
    new_rating = new_rating_avg if new_rating_avg is not None else 0.0
    
    db_profile = get_designer_profile(db, user_id=designer_id)
    if db_profile:
        db_profile.rating = new_rating
        db.commit()
        db.refresh(db_profile)
        
    return db_profile

# === Функції для Коментарів (Comment) ===

def get_comment(db: Session, comment_id: int):
    return (
        db.query(models.Comment)
        .options(
            joinedload(models.Comment.author),
            joinedload(models.Comment.work) 
        ) 
        .filter(models.Comment.id == comment_id)
        .first()
    )

def get_comments_by_work(db: Session, work_id: int, skip: int = 0, limit: int = 100):
    return (
        db.query(models.Comment)
        .options(joinedload(models.Comment.author))
        .filter(models.Comment.work_id == work_id)
        .order_by(models.Comment.review_date.desc()) 
        .offset(skip)
        .limit(limit)
        .all()
    )

def create_comment(db: Session, comment: schemas.CommentCreate, author_id: int):
    db_work = get_work(db, work_id=comment.work_id)
    if not db_work:
        return None 
        
    designer_id = db_work.designer_id
    
    db_comment = models.Comment(
        comment_text=comment.comment_text,
        rating_score=comment.rating_score,
        work_id=comment.work_id,
        author_id=author_id
    )
    db.add(db_comment)
    db.commit()
    
    if db_comment.rating_score is not None:
        _recalculate_designer_rating(db, designer_id=designer_id)
    
    db.refresh(db_comment)
    return get_comment(db, comment_id=db_comment.id)

def update_comment(db: Session, comment_id: int, comment_data: schemas.CommentUpdate):
    db_comment = get_comment(db, comment_id=comment_id)
    if not db_comment:
        return None
        
    old_rating = db_comment.rating_score
    designer_id = db_comment.work.designer_id 

    update_data = comment_data.model_dump(exclude_unset=True)
    rating_changed = 'rating_score' in update_data and update_data['rating_score'] != old_rating
    
    for key, value in update_data.items():
        setattr(db_comment, key, value)
        
    db.commit()
    
    if rating_changed:
        _recalculate_designer_rating(db, designer_id=designer_id)
        
    db.refresh(db_comment)
    return db_comment

def delete_comment(db: Session, comment_id: int):
    db_comment = get_comment(db, comment_id=comment_id)
    if not db_comment:
        return None

    rating_existed = db_comment.rating_score is not None
    designer_id = db_comment.work.designer_id

    db.delete(db_comment)
    db.commit()
    
    if rating_existed:
        _recalculate_designer_rating(db, designer_id=designer_id)
        
    return db_comment

def register_work_view(db: Session, work_id: int, user_id: int):
    """
    Реєструє перегляд роботи користувачем.
    """
    existing_view = db.query(models.WorkView).filter(
        models.WorkView.work_id == work_id,
        models.WorkView.user_id == user_id
    ).first()
    
    if existing_view:
        return False

    new_view = models.WorkView(work_id=work_id, user_id=user_id)
    db.add(new_view)
    
    db_work = db.query(models.Work).filter(models.Work.id == work_id).first()
    if db_work:
        db_work.views_count += 1
        
        designer_profile = db.query(models.Designer_Profile).filter(
            models.Designer_Profile.designer_id == db_work.designer_id
        ).first()
        
        if designer_profile:
            designer_profile.views_count += 1
    
    db.commit()
    return True