DISCUSSION_NORMAL = [
    {
        "id": 1,
        "depth": 0,
        "author": "Minh An",
        "title": "Decision Tree bị overfitting",
        "content": "Chào mọi người, em đang làm bài tập lớn về Decision Tree "
        "nhưng không hiểu tại sao độ chính xác trên tập test lại thấp hơn "
        "nhiều so với tập train. Có ai gặp trường hợp này chưa?",
    },
    {
        "id": 2,
        "depth": 1,
        "author": "TA Huy",
        "title": "Re: Decision Tree bị overfitting",
        "content": "Đây là dấu hiệu của overfitting. Em thử giảm max_depth "
        "của cây hoặc tăng min_samples_leaf xem độ chính xác trên test có "
        "cải thiện không.",
    },
    {
        "id": 3,
        "depth": 2,
        "author": "Minh An",
        "title": "Re: Decision Tree bị overfitting",
        "content": "Em cảm ơn thầy, em thử giảm max_depth từ 10 xuống 5 thì "
        "độ chính xác trên test tăng từ 68% lên 82%, đúng là overfitting thật.",
    },
    {
        "id": 4,
        "depth": 0,
        "author": "Lan Phương",
        "title": "Deadline nộp báo cáo bài tập lớn",
        "content": "Cho em hỏi deadline nộp báo cáo bài tập lớn này là ngày "
        "nào vậy ạ? Em không thấy ghi rõ trên trang môn học.",
    },
    {
        "id": 5,
        "depth": 0,
        "author": "Quốc Bảo",
        "title": "Xử lý dữ liệu mất cân bằng nhãn",
        "content": "Em cũng dùng Decision Tree nhưng dữ liệu của em bị mất "
        "cân bằng nhãn (class imbalance), có cách nào xử lý không ạ?",
    },
    {
        "id": 6,
        "depth": 1,
        "author": "TA Huy",
        "title": "Re: Xử lý dữ liệu mất cân bằng nhãn",
        "content": "Với dữ liệu mất cân bằng, em có thể dùng class_weight="
        "'balanced' trong sklearn, hoặc áp dụng kỹ thuật oversampling như "
        "SMOTE cho lớp thiểu số.",
    },
]
