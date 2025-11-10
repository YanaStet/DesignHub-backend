from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import crud, models, schemas, security
from typing import List
from database import get_db

router = APIRouter()

# === Ендпоінт для створення (реєстрації) користувача ===
@router.post("/", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Створює нового користувача в системі.
    """
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Email already registered"
        )
    
    # Pydantic вже провалідував, що 'role' є одним із значень Enum
    return crud.create_user(db=db, user=user)


# === Ендпоінт для отримання списку користувачів ===
@router.get("/", response_model=List[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Отримує список користувачів.
    (В майбутньому цей ендпоінт варто захистити,
    щоб його могли бачити лише адміністратори)
    """
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


# === Ендпоінт для отримання інформації про себе ===
@router.get("/me", response_model=schemas.User)
def read_users_me(current_user: models.User = Depends(security.get_current_user)):
    """
    Отримує профіль поточного автентифікованого користувача.
    """
    return current_user


# === Ендпоінт для отримання користувача за ID ===
@router.get("/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    """
    Отримує профіль користувача за його ID.
    """
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="User not found"
        )
    return db_user

# === НОВИЙ ЕНДПОІНТ ДЛЯ ВИДАЛЕННЯ ===
@router.delete("/{user_id}", response_model=schemas.User)
def delete_user(
    user_id: int, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(security.get_current_user)
):
    """
    Видаляє користувача.
    Дозволено лише якщо:
    1. Ви адміністратор (`role == 'admin'`).
    2. Ви видаляєте свій власний акаунт.
    """
    # Перевірка прав доступу
    # Використовуємо .value, оскільки current_user.role є Enum
    if current_user.role.value != 'admin' and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this user"
        )

    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="User not found"
        )
    
    deleted_user = crud.delete_user(db, user_id=user_id)
    return deleted_user