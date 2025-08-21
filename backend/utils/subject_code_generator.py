"""
Utility để generate subject code từ tên môn học
"""

def generate_subject_code(subject_name: str) -> str:
    """
    Generate subject code từ tên môn học
    Ví dụ: "Information Systems" -> "IS"
    """
    if not subject_name:
        return "SUB"
    
    # Loại bỏ các từ không cần thiết
    stop_words = ['cơ bản', 'nâng cao', 'cơ sở', 'chuyên ngành', 'học', 'môn']
    
    # Chuyển về lowercase và tách từ
    words = subject_name.lower().split()
    
    # Lọc bỏ stop words
    filtered_words = [word for word in words if word not in stop_words]
    
    if not filtered_words:
        # Nếu không có từ nào, lấy 3 ký tự đầu
        return subject_name[:3].upper()
    
    # Lấy chữ cái đầu của mỗi từ
    code = ''.join([word[0].upper() for word in filtered_words])
    
    # Giới hạn độ dài tối đa 4 ký tự
    return code[:4]

def generate_exam_code(subject_code: str, exam_number: int) -> str:
    """
    Generate mã đề thi theo format: {Subject Code}-{Number}
    Ví dụ: ISC-001, ISC-002...
    """
    return f"{subject_code}-{exam_number:03d}"

def get_next_exam_number(subject_id: int, subject_code: str) -> int:
    """
    Lấy số thứ tự tiếp theo cho đề thi của môn học
    """
    from ..database import db
    
    try:
        # Tìm đề thi cuối cùng của môn học này
        query = """
            SELECT code FROM exams 
            WHERE subject_id = %s 
            AND code LIKE %s
            ORDER BY code DESC 
            LIMIT 1
        """
        pattern = f"{subject_code}-%"
        result = db.execute_single(query, (subject_id, pattern))
        
        if result:
            # Lấy số từ mã đề cuối cùng
            last_code = result['code']
            try:
                last_number = int(last_code.split('-')[-1])
                return last_number + 1
            except (ValueError, IndexError):
                return 1
        else:
            return 1
            
    except Exception as e:
        print(f"Error getting next exam number: {e}")
        return 1 