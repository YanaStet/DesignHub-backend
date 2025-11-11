from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import crud, models, schemas, security
from typing import List
from database import get_db

router = APIRouter(
    prefix="/profiles",
    tags=["Designer Profiles"]
)

@router.get("/me", response_model=schemas.DesignerProfile)
def get_my_profile(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(security.get_current_user)
):
    """
    Отримує профіль поточного автентифікованого користувача.
    """
    profile = crud.get_designer_profile(db, user_id=current_user.id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Профіль ще не створено. Створіть його за допомогою PUT-запиту."
        )
    return profile

@router.put("/me", response_model=schemas.DesignerProfile)
def create_or_update_my_profile(
    profile_data: schemas.DesignerProfileCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(security.get_current_user)
):
    """
    Створює (якщо не існує) або оновлює (якщо існує)
    профіль поточного автентифікованого користувача.
    """
    # Переконуємося, що профіль створює/редагує лише дизайнер
    if current_user.role.value != 'designer':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Тільки дизайнери можуть мати профіль."
        )
        
    profile = crud.upsert_designer_profile(db, user_id=current_user.id, profile_data=profile_data)
    return profile

@router.get("/{user_id}", response_model=schemas.DesignerProfile)
def get_public_profile(user_id: int, db: Session = Depends(get_db)):
    """
    Отримує публічний профіль дизайнера за його ID користувача.
    """
    profile = crud.get_designer_profile(db, user_id=user_id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Профіль дизайнера не знайдено."
        )
    return profile