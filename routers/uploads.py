from fastapi import APIRouter, File, UploadFile, Depends, HTTPException, status
import models
import security
import shutil
import os
import uuid # Використовуємо uuid для унікальних імен

router = APIRouter(
    tags=["Uploads"]
)

# Папка для збереження завантажених зображень
STATIC_DIR = "static"
IMAGES_DIR = os.path.join(STATIC_DIR, "images")

# Переконуємося, що директорії існують при старті
os.makedirs(IMAGES_DIR, exist_ok=True)

ALLOWED_CONTENT_TYPES = ["image/jpeg", "image/png", "image/webp"]

@router.post("/upload/image/")
async def upload_image(
    file: UploadFile = File(...),
    # (Опційно) Можна вимагати автентифікацію для завантаження
    # current_user: models.User = Depends(security.get_current_user)
):
    """
    Приймає файл зображення, перевіряє його тип, зберігає на сервері
    та повертає публічний URL.
    """
    
    # 1. Перевірка типу файлу
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Непідтримуваний тип файлу: {file.content_type}. Дозволені: {', '.join(ALLOWED_CONTENT_TYPES)}"
        )
        
    # 2. Генерація унікального імені файлу
    # Використовуємо розширення оригінального файлу
    file_extension = os.path.splitext(file.filename)[1]
    # Генеруємо унікальне ім'я, щоб уникнути конфліктів
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    
    # 3. Збереження файлу
    file_path = os.path.join(IMAGES_DIR, unique_filename)
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        # Обробка помилок при збереженні файлу
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Не вдалося зберегти файл: {e}"
        )
    finally:
        file.file.close()

    # 4. Повернення публічного URL
    # Цей URL буде працювати завдяки 'app.mount("/static", ...)' у main.py
    # Важливо: URL-адреси використовують прямі слеші '/'
    public_url = f"/static/images/{unique_filename}"
    
    return {"file_url": public_url}