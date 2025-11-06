from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import crud, models, schemas, security
from typing import List
from database import get_db

router = APIRouter(
    # prefix="/categories",
    tags=["categories"],
)

# def get_db():
#     db = security.get_db()
#     try:
#         yield db
#     finally:
#         db.close()

@router.get("/", response_model=List[schemas.Category])
def read_categories(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    """
    Отримати список всіх категорій.
    """
    categories = crud.get_categories(db, skip=skip, limit=limit)
    return categories

@router.post("/", response_model=schemas.Category, status_code=status.HTTP_201_CREATED)
def create_category(
    category: schemas.CategoryCreate,
    db: Session = Depends(get_db)
    # (Опційно) Можна захистити цей ендпоінт,
    # щоб тільки адміни могли створювати категорії
    # current_user: models.User = Depends(security.get_current_user) 
):
    """
    Створити нову категорію.
    """
    db_category = crud.get_category_by_name(db, name=category.name)
    if db_category:
        raise HTTPException(status_code=400, detail="Category already exists")
    return crud.create_category(db=db, category=category)

