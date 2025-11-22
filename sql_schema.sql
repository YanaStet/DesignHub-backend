DROP TABLE IF EXISTS "Work_Category", "Work_Tag", "Comment", "Work", "Designer_Profile", "User", "Category", "Tag" CASCADE;
DROP TYPE IF EXISTS user_role_enum CASCADE;

CREATE TYPE user_role_enum AS ENUM (
  'designer',
  'admin',
  'moderator'
);

CREATE TABLE "User" (
  "id" SERIAL PRIMARY KEY,
  "firstName" VARCHAR(100) NOT NULL,
  "lastName" VARCHAR(100) NOT NULL,
  "email" VARCHAR(255) UNIQUE NOT NULL,
  "role" user_role_enum NOT NULL DEFAULT 'designer',
  "password_hash" VARCHAR(255) NOT NULL,
  "registration_date" TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE "Designer_Profile" (
  "designer_id" INTEGER PRIMARY KEY REFERENCES "User"("id") ON DELETE CASCADE,
  "specialization" VARCHAR(255),
  "bio" TEXT,
  "experience" INTEGER DEFAULT 0, 
  "rating" DECIMAL(3, 2) DEFAULT 0.00,
  "views_count" INTEGER DEFAULT 0,
  "work_amount" INTEGER DEFAULT 0
);

CREATE TABLE "Work" (
  "id" SERIAL PRIMARY KEY,
  "designer_id" INTEGER NOT NULL REFERENCES "User"("id") ON DELETE CASCADE,
  "title" VARCHAR(255) NOT NULL,
  "description" TEXT,
  "upload_date" TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  "views_count" INTEGER DEFAULT 0,
  "image_url" VARCHAR(255)
);

CREATE TABLE "Category" (
  "id" SERIAL PRIMARY KEY,
  "name" VARCHAR(100) UNIQUE NOT NULL
);

CREATE TABLE "Tag" (
  "id" SERIAL PRIMARY KEY,
  "name" VARCHAR(100) UNIQUE NOT NULL
);

CREATE TABLE "Comment" (
  "id" SERIAL PRIMARY KEY,
  "author_id" INTEGER NOT NULL REFERENCES "User"("id") ON DELETE CASCADE,
  "work_id" INTEGER NOT NULL REFERENCES "Work"("id") ON DELETE CASCADE,
  "rating_score" INTEGER CHECK (rating_score >= 1 AND rating_score <= 5),
  "comment_text" TEXT NOT NULL,
  "review_date" TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE "Work_Category" (
  "work_id" INTEGER NOT NULL REFERENCES "Work"("id") ON DELETE CASCADE,
  "category_id" INTEGER NOT NULL REFERENCES "Category"("id") ON DELETE CASCADE,
  PRIMARY KEY ("work_id", "category_id")
);

CREATE TABLE "Work_Tag" (
  "work_id" INTEGER NOT NULL REFERENCES "Work"("id") ON DELETE CASCADE,
  "tag_id" INTEGER NOT NULL REFERENCES "Tag"("id") ON DELETE CASCADE,
  PRIMARY KEY ("work_id", "tag_id")
);

CREATE INDEX ON "Work" ("designer_id");
CREATE INDEX ON "Comment" ("author_id");
CREATE INDEX ON "Comment" ("work_id");