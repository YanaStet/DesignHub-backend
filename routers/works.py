from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
import crud, models, schemas, security
from typing import List, Optional
from database import get_db

router = APIRouter()

# === Ендпоінт для СТВОРЕННЯ роботи ===
@router.post("/", response_model=schemas.Work, status_code=status.HTTP_201_CREATED)
def create_work(
    work: schemas.WorkCreate, 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(security.get_current_user)
):
    """
    Створює нову роботу.
    Доступно лише для автентифікованих користувачів.
    Автор роботи автоматично прив'язується до поточного користувача.
    """
    # Ми передаємо ID поточного користувача в CRUD функцію
    return crud.create_work(db=db, work=work, designer_id=current_user.id)


# === Ендпоінт для ОТРИМАННЯ списку робіт (З ФІЛЬТРАЦІЄЮ) ===
@router.get("/", response_model=List[schemas.Work])
def read_works(
    skip: int = 0, 
    limit: int = 20, 
    db: Session = Depends(get_db),
    # === НОВИЙ ПАРАМЕТР ===
    q: Optional[str] = Query(None, description="Рядок пошуку по заголовку або опису роботи."), 
    # =====================
    categories: Optional[str] = Query(None, description="Список ID категорій через кому (напр., '1,2,3')"),
    tags: Optional[str] = Query(None, description="Список назв тегів через кому (напр., 'design,art')")
):
    """
    Отримує список робіт з пагінацією, фільтрацією та пошуком.
    """
    # ... (Конвертація categories та tags залишається без змін) ...
    categories_ids_list: Optional[List[int]] = None
    if categories:
        # ... (логіка конвертації) ...
        try:
             categories_ids_list = [int(id_str.strip()) for id_str in categories.split(',')]
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Неправильний формат ID категорій. Очікується список чисел через кому."
            )
            
    tags_names_list: Optional[List[str]] = None
    if tags:
        tags_names_list = [name.strip() for name in tags.split(',')]

    # Викликаємо оновлену CRUD-функцію
    works = crud.get_works(
        db, 
        skip=skip, 
        limit=limit, 
        categories_ids=categories_ids_list, 
        tags_names=tags_names_list,
        search_query=q # 💡 ПЕРЕДАЄМО НОВИЙ ПАРАМЕТР
    )
    return works


# === Ендпоінт: Отримання робіт за ID дизайнера (публічний) ===
@router.get("/by-designer/{designer_id}", response_model=List[schemas.Work])
def read_works_by_designer(
    designer_id: int,
    skip: int = 0, 
    limit: int = 20, 
    db: Session = Depends(get_db)
):
    """
    Отримує список робіт конкретного дизайнера.
    Це публічний ендпоінт (для профілю дизайнера).
    """
    designer = crud.get_user(db, user_id=designer_id)
    if not designer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Дизайнера з таким ID не знайдено."
        )
        
    # Використовуємо ту саму get_works, але передаємо designer_id
    works = crud.get_works_by_designer(db, designer_id=designer_id, skip=skip, limit=limit)
    return works


# === Ендпоінт для ОТРИМАННЯ однієї роботи (публічний) ===
@router.get("/{work_id}", response_model=schemas.Work)
def read_work(work_id: int, db: Session = Depends(get_db)):
    """
    Отримує одну конкретну роботу за її ID.
    Це публічний ендпоінт.
    """
    db_work = crud.get_work(db, work_id=work_id)
    if db_work is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Роботу не знайдено."
        )
    return db_work


# === Ендпоінт для ВИДАЛЕННЯ роботи (захищений) ===
@router.delete("/{work_id}", response_model=schemas.Work)
def delete_work(
    work_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(security.get_current_user)
):
    """
    Видаляє роботу.
    Доступно лише якщо:
    1. Ви адміністратор (`role == 'admin'`).
    2. Ви автор цієї роботи.
    """
    db_work = crud.get_work(db, work_id=work_id)
    
    if db_work is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Роботу не знайдено."
        )
    
    # Перевірка прав доступу
    is_admin = current_user.role.value == 'admin'
    is_author = db_work.designer_id == current_user.id
    
    if not is_admin and not is_author:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Ви не маєте прав для видалення цієї роботи."
        )
        
    deleted_work = crud.delete_work(db, work_id=work_id)
    return deleted_work