# Bộ dữ liệu thảo luận forum giả lập dùng để kiểm tra Harness.
# Mỗi bài đăng có dạng: {id, depth, author, content}

DISCUSSION_NORMAL = [
    {
        "id": 1,
        "depth": 0,
        "author": "Minh An",
        "content": "Chào mọi người, em đang làm bài tập lớn về Decision Tree "
        "nhưng không hiểu tại sao độ chính xác trên tập test lại thấp hơn "
        "nhiều so với tập train. Có ai gặp trường hợp này chưa?",
    },
    {
        "id": 2,
        "depth": 1,
        "author": "TA Huy",
        "content": "Đây là dấu hiệu của overfitting. Em thử giảm max_depth "
        "của cây hoặc tăng min_samples_leaf xem độ chính xác trên test có "
        "cải thiện không.",
    },
    {
        "id": 3,
        "depth": 2,
        "author": "Minh An",
        "content": "Em cảm ơn thầy, em thử giảm max_depth từ 10 xuống 5 thì "
        "độ chính xác trên test tăng từ 68% lên 82%, đúng là overfitting thật.",
    },
    {
        "id": 4,
        "depth": 0,
        "author": "Lan Phương",
        "content": "Cho em hỏi deadline nộp báo cáo bài tập lớn này là ngày "
        "nào vậy ạ? Em không thấy ghi rõ trên trang môn học.",
    },
    {
        "id": 5,
        "depth": 0,
        "author": "Quốc Bảo",
        "content": "Em cũng dùng Decision Tree nhưng dữ liệu của em bị mất "
        "cân bằng nhãn (class imbalance), có cách nào xử lý không ạ?",
    },
    {
        "id": 6,
        "depth": 1,
        "author": "TA Huy",
        "content": "Với dữ liệu mất cân bằng, em có thể dùng class_weight="
        "'balanced' trong sklearn, hoặc áp dụng kỹ thuật oversampling như "
        "SMOTE cho lớp thiểu số.",
    },
]

DISCUSSION_NO_ANSWER = [
    {
        "id": 1,
        "depth": 0,
        "author": "Thu Hà",
        "content": "Môn này có được dùng thư viện PyTorch thay cho "
        "TensorFlow khi làm bài tập lớn không ạ? Đề bài không ghi rõ.",
    },
    {
        "id": 2,
        "depth": 0,
        "author": "Đức Anh",
        "content": "Em nộp bài tập lớn qua Moodle rồi nhưng không thấy hệ "
        "thống xác nhận đã nhận bài, có ai biết cách kiểm tra lại không?",
    },
]

DISCUSSION_MIXED_LANGUAGE = [
    {
        "id": 1,
        "depth": 0,
        "author": "Việt Hoàng",
        "content": "Em chạy training trên GPU bị lỗi "
        "ModuleNotFoundError: No module named 'torch', mặc dù em đã cài "
        "PyTorch bằng pip rồi.",
    },
    {
        "id": 2,
        "depth": 1,
        "author": "TA Mai",
        "content": "Em check lại xem đã activate đúng virtual environment "
        "chưa, và kiểm tra `pip list` trong env đó có torch không.",
    },
    {
        "id": 3,
        "depth": 2,
        "author": "Việt Hoàng",
        "content": "À em quên activate venv, giờ cài lại thì chạy được rồi. "
        "Nhưng training rất chậm, em có nên dùng CUDA không ạ?",
    },
    {
        "id": 4,
        "depth": 3,
        "author": "TA Mai",
        "content": "Có, nếu máy có GPU NVIDIA thì nên cài bản PyTorch hỗ trợ "
        "CUDA. Em cũng nên giảm batch_size nếu bị lỗi out of memory.",
    },
    {
        "id": 5,
        "depth": 4,
        "author": "Việt Hoàng",
        "content": "Em để batch_size=64 thì bị CUDA out of memory, giảm "
        "xuống batch_size=16 thì chạy ổn, cảm ơn thầy/cô!",
    },
]

DISCUSSION_EMPTY: list[dict] = []
