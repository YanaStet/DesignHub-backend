from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import crud, models, schemas, security
from typing import List
from database import get_db

router = APIRouter(
    # prefix="/tags",
    tags=["tags"],
)

# def get_db():
#     db = security.get_db()
#     try:
#         yield db
#     finally:
#         db.close()

@router.get("/", response_model=List[schemas.Tag])
def read_tags(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    """
    Отримати список всіх тегів.
    """
    tags = crud.get_tags(db, skip=skip, limit=limit)
    return tags

@router.post("/", response_model=schemas.Tag, status_code=status.HTTP_201_CREATED)
def create_tag(
    tag: schemas.TagCreate,
    db: Session = Depends(get_db)
    # (Опційно) Можна захистити цей ендпоінт
    # current_user: models.User = Depends(security.get_current_user)
):
    """
    Створити новий тег.
    (Примітка: в `crud.create_work` теги створюються автоматично,
    але цей ендпоінт може бути корисним для адмін-панелі)
    """
    db_tag = crud.get_tag_by_name(db, name=tag.name)
    if db_tag:
        raise HTTPException(status_code=400, detail="Tag already exists")
    return crud.create_tag(db=db, tag=tag)

