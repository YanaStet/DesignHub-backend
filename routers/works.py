from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import crud, models, schemas, security
from typing import List
from database import get_db

router = APIRouter()

# === Ендпоінт для отримання списку робіт ===
@router.get("/", response_model=List[schemas.Work])
def read_works(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
# ... (весь існуючий код для read_works) ...
    """
    Отримує список робіт з пагінацією.
    """
    works = crud.get_works(db, skip=skip, limit=limit)
    return works

# === Ендпоінт для отримання однієї роботи ===
@router.get("/{work_id}", response_model=schemas.Work)
def read_work(work_id: int, db: Session = Depends(get_db)):
# ... (весь існуючий код для read_work) ...
    """
    Отримує одну роботу за її ID.
    """
    db_work = crud.get_work(db, work_id=work_id)
    if db_work is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Work not found"
        )
    return db_work

# === Ендпоінт для створення роботи ===
@router.post("/", response_model=schemas.Work, status_code=status.HTTP_201_CREATED)
def create_work(
# ... (весь існуючий код для create_work) ...
    work: schemas.WorkCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(security.get_current_user)
):
    """
    Створює нову роботу для поточного автентифікованого користувача.
    """
    # Перевіряємо, чи користувач є дизайнером або адміном
    if current_user.role.value not in ['designer', 'admin']:
         raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only designers or admins can create works"
        )
        
    return crud.create_work(db=db, work=work, designer_id=current_user.id)

# === НОВИЙ ЕНДПОІНТ ДЛЯ ВИДАЛЕННЯ РОБОТИ ===
@router.delete("/{work_id}", response_model=schemas.Work)
def delete_work(
    work_id: int, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(security.get_current_user)
):
    """
    Видаляє роботу.
    Дозволено лише якщо:
    1. Ви адміністратор (`role == 'admin'`).
    2. Ви є автором цієї роботи.
    """
    db_work = crud.get_work(db, work_id=work_id)
    if db_work is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Work not found"
        )

    # Перевірка прав доступу
    if current_user.role.value != 'admin' and db_work.designer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this work"
        )
    
    deleted_work = crud.delete_work(db, work_id=work_id)
    return deleted_work