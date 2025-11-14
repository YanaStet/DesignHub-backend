from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import crud, models, schemas, security
from typing import List, Optional
from database import get_db

router = APIRouter(
    prefix="/comments",
    tags=["Comments"]
)

# === Ендпоінт для СТВОРЕННЯ коментаря ===
@router.post("/", response_model=schemas.Comment, status_code=status.HTTP_201_CREATED)
def create_comment(
    comment: schemas.CommentCreate, 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(security.get_current_user)
):
    """
    Створює новий коментар.
    Доступно лише для автентифікованих користувачів.
    Автор коментаря (`author_id`) автоматично прив'язується до `current_user`.
    """
    # Перевіряємо, чи існує робота, яку коментують
    db_work = crud.get_work(db, work_id=comment.work_id)
    if not db_work:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Роботу з id {comment.work_id} не знайдено."
        )
        
    return crud.create_comment(db=db, comment=comment, author_id=current_user.id)

# === Ендпоінт для ЧИТАННЯ коментарів (для роботи) ===
@router.get("/by-work/{work_id}", response_model=List[schemas.Comment])
def read_comments_for_work(
    work_id: int,
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    """
    Отримує список коментарів для конкретної роботи.
    Це публічний ендпоінт.
    """
    # Перевіряємо, чи існує робота
    db_work = crud.get_work(db, work_id=work_id)
    if not db_work:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Роботу з id {work_id} не знайдено."
        )
        
    comments = crud.get_comments_by_work(db, work_id=work_id, skip=skip, limit=limit)
    return comments

# === Ендпоінт для РЕДАГУВАННЯ коментаря ===
@router.put("/{comment_id}", response_model=schemas.Comment)
def update_comment(
    comment_id: int,
    comment_data: schemas.CommentUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(security.get_current_user)
):
    """
    Оновлює коментар.
    Доступно лише автору коментаря.
    """
    db_comment = crud.get_comment(db, comment_id=comment_id)
    
    if not db_comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Коментар не знайдено."
        )
        
    # Перевірка: чи є поточний користувач автором коментаря
    if db_comment.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Ви не можете редагувати чужі коментарі."
        )
        
    return crud.update_comment(db=db, comment_id=comment_id, comment_data=comment_data)

# === Ендпоінт для ВИДАЛЕННЯ коментаря ===
@router.delete("/{comment_id}", response_model=schemas.Comment)
def delete_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(security.get_current_user)
):
    """
    Видаляє коментар.
    Доступно лише автору коментаря, адміністратору або модератору.
    """
    db_comment = crud.get_comment(db, comment_id=comment_id)
    
    if not db_comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Коментар не знайдено."
        )
        
    # Перевірка прав доступу
    is_author = db_comment.author_id == current_user.id
    is_privileged = current_user.role.value in ('admin', 'moderator')
    
    if not is_author and not is_privileged:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Ви не маєте прав для видалення цього коментаря."
        )
        
    deleted_comment = crud.delete_comment(db, comment_id=comment_id)
    return deleted_comment