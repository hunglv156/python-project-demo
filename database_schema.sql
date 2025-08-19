-- =========================
-- 0) Database ECTS (Tạo Database)
-- =========================
-- Run DB
-- docker run --name python_project -e POSTGRES_PASSWORD=python_project -p 5432:5432 -v pgdata:/home/hungle/postgresql/data -d postgres
-- Tạo database
-- sudo docker exec -it python_project psql -U postgres
-- CREATE DATABASE "python_project";
-- \quit

-- Truy cập database để chạy câu lệnh
-- sudo docker exec -it python_project psql -U postgres -d python_project

-- =========================
-- 1) USERS (Người dùng)
-- =========================
CREATE TABLE IF NOT EXISTS users (
  id            SERIAL PRIMARY KEY,
  username      VARCHAR(50) NOT NULL UNIQUE,
  password VARCHAR(255) NOT NULL, -- Lưu hash password (bcrypt)
  role          VARCHAR(20) NOT NULL CHECK (role IN ('importer', 'editor', 'generator')),
  created_at    TIMESTAMP NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);

-- =========================
-- 2) SUBJECTS (Môn học)
-- =========================
CREATE TABLE IF NOT EXISTS subjects (
  id         SERIAL PRIMARY KEY,
  name       TEXT NOT NULL UNIQUE,
  created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- =========================
-- 3) USER_SUBJECTS (Phân công môn cho người sửa)
-- =========================
CREATE TABLE IF NOT EXISTS user_subjects (
  user_id    INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  subject_id INTEGER NOT NULL REFERENCES subjects(id) ON DELETE CASCADE,
  PRIMARY KEY (user_id, subject_id)
);
CREATE INDEX IF NOT EXISTS idx_user_subjects_user ON user_subjects(user_id);

-- =========================
-- 4) QUESTIONS (Câu hỏi)
-- =========================
CREATE TABLE IF NOT EXISTS questions (
  id           SERIAL PRIMARY KEY,
  subject_id   INTEGER NOT NULL REFERENCES subjects(id) ON DELETE CASCADE,
  unit_text    TEXT,                      -- ví dụ: "Unit 1"
  question     TEXT NOT NULL,             -- nội dung câu hỏi
  mix_choices  INTEGER NOT NULL DEFAULT 1, -- 1=xáo đáp án; 0=giữ nguyên
  image        TEXT,                      -- đường dẫn ảnh (nếu có)
  mark         DECIMAL(3,2) DEFAULT 1.0,  -- điểm câu hỏi
  created_by   INTEGER NOT NULL REFERENCES users(id), -- Người nhập/tạo câu hỏi
  created_at   TIMESTAMP NOT NULL DEFAULT NOW(),
  updated_by   INTEGER REFERENCES users(id), -- Người sửa (nullable nếu chưa sửa)
  updated_at   TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_questions_subject ON questions(subject_id);
CREATE INDEX IF NOT EXISTS idx_questions_unit_text ON questions(unit_text);

-- =========================
-- 5) CHOICES (Phương án)
-- =========================
CREATE TABLE IF NOT EXISTS choices (
  id          SERIAL PRIMARY KEY,
  question_id INTEGER NOT NULL REFERENCES questions(id) ON DELETE CASCADE,
  content     TEXT NOT NULL,
  is_correct  BOOLEAN NOT NULL DEFAULT FALSE, -- true = đáp án đúng
  position    INTEGER NOT NULL,              -- thứ tự gốc
  created_at  TIMESTAMP NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_choices_question ON choices(question_id);

-- TỐI ĐA 1 đáp án đúng/câu
CREATE UNIQUE INDEX uq_one_correct_per_question
ON choices(question_id)
WHERE is_correct = TRUE;

-- ÍT NHẤT 1 đáp án đúng/câu
CREATE OR REPLACE FUNCTION check_correct_answers()
RETURNS TRIGGER AS $$
BEGIN
  IF (TG_OP = 'UPDATE' AND OLD.is_correct = TRUE AND NEW.is_correct = FALSE) OR 
     (TG_OP = 'DELETE' AND OLD.is_correct = TRUE) THEN
    IF NOT EXISTS (
      SELECT 1 FROM choices
      WHERE question_id = OLD.question_id
        AND id <> OLD.id
        AND is_correct = TRUE
    ) THEN
      RAISE EXCEPTION 'A question must have at least one correct answer';
    END IF;
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_no_zero_correct_on_update
BEFORE UPDATE ON choices
FOR EACH ROW
EXECUTE FUNCTION check_correct_answers();

CREATE TRIGGER trg_no_zero_correct_on_delete
BEFORE DELETE ON choices
FOR EACH ROW
EXECUTE FUNCTION check_correct_answers();

-- Trigger đảm bảo content không được empty
CREATE OR REPLACE FUNCTION check_choice_content()
RETURNS TRIGGER AS $$
BEGIN
  IF NEW.content IS NULL OR TRIM(NEW.content) = '' THEN
    RAISE EXCEPTION 'Choice content cannot be empty';
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_check_choice_content
BEFORE INSERT OR UPDATE ON choices
FOR EACH ROW
EXECUTE FUNCTION check_choice_content();

-- =========================
-- 6) EXAMS (Khuôn đề)
-- =========================
CREATE TABLE IF NOT EXISTS exams (
  id               SERIAL PRIMARY KEY,
  subject_id       INTEGER NOT NULL REFERENCES subjects(id) ON DELETE CASCADE,
  code             TEXT NOT NULL,           -- mã đợt/đề, ví dụ: ENG-MID-2025
  title            TEXT NOT NULL,
  duration_minutes INTEGER NOT NULL,
  num_questions    INTEGER NOT NULL,
  generated_by     INTEGER NOT NULL REFERENCES users(id), -- Người tạo đề
  created_at       TIMESTAMP NOT NULL DEFAULT NOW(),
  UNIQUE(subject_id, code)
);
CREATE INDEX IF NOT EXISTS idx_exams_subject ON exams(subject_id);

-- =========================
-- 7) EXAM_VERSIONS (Mã đề)
-- =========================
CREATE TABLE IF NOT EXISTS exam_versions (
  id            SERIAL PRIMARY KEY,
  exam_id       INTEGER NOT NULL REFERENCES exams(id) ON DELETE CASCADE,
  version_code  TEXT NOT NULL,              -- '101','102',...
  shuffle_seed  INTEGER NOT NULL,           -- seed để tái lập trộn phương án
  is_active     BOOLEAN DEFAULT TRUE,       -- đề có đang sử dụng không
  created_at    TIMESTAMP NOT NULL DEFAULT NOW(),
  UNIQUE(exam_id, version_code)
);
CREATE INDEX IF NOT EXISTS idx_exam_versions_exam ON exam_versions(exam_id);

-- =========================
-- 8) EXAM_VERSION_QUESTIONS (Snapshot thứ tự phương án sau khi xáo)
-- =========================
CREATE TABLE IF NOT EXISTS exam_version_questions (
  id                  SERIAL PRIMARY KEY,
  exam_version_id     INTEGER NOT NULL REFERENCES exam_versions(id) ON DELETE CASCADE,
  question_id         INTEGER NOT NULL REFERENCES questions(id),
  choice_order_json   TEXT NOT NULL,        -- JSON mảng choice.id theo thứ tự sau xáo phương án
  UNIQUE(exam_version_id, question_id)
);
CREATE INDEX IF NOT EXISTS idx_evv_examversion ON exam_version_questions(exam_version_id);
CREATE INDEX IF NOT EXISTS idx_evv_question ON exam_version_questions(question_id);

-- Trigger đảm bảo câu hỏi có đáp án đúng
CREATE OR REPLACE FUNCTION trg_check_correct_choice()
RETURNS TRIGGER AS $$
BEGIN
  IF NOT EXISTS (
    SELECT 1
    FROM choices
    WHERE question_id = NEW.question_id
      AND is_correct = TRUE
  ) THEN
    RAISE EXCEPTION 'Question must have a correct choice before being used in an exam';
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_exam_use_requires_correct
BEFORE INSERT ON exam_version_questions
FOR EACH ROW
EXECUTE FUNCTION trg_check_correct_choice();

-- =========================
-- 9) INSERT SAMPLE DATA
-- =========================

-- Insert sample subjects
INSERT INTO subjects (name) VALUES 
('ISC'),
('Python'),
('Database')
ON CONFLICT (name) DO NOTHING;

-- Insert sample users 
INSERT INTO users (username, password, role) VALUES 
('importer1', '123', 'importer'),
('editor1', '123', 'editor'),
('generator1', '123', 'generator')
ON CONFLICT (username) DO NOTHING; 