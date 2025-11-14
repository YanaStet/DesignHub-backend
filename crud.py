# --- ОНОВЛЕНО: Додано 'subqueryload' для ефективного завантаження коментарів ---
from sqlalchemy.orm import Session, joinedload, subqueryload
from typing import List, Optional
from sqlalchemy import func # --- ОНОВЛЕНО: Додано 'func' для AVG

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
    """Створює нового користувача з хешованим паролем."""
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
    
    # --- НОВЕ: Автоматично створюємо порожній профіль для дизайнера ---
    # Це гарантує, що у профіля завжди буде куди записати рейтинг
    if db_user.role == models.UserRole.designer:
        # Перевіряємо, чи раптом профіль не створився каскадом (хоча uselist=False мав би)
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
    Отримує одну роботу за ID з усіма пов'язаними даними:
    дизайнер, категорії, теги, коментарі та автори коментарів.
    """
    return (
        db.query(models.Work)
        .options(
            joinedload(models.Work.designer),
            joinedload(models.Work.categories),
            joinedload(models.Work.tags),
            # --- ОНОВЛЕНО: Ефективно завантажуємо коментарі та їх авторів ---
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
    tags_names: Optional[List[str]] = None
):
    """
    Отримує список робіт з фільтрацією та пагінацією.
    Також завантажує пов'язані дані.
    """
    query = db.query(models.Work).options(
        joinedload(models.Work.designer),
        joinedload(models.Work.categories),
        joinedload(models.Work.tags),
        # --- ОНОВЛЕНО: Завантажуємо коментарі та їх авторів ---
        subqueryload(models.Work.comments).joinedload(models.Comment.author)
    )

    if categories_ids:
        # Переконуємось, що ми фільтруємо роботи, які мають *хоча б одну* з категорій
        query = query.join(models.WorkCategory).filter(
            models.WorkCategory.c.category_id.in_(categories_ids)
        )
    if tags_names:
        # Аналогічно для тегів
        query = query.join(models.WorkTag).join(models.Tag).filter(
            models.Tag.name.in_(tags_names)
        )

    works = (
        query.order_by(models.Work.upload_date.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    # --- ОНОВЛЕНО: Використовуємо set для уникнення дублікатів через JOIN ---
    return list(dict.fromkeys(works))


def get_works_by_designer(db: Session, designer_id: int, skip: int = 0, limit: int = 20):
    """Отримує список робіт конкретного дизайнера."""
    return (
        db.query(models.Work)
        .options(
            joinedload(models.Work.designer),
            joinedload(models.Work.categories),
            joinedload(models.Work.tags),
            # --- ОНОВЛЕНО: Завантажуємо коментарі та їх авторів ---
            subqueryload(models.Work.comments).joinedload(models.Comment.author)
        )
        .filter(models.Work.designer_id == designer_id)
        .order_by(models.Work.upload_date.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

def create_work(db: Session, work: schemas.WorkCreate, designer_id: int):
    """Створює нову роботу."""
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
    db.refresh(db_work)
    # Повертаємо повний об'єкт роботи з усіма зв'язками
    return get_work(db, work_id=db_work.id)

def delete_work(db: Session, work_id: int):
    """Видаляє роботу за ID."""
    db_work = db.query(models.Work).filter(models.Work.id == work_id).first()
    if db_work:
        # --- НОВЕ: Потрібно оновити рейтинг дизайнера ПІСЛЯ видалення роботи ---
        # Отримуємо ID дизайнера до того, як видалити роботу
        designer_id = db_work.designer_id
        
        db.delete(db_work)
        db.commit()
        
        # Запускаємо перерахунок рейтингу
        _recalculate_designer_rating(db, designer_id=designer_id)
        
    return db_work

# === Функції для Профілю Дизайнера (Designer_Profile) ===

def get_designer_profile(db: Session, user_id: int):
    """Отримує профіль дизайнера за ID користувача."""
    return db.query(models.Designer_Profile).filter(models.Designer_Profile.designer_id == user_id).first()

def upsert_designer_profile(db: Session, user_id: int, profile_data: schemas.DesignerProfileCreate):
    """
    Оновлює профіль дизайнера, якщо він існує, або створює новий.
    'upsert' = update + insert
    """
    db_profile = get_designer_profile(db, user_id=user_id)
    
    if db_profile:
        # Оновлення існуючого
        update_data = profile_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_profile, key, value)
    else:
        # Створення нового
        db_profile = models.Designer_Profile(
            **profile_data.model_dump(),
            designer_id=user_id
            # Рейтинг, views, work_amount мають default у моделі
        )
        db.add(db_profile)
        
    db.commit()
    db.refresh(db_profile)
    return db_profile

# === НОВЕ: Функції для Рейтингу (інтегровані в Коментарі) ===

def _recalculate_designer_rating(db: Session, designer_id: int):
    """
    (Внутрішня функція)
    Перераховує середній рейтинг для профілю дизайнера на основі
    усіх оцінок (`rating_score`) у всіх коментарях до всіх його робіт.
    """
    
    # 1. Розраховуємо новий середній рейтинг
    # SELECT AVG(Comment.rating_score) 
    # FROM Comment 
    # JOIN Work ON Work.id = Comment.work_id
    # WHERE Work.designer_id = :designer_id AND Comment.rating_score IS NOT NULL
    new_rating_avg = (
        db.query(func.avg(models.Comment.rating_score))
        .join(models.Work, models.Work.id == models.Comment.work_id)
        .filter(models.Work.designer_id == designer_id)
        .filter(models.Comment.rating_score.isnot(None)) # Враховуємо лише коментарі з оцінкою
        .scalar()
    )
    
    # Якщо оцінок немає, scalar() поверне None. Замінюємо на 0.0
    new_rating = new_rating_avg if new_rating_avg is not None else 0.0
    
    # 2. Оновлюємо профіль дизайнера
    # Використовуємо get_designer_profile, який у нас вже є
    db_profile = get_designer_profile(db, user_id=designer_id)
    
    if db_profile:
        db_profile.rating = new_rating
        db.commit()
        db.refresh(db_profile)
    else:
        # Це спрацює, якщо профіль раптом не був створений при реєстрації
        # (хоча функція create_user тепер це обробляє)
        db_profile = models.Designer_Profile(
            designer_id=designer_id,
            rating=new_rating
        )
        db.add(db_profile)
        db.commit()
        db.refresh(db_profile)
        
    return db_profile

# === НОВЕ: Функції для Коментарів (Comment) ===

def get_comment(db: Session, comment_id: int):
    """Отримує один коментар за ID, одразу завантажуючи автора та роботу."""
    return (
        db.query(models.Comment)
        .options(
            joinedload(models.Comment.author),
            joinedload(models.Comment.work) # Завантажуємо роботу для доступу до designer_id
        ) 
        .filter(models.Comment.id == comment_id)
        .first()
    )

def get_comments_by_work(db: Session, work_id: int, skip: int = 0, limit: int = 100):
    """Отримує список коментарів для роботи (з пагінацією), завантажуючи авторів."""
    return (
        db.query(models.Comment)
        .options(joinedload(models.Comment.author)) # Завантажуємо автора для кожного коментаря
        .filter(models.Comment.work_id == work_id)
        .order_by(models.Comment.review_date.desc()) # Свіжіші спочатку
        .offset(skip)
        .limit(limit)
        .all()
    )

def create_comment(db: Session, comment: schemas.CommentCreate, author_id: int):
    """Створює новий коментар та оновлює рейтинг дизайнера, якщо є оцінка."""
    
    # 1. Отримуємо ID дизайнера (власника роботи)
    # Це потрібно, щоб знати, чий рейтинг оновлювати.
    # Ваш `comments.py` вже перевіряє, чи існує робота, тому get_work тут безпечний.
    db_work = get_work(db, work_id=comment.work_id)
    if not db_work:
        # Ця перевірка тут про всяк випадок, хоча роутер вже це робить
        return None 
        
    designer_id = db_work.designer_id
    
    # 2. Створюємо коментар
    db_comment = models.Comment(
        comment_text=comment.comment_text,
        rating_score=comment.rating_score,
        work_id=comment.work_id,
        author_id=author_id
    )
    db.add(db_comment)
    db.commit()
    
    # 3. 🔥 Оновлюємо рейтинг, якщо оцінка була надана
    if db_comment.rating_score is not None:
        _recalculate_designer_rating(db, designer_id=designer_id)
    
    db.refresh(db_comment)
    # Повертаємо повний об'єкт коментаря з автором
    return get_comment(db, comment_id=db_comment.id)

def update_comment(db: Session, comment_id: int, comment_data: schemas.CommentUpdate):
    """Оновлює коментар та оновлює рейтинг, якщо оцінка змінилася."""
    
    db_comment = get_comment(db, comment_id=comment_id)
    if not db_comment:
        return None
        
    # Зберігаємо стару оцінку, щоб перевірити, чи потрібне оновлення рейтингу
    old_rating = db_comment.rating_score
    designer_id = db_comment.work.designer_id # Робота вже завантажена через get_comment

    # Оновлюємо дані з Pydantic моделі
    update_data = comment_data.model_dump(exclude_unset=True)
    rating_changed = 'rating_score' in update_data and update_data['rating_score'] != old_rating
    
    for key, value in update_data.items():
        setattr(db_comment, key, value)
        
    db.commit()
    
    # 3. 🔥 Оновлюємо рейтинг, якщо оцінка була змінена, додана або видалена
    if rating_changed:
        _recalculate_designer_rating(db, designer_id=designer_id)
        
    db.refresh(db_comment)
    return db_comment

def delete_comment(db: Session, comment_id: int):
    """Видаляє коментар та оновлює рейтинг, якщо у коментаря була оцінка."""
    
    db_comment = get_comment(db, comment_id=comment_id)
    if not db_comment:
        return None

    # Зберігаємо дані до видалення
    rating_existed = db_comment.rating_score is not None
    designer_id = db_comment.work.designer_id

    # Видаляємо коментар
    db.delete(db_comment)
    db.commit()
    
    # 3. 🔥 Оновлюємо рейтинг, якщо видалений коментар мав оцінку
    if rating_existed:
        _recalculate_designer_rating(db, designer_id=designer_id)
        
    return db_comment # Повертаємо об'єкт, який ще є в пам'яті