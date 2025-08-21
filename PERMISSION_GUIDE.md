# Hướng dẫn sử dụng chức năng phân quyền cho Editor

## 🎯 **Tổng quan**

Hệ thống đã được cập nhật để hỗ trợ phân quyền chi tiết cho Editor. Mỗi editor chỉ có thể thấy và sửa được các môn học mà họ được phân công.

## 👥 **Phân công môn học**

### **Editor 1 (user_id=2)**

- **Username**: "2"
- **Password**: "2"
- **Môn học được phân công**:
  - Toán học cơ bản
  - Tiếng Việt

### **Editor 2 (user_id=4)**

- **Username**: "4"
- **Password**: "4"
- **Môn học được phân công**:
  - Khoa học tự nhiên
  - Lịch sử Việt Nam

### **Editor 3 (user_id=5)**

- **Username**: "5"
- **Password**: "5"
- **Môn học được phân công**:
  - Địa lý Việt Nam
  - Tiếng Anh cơ bản

## 🔐 **Cấu trúc phân quyền**

### **Roles và quyền hạn:**

- **Importer**: Có quyền truy cập tất cả môn học
- **Generator**: Có quyền truy cập tất cả môn học
- **Editor**: Chỉ thấy và sửa được môn học được phân công

### **Quyền của Editor:**

- ✅ Xem danh sách môn học được phân công
- ✅ Xem câu hỏi của môn học được phân công
- ✅ Tạo câu hỏi mới cho môn học được phân công
- ✅ Sửa câu hỏi của môn học được phân công
- ✅ Xóa câu hỏi của môn học được phân công
- ❌ Không thể truy cập môn học khác

## 🚀 **Cách sử dụng**

### **1. Khởi động server:**

```bash
python -m backend.main
```

### **2. Đăng nhập với editor:**

- Editor 1: username="2", password="2"
- Editor 2: username="4", password="4"
- Editor 3: username="5", password="5"

### **3. Test chức năng:**

```bash
python test_permissions.py
```

## 📋 **API Endpoints**

### **Authentication:**

- `POST /auth/login` - Đăng nhập
- `POST /auth/logout` - Đăng xuất

### **Subjects:**

- `GET /subjects` - Lấy danh sách môn học (chỉ môn được phân công cho editor)

### **Questions:**

- `GET /questions` - Lấy tất cả câu hỏi (chỉ môn được phân công cho editor)
- `GET /questions?subject_id=X` - Lấy câu hỏi theo môn học (kiểm tra quyền)
- `GET /questions/{id}` - Lấy câu hỏi theo ID (kiểm tra quyền)
- `POST /questions` - Tạo câu hỏi mới (kiểm tra quyền)
- `PUT /questions/{id}` - Sửa câu hỏi (kiểm tra quyền)
- `DELETE /questions/{id}` - Xóa câu hỏi (kiểm tra quyền)

## ⚠️ **Error Messages**

Khi editor cố gắng truy cập môn học không được phân công:

```
{
  "detail": "Môn học này không thuộc bạn quản lý"
}
```

## 🔧 **Files đã tạo/cập nhật**

### **Models:**

- `backend/models/user_subject.py` - Quản lý phân công môn học

### **Middleware:**

- `backend/middleware/auth.py` - Kiểm tra quyền truy cập
- `backend/middleware/session.py` - Quản lý session

### **Routes (đã cập nhật):**

- `backend/routes/questions.py` - Thêm kiểm tra quyền
- `backend/routes/subjects.py` - Thêm kiểm tra quyền
- `backend/routes/auth.py` - Thêm session management

### **Scripts:**

- `backend/scripts/setup_editors.py` - Thiết lập editor và phân công
- `test_permissions.py` - Test chức năng phân quyền

## 🎯 **Kết quả test**

### **Editor 1 (Toán + Văn):**

- ✅ Thấy được Toán học và Tiếng Việt
- ✅ Có thể truy cập câu hỏi Toán học
- ❌ Không thể truy cập Khoa học

### **Editor 2 (Khoa học + Lịch sử):**

- ✅ Thấy được Khoa học và Lịch sử
- ✅ Có thể truy cập câu hỏi Khoa học
- ❌ Không thể truy cập Toán học

### **Editor 3 (Địa lý + Tiếng Anh):**

- ✅ Thấy được Địa lý và Tiếng Anh
- ✅ Có thể truy cập câu hỏi Địa lý
- ❌ Không thể truy cập Toán học

## 🔄 **Thiết lập lại hệ thống**

Nếu cần thiết lập lại:

```bash
cd backend/scripts
python setup_editors.py
```

## 📝 **Lưu ý**

1. **Session Management**: Hệ thống sử dụng session đơn giản để lưu thông tin user
2. **Database**: Bảng `user_subjects` đã được tạo và có dữ liệu phân công
3. **Security**: Chỉ editor mới bị giới hạn quyền, admin vẫn có quyền truy cập tất cả
4. **Error Handling**: Tất cả API đều có xử lý lỗi phù hợp

## ✅ **Hoàn thành**

Chức năng phân quyền đã được implement hoàn chỉnh và sẵn sàng sử dụng! Editor giờ đây chỉ có thể thấy và sửa được các môn học mà họ được phân công, đúng như yêu cầu của bạn.
