-- Видаляємо старі типи та таблиці
DROP TABLE IF EXISTS "Work_Category", "Work_Tag", "Comment", "Work", "Designer_Profile", "User", "Category", "Tag" CASCADE;
DROP TYPE IF EXISTS user_role_enum CASCADE;

-- === НОВЕ: Створюємо тип Enum для ролей ===
CREATE TYPE user_role_enum AS ENUM (
  'designer',
  'admin',
  'moderator'
);

-- Таблиця користувачів
CREATE TABLE "User" (
  "id" SERIAL PRIMARY KEY,
  "firstName" VARCHAR(100) NOT NULL,
  "lastName" VARCHAR(100) NOT NULL,
  "email" VARCHAR(255) UNIQUE NOT NULL,
  -- === ЗМІНЕНО: Використовуємо наш новий тип Enum ===
  "role" user_role_enum NOT NULL DEFAULT 'designer',
  "password_hash" VARCHAR(255) NOT NULL,
  "registration_date" TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Профіль дизайнера (зв'язок один-до-одного з User)
CREATE TABLE "Designer_Profile" (
  "designer_id" INTEGER PRIMARY KEY REFERENCES "User"("id") ON DELETE CASCADE,
  "specialization" VARCHAR(255),
  "bio" TEXT,
  "experience" INTEGER DEFAULT 0, -- Роки досвіду
  "rating" DECIMAL(3, 2) DEFAULT 0.00,
  "views_count" INTEGER DEFAULT 0,
  "work_amount" INTEGER DEFAULT 0
);

-- Таблиця робіт
CREATE TABLE "Work" (
  "id" SERIAL PRIMARY KEY,
  "designer_id" INTEGER NOT NULL REFERENCES "User"("id") ON DELETE CASCADE,
  "title" VARCHAR(255) NOT NULL,
  "description" TEXT,
  "upload_date" TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  "views_count" INTEGER DEFAULT 0,
  "image_url" VARCHAR(255)
);

-- Таблиця категорій
CREATE TABLE "Category" (
  "id" SERIAL PRIMARY KEY,
  "name" VARCHAR(100) UNIQUE NOT NULL
);

-- Таблиця тегів
CREATE TABLE "Tag" (
  "id" SERIAL PRIMARY KEY,
  "name" VARCHAR(100) UNIQUE NOT NULL
);

-- Таблиця коментарів
CREATE TABLE "Comment" (
  "id" SERIAL PRIMARY KEY,
  -- Змінено назви для ясності, відповідно до вашої діаграми
  "author_id" INTEGER NOT NULL REFERENCES "User"("id") ON DELETE CASCADE,
  "work_id" INTEGER NOT NULL REFERENCES "Work"("id") ON DELETE CASCADE,
  -- "receiver_id" видалено, оскільки власника роботи можна отримати через work_id
  "rating_score" INTEGER CHECK (rating_score >= 1 AND rating_score <= 5),
  "comment_text" TEXT NOT NULL,
  "review_date" TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Сполучна таблиця для зв'язку "багато-до-багатьох" між роботами та категоріями
CREATE TABLE "Work_Category" (
  "work_id" INTEGER NOT NULL REFERENCES "Work"("id") ON DELETE CASCADE,
  "category_id" INTEGER NOT NULL REFERENCES "Category"("id") ON DELETE CASCADE,
  PRIMARY KEY ("work_id", "category_id")
);

-- Сполучна таблиця для зв'язку "багато-до-багатьох" між роботами та тегами
CREATE TABLE "Work_Tag" (
  "work_id" INTEGER NOT NULL REFERENCES "Work"("id") ON DELETE CASCADE,
  "tag_id" INTEGER NOT NULL REFERENCES "Tag"("id") ON DELETE CASCADE,
  PRIMARY KEY ("work_id", "tag_id")
);

-- Індекси для прискорення пошуку за зовнішніми ключами
CREATE INDEX ON "Work" ("designer_id");
CREATE INDEX ON "Comment" ("author_id");
CREATE INDEX ON "Comment" ("work_id");