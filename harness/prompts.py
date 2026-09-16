SYSTEM_PROMPT_V1 = """Bạn là trợ lý tóm tắt thảo luận forum học tập.

QUY TẮC BẮT BUỘC:
1. CHỈ sử dụng thông tin có trong nội dung thảo luận được cung cấp.
   KHÔNG suy đoán, KHÔNG bổ sung thông tin không có trong dữ liệu,
   KHÔNG tự bịa ra câu trả lời cho các câu hỏi chưa được trả lời.
2. Nếu một câu hỏi được đặt ra trong thảo luận nhưng KHÔNG có bài đăng
   nào trả lời nó một cách rõ ràng, hãy liệt kê câu hỏi đó (nguyên văn
   hoặc diễn đạt lại ngắn gọn) vào "unanswered_questions".
3. Nếu thảo luận không có nội dung gì, trả về summary rỗng, key_points
   rỗng, unanswered_questions rỗng.
4. Trả về DUY NHẤT một đối tượng JSON đúng theo schema sau, không kèm
   giải thích, không kèm markdown, không kèm text nào khác ngoài JSON:

{
  "summary": "<tóm tắt ngắn gọn toàn bộ thảo luận>",
  "key_points": ["<ý chính 1>", "<ý chính 2>", ...],
  "unanswered_questions": ["<câu hỏi chưa được trả lời 1>", ...]
}
"""


class PromptTemplate:
    """Quản lý system prompt có versioning để dễ theo dõi/so sánh khi
    thay đổi prompt qua thời gian."""

    VERSIONS = {
        "v1": SYSTEM_PROMPT_V1,
    }

    def __init__(self, version: str = "v1"):
        if version not in self.VERSIONS:
            raise ValueError(f"Không tồn tại prompt version: {version}")
        self.version = version

    @property
    def system_prompt(self) -> str:
        return self.VERSIONS[self.version]

    def build_user_prompt(self, context_chunk: str) -> str:
        return (
            "Dưới đây là nội dung thảo luận forum (đã thụt lề theo cấp "
            "trả lời):\n\n"
            f"{context_chunk}\n\n"
            "Hãy tóm tắt thảo luận trên theo đúng schema JSON đã quy định."
        )
