from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import crud, models, schemas, security # Імпортуємо security
from database import SessionLocal
from database import get_db

router = APIRouter(
    # prefix="/users",
    tags=["users"],
)

# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

@router.post("/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db, user=user)

@router.get("/", response_model=list[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users

# --- НОВИЙ ЗАХИЩЕНИЙ ЕНДПОІНТ ---
@router.get("/me", response_model=schemas.User)
def read_users_me(
    current_user: models.User = Depends(security.get_current_user)
):
    """
    Отримує дані поточного залогіненого користувача.
    Запит до цього ендпоінту вимагатиме валідного 'Authorization: Bearer <token>' хедера.
    """
    return current_user

# (Можете залишити /users/{user_id}, але /me є більш поширеним)
@router.get("/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

