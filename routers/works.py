from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import crud, models, schemas, security
from typing import List
from database import get_db

router = APIRouter(
    # prefix="/works",
    tags=["works"],
)

# def get_db():
#     db = security.get_db()
#     try:
#         yield db
#     finally:
#         db.close()

@router.get("/", response_model=List[schemas.Work])
def read_works(
    skip: int = 0, 
    limit: int = 20, 
    db: Session = Depends(get_db)
):
    """
    Отримати список робіт.
    """
    works = crud.get_works(db, skip=skip, limit=limit)
    return works

@router.get("/{work_id}", response_model=schemas.Work)
def read_work(work_id: int, db: Session = Depends(get_db)):
    """
    Отримати одну роботу за її ID.
    """
    db_work = crud.get_work(db, work_id=work_id)
    if db_work is None:
        raise HTTPException(status_code=404, detail="Work not found")
    
    # (Опційно) Тут можна додати логіку підрахунку переглядів
    # db_work.views_count += 1
    # db.commit()
    
    return db_work

@router.post("/", response_model=schemas.Work, status_code=status.HTTP_201_CREATED)
def create_work(
    work: schemas.WorkCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(security.get_current_user)
):
    """
    Створити нову роботу.
    Цей ендпоінт вимагає автентифікації.
    Автор роботи автоматично встановлюється як поточний залогінений користувач.
    """
    
    # (Опційно) Перевірка, чи користувач є дизайнером
    # if current_user.role != 'designer':
    #     raise HTTPException(status_code=403, detail="Only designers can post works")
        
    return crud.create_work(db=db, work=work, designer_id=current_user.id)

