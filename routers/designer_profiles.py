from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
import shutil
import os
import uuid  # Для генерації унікальних імен файлів

import crud, models, schemas, security
from database import get_db

router = APIRouter(
    tags=["Designer Profiles"]
)

# === ОТРИМАННЯ СВОГО ПРОФІЛЮ ===
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
        # У новій логіці це малоймовірно, бо профіль створюється при реєстрації,
        # але перевірка не завадить.
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Профіль дизайнера не знайдено."
        )
    return profile

# === ОНОВЛЕННЯ СВОГО ПРОФІЛЮ (ТЕКСТОВІ ДАНІ) ===
@router.put("/me", response_model=schemas.DesignerProfile)
def update_my_profile(
    profile_data: schemas.DesignerProfileUpdate, # <--- Використовуємо нову схему Update
    db: Session = Depends(get_db),
    current_user: models.User = Depends(security.get_current_user)
):
    """
    Оновлює текстові дані профілю (bio, specialization, experience).
    """
    if current_user.role != models.UserRole.designer: # Перевірка через Enum
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Тільки дизайнери можуть мати профіль."
        )
        
    # Викликаємо оновлену функцію crud
    profile = crud.update_designer_profile(db, user_id=current_user.id, profile_data=profile_data)
    
    if not profile:
        raise HTTPException(status_code=404, detail="Профіль не знайдено")
        
    return profile

# === ЗАВАНТАЖЕННЯ ШАПКИ ПРОФІЛЮ (КАРТИНКА) ===
@router.post("/me/header-image", response_model=schemas.DesignerProfile)
async def upload_header_image(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(security.get_current_user)
):
    """
    Завантажує зображення для шапки профілю.
    Приймає файл, зберігає його в static/images та оновлює URL в базі.
    """
    if current_user.role != models.UserRole.designer:
        raise HTTPException(status_code=403, detail="Тільки дизайнери можуть завантажувати шапку профілю.")

    # 1. Перевірка типу файлу (проста)
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Файл має бути зображенням (jpeg, png, etc.)")

    # 2. Підготовка директорії
    upload_dir = "static/images"
    os.makedirs(upload_dir, exist_ok=True) # Створить папку, якщо її немає

    # 3. Генерація унікального імені файлу
    # Використовуємо UUID, щоб уникнути конфліктів імен і проблем з кешуванням
    file_extension = file.filename.split(".")[-1]
    unique_filename = f"header_{current_user.id}_{uuid.uuid4()}.{file_extension}"
    file_path = os.path.join(upload_dir, unique_filename)

    # 4. Збереження файлу
    try:
        with open(file_path, "wb+") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Помилка при збереженні файлу: {str(e)}")

    # 5. Формування URL для доступу з браузера
    # Зверніть увагу: ми використовуємо прямий слеш /, навіть на Windows, бо це URL
    image_url = f"/static/images/{unique_filename}"

    # 6. Оновлення запису в БД
    updated_profile = crud.update_designer_header_image(db, user_id=current_user.id, image_path=image_url)
    
    return updated_profile

# === ОТРИМАННЯ ПУБЛІЧНОГО ПРОФІЛЮ ===
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

@router.post("/me/avatar", response_model=schemas.DesignerProfile)
async def upload_avatar(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(security.get_current_user)
):
    """
    Завантажує аватарку профілю.
    """
    if current_user.role != models.UserRole.designer:
        raise HTTPException(status_code=403, detail="Тільки дизайнери можуть завантажувати аватар.")

    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Файл має бути зображенням.")

    upload_dir = "static/images"
    os.makedirs(upload_dir, exist_ok=True)

    # Змінюємо префікс файлу на avatar_
    file_extension = file.filename.split(".")[-1]
    unique_filename = f"avatar_{current_user.id}_{uuid.uuid4()}.{file_extension}"
    file_path = os.path.join(upload_dir, unique_filename)

    try:
        with open(file_path, "wb+") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Помилка: {str(e)}")

    image_url = f"/static/images/{unique_filename}"

    # Викликаємо функцію для аватарки
    updated_profile = crud.update_designer_avatar(db, user_id=current_user.id, image_path=image_url)
    
    return updated_profile