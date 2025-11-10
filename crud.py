from sqlalchemy.orm import Session, joinedload
import models, schemas, security

# --- User CRUD ---
# (Весь існуючий код для get_user, get_user_by_email, get_users, create_user, authenticate_user залишається тут)
def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate):
    # Обрізаємо пароль перед хешуванням
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
    return db_user

def authenticate_user(db: Session, email: str, password: str):
    user = get_user_by_email(db, email)
    if not user:
        return False
    if not security.verify_password(password, user.password_hash):
        return False
    return user

# --- Tag CRUD ---
def get_tag_by_name(db: Session, name: str):
    return db.query(models.Tag).filter(models.Tag.name == name).first()

def create_tag(db: Session, tag: schemas.TagCreate):
    db_tag = models.Tag(**tag.model_dump())
    db.add(db_tag)
    db.commit()
    db.refresh(db_tag)
    return db_tag

def get_tags(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Tag).offset(skip).limit(limit).all()

# --- Category CRUD ---
def get_category(db: Session, category_id: int):
    return db.query(models.Category).filter(models.Category.id == category_id).first()

def get_categories(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Category).offset(skip).limit(limit).all()

def create_category(db: Session, category: schemas.CategoryCreate):
    db_category = models.Category(**category.model_dump())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

# --- Work CRUD ---
def get_work(db: Session, work_id: int):
    # Використовуємо joinedload для ефективного завантаження пов'язаних даних
    return db.query(models.Work).options(
        joinedload(models.Work.designer),
        joinedload(models.Work.categories),
        joinedload(models.Work.tags)
    ).filter(models.Work.id == work_id).first()

def get_works(db: Session, skip: int = 0, limit: int = 20):
    return db.query(models.Work).options(
        joinedload(models.Work.designer),
        joinedload(models.Work.categories),
        joinedload(models.Work.tags)
    ).offset(skip).limit(limit).all()

def create_work(db: Session, work: schemas.WorkCreate, designer_id: int):
    # === ОСЬ ЗМІНА ===
    # Тепер ми також передаємо image_url при створенні
    db_work = models.Work(
        title=work.title,
        description=work.description,
        image_url=work.image_url,  # <--- ДОДАНО
        designer_id=designer_id
    )
    
    # Додаємо категорії
    if work.categories_ids:
        db_categories = db.query(models.Category).filter(models.Category.id.in_(work.categories_ids)).all()
        db_work.categories = db_categories
        
    # Додаємо теги (створюємо, якщо їх немає)
    if work.tags_names:
        db_tags = []
        for tag_name in work.tags_names:
            tag = get_tag_by_name(db, name=tag_name)
            if not tag:
                # Якщо тега не існує, створюємо його
                tag_schema = schemas.TagCreate(name=tag_name)
                tag = create_tag(db, tag_schema) # Використовуємо функцію
            db_tags.append(tag)
        db_work.tags = db_tags

    db.add(db_work)
    db.commit()
    db.refresh(db_work)
    return db_work