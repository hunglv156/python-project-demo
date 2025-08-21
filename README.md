# Hệ Thống Quản Lý Ngân Hàng Đề Thi

Một hệ thống quản lý ngân hàng đề thi hoàn chỉnh được xây dựng bằng Python với FastAPI (backend) và Tkinter (frontend). Hệ thống hỗ trợ import đề thi từ file DOCX, quản lý câu hỏi, tạo đề thi tự động với xáo trộn đáp án và hiển thị ảnh.

## 🚀 Tính Năng Chính

### 👥 Phân Quyền Người Dùng

- **Importer**: Import file DOCX vào database
- **Editor**: Quản lý câu hỏi (CRUD) - Thêm, sửa, xóa câu hỏi
- **Generator**: Tạo đề thi với xáo trộn đáp án tự động

### 🎯 Chức Năng Chính

- ✅ **Authentication**: Đăng nhập với username/password
- ✅ **Import DOCX**: Upload và parse file DOCX theo template chuẩn
- ✅ **Question Management**: CRUD operations đầy đủ cho câu hỏi
- ✅ **Exam Generation**: Tạo đề thi mới với xáo trộn đáp án tự động
- ✅ **Image Support**: Hiển thị ảnh trong preview đề thi
- ✅ **Role-based Access Control**: Phân quyền chức năng theo vai trò
- ✅ **Exam Preview**: Xem trước đề thi với ảnh và đáp án đúng được highlight

## 🛠️ Cài Đặt

### Yêu Cầu Hệ Thống

- Python 3.8+
- PostgreSQL 12+
- Docker (khuyến nghị)

### Bước 1: Clone Repository

```bash
git clone <repository-url>
cd python-project-demo
```

### Bước 2: Setup Database

```bash
# Chạy PostgreSQL container
docker run --name python_project \
  -e POSTGRES_PASSWORD=python_project \
  -p 5432:5432 \
  -v pgdata:/var/lib/postgresql/data \
  -d postgres:latest

# Tạo database
docker exec -it python_project psql -U postgres -c "CREATE DATABASE python_project;"

# Import schema
docker exec -i python_project psql -U postgres -d python_project < database_schema.sql
```

### Bước 3: Cài Đặt Dependencies

```bash
pip install -r requirements.txt
```

### Bước 4: Tạo Thư Mục Cần Thiết

```bash
mkdir -p images uploads
```

## 🚀 Sử Dụng

### Khởi Chạy Ứng Dụng

```bash
python main.py
```

### Tài Khoản Mẫu

| Username    | Password | Role      | Chức Năng        |
| ----------- | -------- | --------- | ---------------- |
| `1`  | `1`    | Importer  | Import file DOCX |
| `2`    | `2`    | Editor    | Quản lý câu hỏi  |
| `3` | `3`    | Generator | Tạo đề thi       |

## 📖 Hướng Dẫn Sử Dụng

### 🔧 Editor Role - Quản Lý Câu Hỏi

1. **Đăng nhập** với tài khoản `editor`
2. **Chọn "Manage Questions (CRUD)"** từ menu
3. **Thêm câu hỏi mới**:

   - Click "Add New Question"
   - Chọn môn học
   - Nhập nội dung câu hỏi
   - Thêm ảnh (nếu có) bằng cách nhập tên file ảnh
   - Thêm các đáp án và chọn đáp án đúng
   - Click "Save"

4. **Sửa/Xóa câu hỏi**:
   - Chọn câu hỏi từ danh sách
   - Click "Edit Question" hoặc "Delete Question"

### 🎲 Generator Role - Tạo Đề Thi

1. **Đăng nhập** với tài khoản `generator`
2. **Chọn "Generate Exam with Mixed Answers"** từ menu
3. **Tạo đề thi mới**:

   - Chọn môn thi
   - Nhập thời gian thi và số câu hỏi
   - Click "Tạo Đề Thi"
   - Hệ thống tự động chọn câu hỏi ngẫu nhiên và xáo trộn đáp án

4. **Xem preview đề thi**:
   - Double-click vào đề thi trong danh sách
   - Xem toàn bộ đề thi với ảnh (nếu có)
   - Đáp án đúng được highlight màu xanh

### 📄 Importer Role - Import DOCX

1. **Đăng nhập** với tài khoản `importer`
2. **Chọn "Import DOCX"** từ menu
3. **Upload file DOCX** theo template chuẩn
4. **Preview** và **Import** vào database

## 📁 Cấu Trúc Project

```
python-project-demo/
├── backend/                 # FastAPI Backend
│   ├── main.py             # FastAPI application
│   ├── config.py           # Configuration settings
│   ├── database.py         # Database connection
│   ├── models/             # Database models
│   │   ├── user.py         # User model
│   │   ├── subject.py      # Subject model
│   │   ├── question.py     # Question model
│   │   └── exam.py         # Exam model
│   ├── routes/             # API endpoints
│   │   ├── auth.py         # Authentication
│   │   ├── questions.py    # Question management
│   │   ├── exams.py        # Exam generation
│   │   └── import_docx.py  # DOCX import
│   ├── services/           # Business logic
│   │   └── docx_parser.py  # DOCX parsing
│   └── utils/              # Utilities
│       └── subject_code_generator.py
├── frontend/               # Tkinter Frontend
│   ├── config.py           # Frontend configuration
│   ├── api_client.py       # API client
│   └── views/              # UI Views
│       ├── login_view.py   # Login screen
│       ├── dashboard_view.py # Main dashboard
│       ├── question_view.py # Question management
│       ├── exam_view.py    # Exam generation
│       └── import_view.py  # DOCX import
├── images/                 # Image files
├── uploads/                # Temporary uploads
├── database_schema.sql     # Database schema
├── requirements.txt        # Python dependencies
├── main.py                 # Application entry point
└── README.md              # Documentation
```

## 🔌 API Endpoints

### Authentication

- `POST /auth/login` - Đăng nhập
- `GET /auth/user/{user_id}` - Lấy thông tin user

### Subjects

- `GET /subjects/` - Lấy tất cả môn học
- `GET /subjects/{subject_id}` - Lấy môn học theo ID
- `POST /subjects/` - Tạo môn học mới

### Questions

- `GET /questions/` - Lấy tất cả câu hỏi
- `GET /questions/{question_id}` - Lấy câu hỏi theo ID
- `POST /questions/` - Tạo câu hỏi mới
- `PUT /questions/{question_id}` - Cập nhật câu hỏi
- `DELETE /questions/{question_id}` - Xóa câu hỏi

### Exams

- `GET /exams/` - Lấy tất cả đề thi
- `GET /exams/{exam_id}` - Lấy đề thi theo ID
- `POST /exams/` - Tạo đề thi mới
- `GET /exams/{exam_id}/preview` - Xem preview đề thi
- `POST /exams/{exam_id}/versions` - Thêm version cho đề thi

### Import

- `POST /import/preview` - Preview DOCX file
- `POST /import/docx` - Import DOCX file

## 📋 Template DOCX Format

File DOCX phải theo format chuẩn:

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

### Quy Tắc Format

- **Subject**: Tên môn học
- **Number of Quiz**: Số lượng câu hỏi
- **Lecturer**: Tên giảng viên
- **Date**: Ngày tháng năm
- **QN=**: Số thứ tự câu hỏi
- **[file:filename.jpg]**: Tham chiếu ảnh (tùy chọn)
- **ANSWER**: Đáp án đúng (A, B, C, D)
- **MARK**: Điểm câu hỏi
- **UNIT**: Đơn vị bài học
- **MIX CHOICES**: Có xáo trộn đáp án không (Yes/No)

## 🗄️ Database Schema

### Tables

- `users` - Thông tin người dùng
- `subjects` - Môn học
- `questions` - Câu hỏi (bao gồm trường image)
- `choices` - Đáp án
- `exams` - Khuôn đề
- `exam_versions` - Phiên bản đề
- `exam_version_questions` - Snapshot câu hỏi sau xáo trộn

## 🔒 Bảo Mật

- **Password Hashing**: Sử dụng bcrypt để mã hóa mật khẩu
- **Role-based Access Control**: Phân quyền theo vai trò
- **Input Validation**: Kiểm tra dữ liệu đầu vào
- **Error Handling**: Xử lý lỗi an toàn

## 🧪 Testing

### Test CRUD và Exam Generation

```bash
python test_crud_and_exam_generation.py
```

Script test sẽ kiểm tra:

- CRUD operations cho câu hỏi
- Tạo đề thi với xáo trộn đáp án
- Thêm phiên bản mới cho đề thi
- Hiển thị ảnh trong preview

## 🐛 Troubleshooting

### Lỗi Kết Nối Database

```bash
# Kiểm tra PostgreSQL container
docker ps | grep python_project

# Kiểm tra logs
docker logs python_project
```

### Lỗi Import DOCX

- Kiểm tra format file DOCX có đúng template không
- Kiểm tra thư mục `uploads/` có tồn tại không
- Kiểm tra quyền ghi file

### Lỗi Hiển Thị Ảnh

- Kiểm tra thư mục `images/` có tồn tại không
- Kiểm tra tên file ảnh trong database có khớp với file thực tế không
- Kiểm tra quyền đọc file ảnh

### Lỗi CRUD Operations

- Kiểm tra API server có đang chạy không
- Kiểm tra quyền truy cập database
- Kiểm tra log lỗi trong console

## 📝 Changelog

### Version 2.0.0

- ✅ Thêm hỗ trợ hiển thị ảnh trong preview đề thi
- ✅ Cải thiện UI/UX cho exam preview
- ✅ Thêm validation cho số câu hỏi
- ✅ Cập nhật dependencies

### Version 1.0.0

- ✅ Hệ thống authentication
- ✅ Import DOCX
- ✅ CRUD operations cho câu hỏi
- ✅ Tạo đề thi với xáo trộn đáp án
- ✅ Role-based access control

## 🤝 Contributing

1. Fork project
2. Tạo feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Tạo Pull Request

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

## 📞 Support

Nếu bạn gặp vấn đề, vui lòng:

1. Kiểm tra phần Troubleshooting
2. Tạo issue trên GitHub
3. Liên hệ maintainer

---

**Made with ❤️ by Python Team**
