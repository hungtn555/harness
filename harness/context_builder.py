MAX_CHUNK_CHARS = 8000
INDENT_UNIT = "  "


class ContextBuilder:
    """Ghép danh sách bài đăng forum thành text có thụt lề theo depth,
    rồi cắt thành các chunk tối đa MAX_CHUNK_CHARS ký tự, chỉ cắt tại
    ranh giới giữa các bài đăng (không cắt giữa nội dung 1 bài)."""

    def __init__(self, max_chunk_chars: int = MAX_CHUNK_CHARS):
        self.max_chunk_chars = max_chunk_chars

    def _format_post(self, post: dict) -> str:
        depth = post.get("depth", 0)
        indent = INDENT_UNIT * depth
        post_id = post["id"]
        author = post["author"]
        content = post["content"]
        return f"{indent}[Bài #{post_id}] {author}: {content}"

    def build(self, posts: list[dict]) -> list[str]:
        """Trả về list các chunk text. Nếu posts rỗng, trả về list rỗng."""
        if not posts:
            return []

        formatted_lines = [self._format_post(p) for p in posts]

        chunks: list[str] = []
        current_lines: list[str] = []
        current_len = 0

        for line in formatted_lines:
            line_len = len(line) + 1  # +1 cho ký tự newline nối giữa các bài

            # Nếu một bài đăng đơn lẻ đã vượt quá max_chunk_chars, vẫn giữ
            # nguyên nó thành 1 chunk riêng (không cắt giữa nội dung bài đó).
            if current_lines and current_len + line_len > self.max_chunk_chars:
                chunks.append("\n".join(current_lines))
                current_lines = []
                current_len = 0

            current_lines.append(line)
            current_len += line_len

        if current_lines:
            chunks.append("\n".join(current_lines))

        return chunks
