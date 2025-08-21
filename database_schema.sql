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
  password VARCHAR(255) NOT NULL,
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

-- Insert sample subjects (Môn học phù hợp cho trẻ em)
INSERT INTO subjects (name) VALUES 
('Toán học cơ bản'),
('Tiếng Việt'),
('Khoa học tự nhiên'),
('Lịch sử Việt Nam'),
('Địa lý Việt Nam'),
('Tiếng Anh cơ bản'),
('Mỹ thuật'),
('Âm nhạc'),
('Thể dục'),
('Đạo đức')
ON CONFLICT (name) DO NOTHING;

-- Insert sample users 
INSERT INTO users (username, password, role) VALUES 
('1', '1', 'importer'),
('2', '2', 'editor'),
('3', '3', 'generator')
ON CONFLICT (username) DO NOTHING;

-- =========================
-- 10) INSERT SAMPLE QUESTIONS FOR CHILDREN
-- =========================

-- Môn: Toán học cơ bản
INSERT INTO questions (subject_id, unit_text, question, mix_choices, image, mark, created_by) VALUES 
(1, 'Phép cộng', '2 + 3 = ?', 1, NULL, 1.0, 1),
(1, 'Phép trừ', '5 - 2 = ?', 1, NULL, 1.0, 1),
(1, 'Phép nhân', '3 x 4 = ?', 1, NULL, 1.0, 1),
(1, 'Phép chia', '8 : 2 = ?', 1, NULL, 1.0, 1),
(1, 'Số tự nhiên', 'Số nào lớn hơn: 7 hay 9?', 1, NULL, 1.0, 1);

-- Môn: Tiếng Việt
INSERT INTO questions (subject_id, unit_text, question, mix_choices, image, mark, created_by) VALUES 
(2, 'Chính tả', 'Từ nào viết đúng: "con mèo" hay "con mẹo"?', 1, NULL, 1.0, 1),
(2, 'Từ vựng', 'Con gì kêu "meo meo"?', 1, NULL, 1.0, 1),
(2, 'Ngữ pháp', 'Từ nào là danh từ: "đẹp", "nhà", "chạy"?', 1, NULL, 1.0, 1),
(2, 'Đọc hiểu', 'Ai là người sinh ra chúng ta?', 1, NULL, 1.0, 1),
(2, 'Viết câu', 'Câu nào đúng: "Tôi đi học" hay "Tôi đi học."?', 1, NULL, 1.0, 1);

-- Môn: Khoa học tự nhiên
INSERT INTO questions (subject_id, unit_text, question, mix_choices, image, mark, created_by) VALUES 
(3, 'Động vật', 'Con gì có 4 chân và sủa "gâu gâu"?', 1, NULL, 1.0, 1),
(3, 'Thực vật', 'Cây nào cho quả màu đỏ và ăn được?', 1, NULL, 1.0, 1),
(3, 'Thời tiết', 'Khi trời mưa, chúng ta cần mang gì?', 1, NULL, 1.0, 1),
(3, 'Cơ thể', 'Chúng ta thở bằng bộ phận nào?', 1, NULL, 1.0, 1),
(3, 'Vệ sinh', 'Trước khi ăn, chúng ta cần làm gì?', 1, NULL, 1.0, 1);

-- Môn: Lịch sử Việt Nam
INSERT INTO questions (subject_id, unit_text, question, mix_choices, image, mark, created_by) VALUES 
(4, 'Vua Hùng', 'Ai là vị vua đầu tiên của nước ta?', 1, NULL, 1.0, 1),
(4, 'Hai Bà Trưng', 'Hai Bà Trưng đánh giặc nào?', 1, NULL, 1.0, 1),
(4, 'Ngô Quyền', 'Ngô Quyền đánh bại quân nào trên sông Bạch Đằng?', 1, NULL, 1.0, 1),
(4, 'Lý Thường Kiệt', 'Ai là người đánh bại quân Tống?', 1, NULL, 1.0, 1),
(4, 'Quang Trung', 'Vua Quang Trung đánh bại quân nào?', 1, NULL, 1.0, 1);

-- Môn: Địa lý Việt Nam
INSERT INTO questions (subject_id, unit_text, question, mix_choices, image, mark, created_by) VALUES 
(5, 'Thủ đô', 'Thủ đô của nước ta là thành phố nào?', 1, NULL, 1.0, 1),
(5, 'Sông Hồng', 'Sông Hồng chảy qua vùng nào?', 1, NULL, 1.0, 1),
(5, 'Biển Đông', 'Nước ta có biển nào ở phía Đông?', 1, NULL, 1.0, 1),
(5, 'Đồng bằng', 'Đồng bằng sông Cửu Long ở miền nào?', 1, NULL, 1.0, 1),
(5, 'Núi', 'Núi nào cao nhất Việt Nam?', 1, NULL, 1.0, 1);

-- Môn: Tiếng Anh cơ bản
INSERT INTO questions (subject_id, unit_text, question, mix_choices, image, mark, created_by) VALUES 
(6, 'Số đếm', 'Số 1 trong tiếng Anh là gì?', 1, NULL, 1.0, 1),
(6, 'Màu sắc', 'Màu đỏ trong tiếng Anh là gì?', 1, NULL, 1.0, 1),
(6, 'Con vật', 'Con mèo trong tiếng Anh là gì?', 1, NULL, 1.0, 1),
(6, 'Chào hỏi', 'Xin chào trong tiếng Anh là gì?', 1, NULL, 1.0, 1),
(6, 'Gia đình', 'Mẹ trong tiếng Anh là gì?', 1, NULL, 1.0, 1);

-- Môn: Mỹ thuật
INSERT INTO questions (subject_id, unit_text, question, mix_choices, image, mark, created_by) VALUES 
(7, 'Màu sắc', 'Màu nào là màu cơ bản?', 1, NULL, 1.0, 1),
(7, 'Hình học', 'Hình nào có 3 cạnh?', 1, NULL, 1.0, 1),
(7, 'Vẽ tranh', 'Khi vẽ mặt trời, ta dùng màu gì?', 1, NULL, 1.0, 1),
(7, 'Tạo hình', 'Đất nặn dùng để làm gì?', 1, NULL, 1.0, 1),
(7, 'Thủ công', 'Giấy màu dùng để làm gì?', 1, NULL, 1.0, 1);

-- Môn: Âm nhạc
INSERT INTO questions (subject_id, unit_text, question, mix_choices, image, mark, created_by) VALUES 
(8, 'Nhạc cụ', 'Đàn gì có 6 dây?', 1, NULL, 1.0, 1),
(8, 'Bài hát', 'Bài "Cháu yêu bà" nói về ai?', 1, NULL, 1.0, 1),
(8, 'Âm thanh', 'Tiếng gì phát ra từ trống?', 1, NULL, 1.0, 1),
(8, 'Giai điệu', 'Khi vui, chúng ta hát như thế nào?', 1, NULL, 1.0, 1),
(8, 'Vận động', 'Khi hát, chúng ta có thể làm gì?', 1, NULL, 1.0, 1);

-- Môn: Thể dục
INSERT INTO questions (subject_id, unit_text, question, mix_choices, image, mark, created_by) VALUES 
(9, 'Chạy', 'Chạy giúp cơ thể như thế nào?', 1, NULL, 1.0, 1),
(9, 'Nhảy', 'Nhảy dây cần dụng cụ gì?', 1, NULL, 1.0, 1),
(9, 'Bơi', 'Khi bơi, chúng ta cần làm gì?', 1, NULL, 1.0, 1),
(9, 'Bóng đá', 'Bóng đá cần bao nhiêu người?', 1, NULL, 1.0, 1),
(9, 'Sức khỏe', 'Tập thể dục giúp gì?', 1, NULL, 1.0, 1);

-- Môn: Đạo đức
INSERT INTO questions (subject_id, unit_text, question, mix_choices, image, mark, created_by) VALUES 
(10, 'Lễ phép', 'Khi gặp người lớn, chúng ta làm gì?', 1, NULL, 1.0, 1),
(10, 'Giúp đỡ', 'Khi thấy bạn ngã, chúng ta làm gì?', 1, NULL, 1.0, 1),
(10, 'Thật thà', 'Khi làm sai, chúng ta nên làm gì?', 1, NULL, 1.0, 1),
(10, 'Tôn trọng', 'Chúng ta có nên nói tục không?', 1, NULL, 1.0, 1),
(10, 'Yêu thương', 'Chúng ta có nên yêu thương bạn bè không?', 1, NULL, 1.0, 1);

-- =========================
-- 11) INSERT CHOICES FOR EACH QUESTION
-- =========================

-- Toán học cơ bản - Câu 1: 2 + 3 = ?
INSERT INTO choices (question_id, content, is_correct, position) VALUES 
(1, '5', TRUE, 1),
(1, '6', FALSE, 2),
(1, '4', FALSE, 3),
(1, '7', FALSE, 4);

-- Toán học cơ bản - Câu 2: 5 - 2 = ?
INSERT INTO choices (question_id, content, is_correct, position) VALUES 
(2, '3', TRUE, 1),
(2, '2', FALSE, 2),
(2, '4', FALSE, 3),
(2, '1', FALSE, 4);

-- Toán học cơ bản - Câu 3: 3 x 4 = ?
INSERT INTO choices (question_id, content, is_correct, position) VALUES 
(3, '12', TRUE, 1),
(3, '7', FALSE, 2),
(3, '8', FALSE, 3),
(3, '10', FALSE, 4);

-- Toán học cơ bản - Câu 4: 8 : 2 = ?
INSERT INTO choices (question_id, content, is_correct, position) VALUES 
(4, '4', TRUE, 1),
(4, '6', FALSE, 2),
(4, '2', FALSE, 3),
(4, '3', FALSE, 4);

-- Toán học cơ bản - Câu 5: Số nào lớn hơn: 7 hay 9?
INSERT INTO choices (question_id, content, is_correct, position) VALUES 
(5, '9', TRUE, 1),
(5, '7', FALSE, 2),
(5, 'Bằng nhau', FALSE, 3),
(5, 'Không biết', FALSE, 4);

-- Tiếng Việt - Câu 1: Từ nào viết đúng: "con mèo" hay "con mẹo"?
INSERT INTO choices (question_id, content, is_correct, position) VALUES 
(6, 'con mèo', TRUE, 1),
(6, 'con mẹo', FALSE, 2),
(6, 'con méo', FALSE, 3),
(6, 'con mẹo', FALSE, 4);

-- Tiếng Việt - Câu 2: Con gì kêu "meo meo"?
INSERT INTO choices (question_id, content, is_correct, position) VALUES 
(7, 'Con mèo', TRUE, 1),
(7, 'Con chó', FALSE, 2),
(7, 'Con gà', FALSE, 3),
(7, 'Con vịt', FALSE, 4);

-- Tiếng Việt - Câu 3: Từ nào là danh từ: "đẹp", "nhà", "chạy"?
INSERT INTO choices (question_id, content, is_correct, position) VALUES 
(8, 'nhà', TRUE, 1),
(8, 'đẹp', FALSE, 2),
(8, 'chạy', FALSE, 3),
(8, 'Cả ba từ', FALSE, 4);

-- Tiếng Việt - Câu 4: Ai là người sinh ra chúng ta?
INSERT INTO choices (question_id, content, is_correct, position) VALUES 
(9, 'Bố mẹ', TRUE, 1),
(9, 'Ông bà', FALSE, 2),
(9, 'Thầy cô', FALSE, 3),
(9, 'Bạn bè', FALSE, 4);

-- Tiếng Việt - Câu 5: Câu nào đúng: "Tôi đi học" hay "Tôi đi học."?
INSERT INTO choices (question_id, content, is_correct, position) VALUES 
(10, 'Tôi đi học.', TRUE, 1),
(10, 'Tôi đi học', FALSE, 2),
(10, 'Cả hai đều đúng', FALSE, 3),
(10, 'Cả hai đều sai', FALSE, 4);

-- Khoa học tự nhiên - Câu 1: Con gì có 4 chân và sủa "gâu gâu"?
INSERT INTO choices (question_id, content, is_correct, position) VALUES 
(11, 'Con chó', TRUE, 1),
(11, 'Con mèo', FALSE, 2),
(11, 'Con gà', FALSE, 3),
(11, 'Con vịt', FALSE, 4);

-- Khoa học tự nhiên - Câu 2: Cây nào cho quả màu đỏ và ăn được?
INSERT INTO choices (question_id, content, is_correct, position) VALUES 
(12, 'Cây táo', TRUE, 1),
(12, 'Cây chuối', FALSE, 2),
(12, 'Cây cam', FALSE, 3),
(12, 'Cây dừa', FALSE, 4);

-- Khoa học tự nhiên - Câu 3: Khi trời mưa, chúng ta cần mang gì?
INSERT INTO choices (question_id, content, is_correct, position) VALUES 
(13, 'Áo mưa', TRUE, 1),
(13, 'Áo khoác', FALSE, 2),
(13, 'Mũ', FALSE, 3),
(13, 'Giày', FALSE, 4);

-- Khoa học tự nhiên - Câu 4: Chúng ta thở bằng bộ phận nào?
INSERT INTO choices (question_id, content, is_correct, position) VALUES 
(14, 'Mũi', TRUE, 1),
(14, 'Miệng', FALSE, 2),
(14, 'Tai', FALSE, 3),
(14, 'Mắt', FALSE, 4);

-- Khoa học tự nhiên - Câu 5: Trước khi ăn, chúng ta cần làm gì?
INSERT INTO choices (question_id, content, is_correct, position) VALUES 
(15, 'Rửa tay', TRUE, 1),
(15, 'Đánh răng', FALSE, 2),
(15, 'Tắm', FALSE, 3),
(15, 'Thay quần áo', FALSE, 4);

-- Lịch sử Việt Nam - Câu 1: Ai là vị vua đầu tiên của nước ta?
INSERT INTO choices (question_id, content, is_correct, position) VALUES 
(16, 'Vua Hùng', TRUE, 1),
(16, 'Vua Lý', FALSE, 2),
(16, 'Vua Trần', FALSE, 3),
(16, 'Vua Lê', FALSE, 4);

-- Lịch sử Việt Nam - Câu 2: Hai Bà Trưng đánh giặc nào?
INSERT INTO choices (question_id, content, is_correct, position) VALUES 
(17, 'Giặc Hán', TRUE, 1),
(17, 'Giặc Tống', FALSE, 2),
(17, 'Giặc Nguyên', FALSE, 3),
(17, 'Giặc Minh', FALSE, 4);

-- Lịch sử Việt Nam - Câu 3: Ngô Quyền đánh bại quân nào trên sông Bạch Đằng?
INSERT INTO choices (question_id, content, is_correct, position) VALUES 
(18, 'Quân Nam Hán', TRUE, 1),
(18, 'Quân Tống', FALSE, 2),
(18, 'Quân Nguyên', FALSE, 3),
(18, 'Quân Minh', FALSE, 4);

-- Lịch sử Việt Nam - Câu 4: Ai là người đánh bại quân Tống?
INSERT INTO choices (question_id, content, is_correct, position) VALUES 
(19, 'Lý Thường Kiệt', TRUE, 1),
(19, 'Trần Hưng Đạo', FALSE, 2),
(19, 'Lê Lợi', FALSE, 3),
(19, 'Quang Trung', FALSE, 4);

-- Lịch sử Việt Nam - Câu 5: Vua Quang Trung đánh bại quân nào?
INSERT INTO choices (question_id, content, is_correct, position) VALUES 
(20, 'Quân Thanh', TRUE, 1),
(20, 'Quân Tống', FALSE, 2),
(20, 'Quân Nguyên', FALSE, 3),
(20, 'Quân Minh', FALSE, 4);

-- Địa lý Việt Nam - Câu 1: Thủ đô của nước ta là thành phố nào?
INSERT INTO choices (question_id, content, is_correct, position) VALUES 
(21, 'Hà Nội', TRUE, 1),
(21, 'TP. Hồ Chí Minh', FALSE, 2),
(21, 'Đà Nẵng', FALSE, 3),
(21, 'Hải Phòng', FALSE, 4);

-- Địa lý Việt Nam - Câu 2: Sông Hồng chảy qua vùng nào?
INSERT INTO choices (question_id, content, is_correct, position) VALUES 
(22, 'Đồng bằng Bắc Bộ', TRUE, 1),
(22, 'Đồng bằng Nam Bộ', FALSE, 2),
(22, 'Tây Nguyên', FALSE, 3),
(22, 'Duyên hải miền Trung', FALSE, 4);

-- Địa lý Việt Nam - Câu 3: Nước ta có biển nào ở phía Đông?
INSERT INTO choices (question_id, content, is_correct, position) VALUES 
(23, 'Biển Đông', TRUE, 1),
(23, 'Biển Tây', FALSE, 2),
(23, 'Biển Nam', FALSE, 3),
(23, 'Biển Bắc', FALSE, 4);

-- Địa lý Việt Nam - Câu 4: Đồng bằng sông Cửu Long ở miền nào?
INSERT INTO choices (question_id, content, is_correct, position) VALUES 
(24, 'Miền Nam', TRUE, 1),
(24, 'Miền Bắc', FALSE, 2),
(24, 'Miền Trung', FALSE, 3),
(24, 'Tây Nguyên', FALSE, 4);

-- Địa lý Việt Nam - Câu 5: Núi nào cao nhất Việt Nam?
INSERT INTO choices (question_id, content, is_correct, position) VALUES 
(25, 'Núi Phan Xi Păng', TRUE, 1),
(25, 'Núi Bà Đen', FALSE, 2),
(25, 'Núi Lang Bian', FALSE, 3),
(25, 'Núi Ngọc Linh', FALSE, 4);

-- Tiếng Anh cơ bản - Câu 1: Số 1 trong tiếng Anh là gì?
INSERT INTO choices (question_id, content, is_correct, position) VALUES 
(26, 'One', TRUE, 1),
(26, 'Two', FALSE, 2),
(26, 'Three', FALSE, 3),
(26, 'Four', FALSE, 4);

-- Tiếng Anh cơ bản - Câu 2: Màu đỏ trong tiếng Anh là gì?
INSERT INTO choices (question_id, content, is_correct, position) VALUES 
(27, 'Red', TRUE, 1),
(27, 'Blue', FALSE, 2),
(27, 'Green', FALSE, 3),
(27, 'Yellow', FALSE, 4);

-- Tiếng Anh cơ bản - Câu 3: Con mèo trong tiếng Anh là gì?
INSERT INTO choices (question_id, content, is_correct, position) VALUES 
(28, 'Cat', TRUE, 1),
(28, 'Dog', FALSE, 2),
(28, 'Bird', FALSE, 3),
(28, 'Fish', FALSE, 4);

-- Tiếng Anh cơ bản - Câu 4: Xin chào trong tiếng Anh là gì?
INSERT INTO choices (question_id, content, is_correct, position) VALUES 
(29, 'Hello', TRUE, 1),
(29, 'Goodbye', FALSE, 2),
(29, 'Thank you', FALSE, 3),
(29, 'Please', FALSE, 4);

-- Tiếng Anh cơ bản - Câu 5: Mẹ trong tiếng Anh là gì?
INSERT INTO choices (question_id, content, is_correct, position) VALUES 
(30, 'Mother', TRUE, 1),
(30, 'Father', FALSE, 2),
(30, 'Sister', FALSE, 3),
(30, 'Brother', FALSE, 4);

-- Mỹ thuật - Câu 1: Màu nào là màu cơ bản?
INSERT INTO choices (question_id, content, is_correct, position) VALUES 
(31, 'Đỏ', TRUE, 1),
(31, 'Xanh lá', FALSE, 2),
(31, 'Tím', FALSE, 3),
(31, 'Nâu', FALSE, 4);

-- Mỹ thuật - Câu 2: Hình nào có 3 cạnh?
INSERT INTO choices (question_id, content, is_correct, position) VALUES 
(32, 'Hình tam giác', TRUE, 1),
(32, 'Hình vuông', FALSE, 2),
(32, 'Hình tròn', FALSE, 3),
(32, 'Hình chữ nhật', FALSE, 4);

-- Mỹ thuật - Câu 3: Khi vẽ mặt trời, ta dùng màu gì?
INSERT INTO choices (question_id, content, is_correct, position) VALUES 
(33, 'Màu vàng', TRUE, 1),
(33, 'Màu xanh', FALSE, 2),
(33, 'Màu đen', FALSE, 3),
(33, 'Màu trắng', FALSE, 4);

-- Mỹ thuật - Câu 4: Đất nặn dùng để làm gì?
INSERT INTO choices (question_id, content, is_correct, position) VALUES 
(34, 'Nặn hình', TRUE, 1),
(34, 'Vẽ tranh', FALSE, 2),
(34, 'Cắt giấy', FALSE, 3),
(34, 'Xé giấy', FALSE, 4);

-- Mỹ thuật - Câu 5: Giấy màu dùng để làm gì?
INSERT INTO choices (question_id, content, is_correct, position) VALUES 
(35, 'Cắt dán', TRUE, 1),
(35, 'Vẽ tranh', FALSE, 2),
(35, 'Nặn hình', FALSE, 3),
(35, 'Viết chữ', FALSE, 4);

-- Âm nhạc - Câu 1: Đàn gì có 6 dây?
INSERT INTO choices (question_id, content, is_correct, position) VALUES 
(36, 'Đàn guitar', TRUE, 1),
(36, 'Đàn piano', FALSE, 2),
(36, 'Đàn violin', FALSE, 3),
(36, 'Đàn organ', FALSE, 4);

-- Âm nhạc - Câu 2: Bài "Cháu yêu bà" nói về ai?
INSERT INTO choices (question_id, content, is_correct, position) VALUES 
(37, 'Bà', TRUE, 1),
(37, 'Mẹ', FALSE, 2),
(37, 'Chị', FALSE, 3),
(37, 'Bạn', FALSE, 4);

-- Âm nhạc - Câu 3: Tiếng gì phát ra từ trống?
INSERT INTO choices (question_id, content, is_correct, position) VALUES 
(38, 'Tiếng trống', TRUE, 1),
(38, 'Tiếng đàn', FALSE, 2),
(38, 'Tiếng sáo', FALSE, 3),
(38, 'Tiếng hát', FALSE, 4);

-- Âm nhạc - Câu 4: Khi vui, chúng ta hát như thế nào?
INSERT INTO choices (question_id, content, is_correct, position) VALUES 
(39, 'Vui vẻ', TRUE, 1),
(39, 'Buồn bã', FALSE, 2),
(39, 'Giận dữ', FALSE, 3),
(39, 'Sợ hãi', FALSE, 4);

-- Âm nhạc - Câu 5: Khi hát, chúng ta có thể làm gì?
INSERT INTO choices (question_id, content, is_correct, position) VALUES 
(40, 'Vỗ tay', TRUE, 1),
(40, 'Khóc', FALSE, 2),
(40, 'Ngủ', FALSE, 3),
(40, 'Chạy', FALSE, 4);

-- Thể dục - Câu 1: Chạy giúp cơ thể như thế nào?
INSERT INTO choices (question_id, content, is_correct, position) VALUES 
(41, 'Khỏe mạnh', TRUE, 1),
(41, 'Mệt mỏi', FALSE, 2),
(41, 'Buồn ngủ', FALSE, 3),
(41, 'Đói bụng', FALSE, 4);

-- Thể dục - Câu 2: Nhảy dây cần dụng cụ gì?
INSERT INTO choices (question_id, content, is_correct, position) VALUES 
(42, 'Dây nhảy', TRUE, 1),
(42, 'Bóng', FALSE, 2),
(42, 'Vợt', FALSE, 3),
(42, 'Gậy', FALSE, 4);

-- Thể dục - Câu 3: Khi bơi, chúng ta cần làm gì?
INSERT INTO choices (question_id, content, is_correct, position) VALUES 
(43, 'Có người lớn giám sát', TRUE, 1),
(43, 'Bơi một mình', FALSE, 2),
(43, 'Bơi ban đêm', FALSE, 3),
(43, 'Bơi khi mưa', FALSE, 4);

-- Thể dục - Câu 4: Bóng đá cần bao nhiêu người?
INSERT INTO choices (question_id, content, is_correct, position) VALUES 
(44, '11 người mỗi đội', TRUE, 1),
(44, '5 người mỗi đội', FALSE, 2),
(44, '7 người mỗi đội', FALSE, 3),
(44, '9 người mỗi đội', FALSE, 4);

-- Thể dục - Câu 5: Tập thể dục giúp gì?
INSERT INTO choices (question_id, content, is_correct, position) VALUES 
(45, 'Sức khỏe tốt', TRUE, 1),
(45, 'Bệnh tật', FALSE, 2),
(45, 'Mệt mỏi', FALSE, 3),
(45, 'Buồn ngủ', FALSE, 4);

-- Đạo đức - Câu 1: Khi gặp người lớn, chúng ta làm gì?
INSERT INTO choices (question_id, content, is_correct, position) VALUES 
(46, 'Chào hỏi', TRUE, 1),
(46, 'Bỏ chạy', FALSE, 2),
(46, 'Làm ngơ', FALSE, 3),
(46, 'Nói tục', FALSE, 4);

-- Đạo đức - Câu 2: Khi thấy bạn ngã, chúng ta làm gì?
INSERT INTO choices (question_id, content, is_correct, position) VALUES 
(47, 'Giúp bạn đứng dậy', TRUE, 1),
(47, 'Cười bạn', FALSE, 2),
(47, 'Bỏ đi', FALSE, 3),
(47, 'Chạy trốn', FALSE, 4);

-- Đạo đức - Câu 3: Khi làm sai, chúng ta nên làm gì?
INSERT INTO choices (question_id, content, is_correct, position) VALUES 
(48, 'Xin lỗi', TRUE, 1),
(48, 'Giấu diếm', FALSE, 2),
(48, 'Đổ lỗi', FALSE, 3),
(48, 'Bỏ chạy', FALSE, 4);

-- Đạo đức - Câu 4: Chúng ta có nên nói tục không?
INSERT INTO choices (question_id, content, is_correct, position) VALUES 
(49, 'Không nên', TRUE, 1),
(49, 'Nên', FALSE, 2),
(49, 'Tùy lúc', FALSE, 3),
(49, 'Không biết', FALSE, 4);

-- Đạo đức - Câu 5: Chúng ta có nên yêu thương bạn bè không?
INSERT INTO choices (question_id, content, is_correct, position) VALUES 
(50, 'Có', TRUE, 1),
(50, 'Không', FALSE, 2),
(50, 'Tùy lúc', FALSE, 3),
(50, 'Không biết', FALSE, 4); 