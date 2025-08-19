# Test Management System

Hệ thống quản lý ngân hàng đề thi sử dụng Python với FastAPI (backend) và Tkinter (frontend).

## Tính năng

### Phân quyền người dùng

- **Người nhập đề (Importer)**: Import file DOCX vào database
- **Người sửa ngân hàng đề (Editor)**: Quản lý câu hỏi (CRUD) - Thêm, sửa, xóa câu hỏi
- **Người sinh đề thi (Generator)**: Tạo đề thi với xáo trộn đáp án - Tạo đề thi mới và thêm phiên bản với đáp án được xáo trộn

### Chức năng chính

1. **Authentication**: Đăng nhập với username/password
2. **Import DOCX**: Upload và parse file DOCX theo template
3. **Question Management**: CRUD operations đầy đủ cho câu hỏi (Create, Read, Update, Delete)
4. **Exam Generation**: Tạo đề thi mới và thêm phiên bản với xáo trộn đáp án tự động
5. **Image Support**: Hiển thị ảnh từ đường dẫn local
6. **Role-based Access Control**: Phân quyền chức năng theo vai trò người dùng

## Cài đặt

### Yêu cầu hệ thống

- Python 3.13.5
- PostgreSQL (Docker)
- Docker

### Bước 1: Setup Database

```bash
# Chạy PostgreSQL container
docker run --name python_project -e POSTGRES_PASSWORD=python_project -p 5432:5432 -v pgdata:/home/hungle/postgresql/data -d postgres

# Tạo database
sudo docker exec -it python_project psql -U postgres
CREATE DATABASE "python_project";
\quit

# Chạy schema
sudo docker exec -it python_project psql -U postgres -d python_project -f /path/to/database_schema.sql
```

### Bước 2: Cài đặt dependencies

```bash
pip install -r requirements.txt
```

### Bước 3: Tạo thư mục cần thiết

```bash
mkdir images uploads
```

## Sử dụng

### Chạy ứng dụng

```bash
python main.py
```

### Tài khoản mẫu

- **Username**: importer, **Password**: 123, **Role**: importer
- **Username**: editor, **Password**: 123, **Role**: editor
- **Username**: generator, **Password**: 123, **Role**: generator

### Hướng dẫn sử dụng

#### Editor Role - Quản lý câu hỏi (CRUD)

1. **Đăng nhập** với tài khoản editor
2. **Chọn "Manage Questions (CRUD)"** từ menu
3. **Thêm câu hỏi mới**:
   - Click "Add New Question"
   - Chọn môn học
   - Nhập nội dung câu hỏi
   - Thêm các đáp án và chọn đáp án đúng
   - Click "Save"
4. **Sửa câu hỏi**:
   - Chọn câu hỏi từ danh sách
   - Click "Edit Question"
   - Chỉnh sửa thông tin
   - Click "Save"
5. **Xóa câu hỏi**:
   - Chọn câu hỏi từ danh sách
   - Click "Delete Question"
   - Xác nhận xóa

#### Generator Role - Tạo đề thi với xáo trộn đáp án

1. **Đăng nhập** với tài khoản generator
2. **Chọn "Generate Exam with Mixed Answers"** từ menu
3. **Tạo đề thi mới**:
   - Click "Create New Exam"
   - Nhập thông tin đề thi (mã, tiêu đề, thời gian)
   - Chọn các câu hỏi từ danh sách
   - Click "Save" - hệ thống tự động tạo phiên bản đầu tiên với đáp án xáo trộn
4. **Thêm phiên bản mới**:
   - Chọn đề thi từ danh sách
   - Click "Add Version to Exam"
   - Chọn câu hỏi cho phiên bản mới
   - Click "Add Version" - hệ thống tạo phiên bản mới với đáp án xáo trộn khác

## Cấu trúc Project

```
project/
├── backend/                 # FastAPI backend
│   ├── main.py             # FastAPI app
│   ├── config.py           # Configuration
│   ├── database.py         # Database connection
│   ├── models/             # Database models
│   ├── routes/             # API routes
│   └── services/           # Business logic
├── frontend/               # Tkinter frontend
│   ├── config.py           # Frontend config
│   ├── api_client.py       # API client
│   └── views/              # UI views
├── images/                 # Thư mục ảnh
├── uploads/                # File upload tạm
├── database_schema.sql     # Database schema
├── requirements.txt        # Dependencies
├── main.py                 # Main application
└── README.md              # Documentation
```

## API Endpoints

### Authentication

- `POST /auth/login` - Đăng nhập
- `GET /auth/user/{user_id}` - Lấy thông tin user

### Subjects

- `GET /subjects/` - Lấy tất cả subjects
- `GET /subjects/{subject_id}` - Lấy subject theo ID
- `POST /subjects/` - Tạo subject mới

### Questions

- `GET /questions/` - Lấy tất cả questions
- `GET /questions/{question_id}` - Lấy question theo ID
- `POST /questions/` - Tạo question mới
- `PUT /questions/{question_id}` - Cập nhật question
- `DELETE /questions/{question_id}` - Xóa question

### Exams

- `GET /exams/` - Lấy tất cả exams
- `GET /exams/{exam_id}` - Lấy exam theo ID
- `POST /exams/` - Tạo exam mới
- `POST /exams/{exam_id}/versions` - Thêm version cho exam

### Import

- `POST /import/preview` - Preview DOCX file
- `POST /import/docx` - Import DOCX file

## Template DOCX Format

File DOCX phải theo format sau:

```
Subject: ISC
Number of Quiz: 30
Lecturer: hungpd2
Date: dd-mm-yyyy

QN=1
See the figure and choose the right type of B2B E-Commerce
[file:8435.jpg]
a. Sell-side B2B
b. Electronic Exchange
c. Buy-side B2B
d. Supply Chain Improvements and Collaborative Commerce
ANSWER: B
MARK: 0.5
UNIT: Chapter1
MIX CHOICES: Yes
```

## Database Schema

### Tables

- `users` - Thông tin người dùng
- `subjects` - Môn học
- `questions` - Câu hỏi
- `choices` - Đáp án
- `exams` - Khuôn đề
- `exam_versions` - Phiên bản đề
- `exam_version_questions` - Snapshot câu hỏi sau xáo trộn

## Tính năng bảo mật

- Password hashing với bcrypt
- Role-based access control
- Input validation
- Error handling

## Testing

### Test CRUD và Exam Generation

Chạy script test để kiểm tra các chức năng mới:

```bash
python test_crud_and_exam_generation.py
```

Script này sẽ test:

- CRUD operations cho câu hỏi (Create, Read, Update, Delete)
- Tạo đề thi với xáo trộn đáp án
- Thêm phiên bản mới cho đề thi

## Troubleshooting

### Lỗi kết nối database

- Kiểm tra PostgreSQL container có đang chạy không
- Kiểm tra connection string trong `backend/config.py`

### Lỗi import DOCX

- Kiểm tra format file DOCX có đúng template không
- Kiểm tra thư mục `uploads/` có tồn tại không

### Lỗi hiển thị ảnh

- Kiểm tra thư mục `images/` có tồn tại không
- Kiểm tra đường dẫn ảnh trong database

### Lỗi CRUD operations

- Kiểm tra quyền truy cập database
- Kiểm tra API server có đang chạy không
- Kiểm tra log lỗi trong console

## Contributing

1. Fork project
2. Tạo feature branch
3. Commit changes
4. Push to branch
5. Tạo Pull Request

## License

MIT License
