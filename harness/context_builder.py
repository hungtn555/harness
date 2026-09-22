MAX_CHUNK_CHARS = 8000
INDENT_UNIT = "  "


class ContextBuilder:
    """Joins forum posts into text indented by depth, then splits it into
    chunks of at most MAX_CHUNK_CHARS characters, cutting only at post
    boundaries (never in the middle of a post)."""

    def __init__(self, max_chunk_chars: int = MAX_CHUNK_CHARS):
        self.max_chunk_chars = max_chunk_chars

    def _format_post(self, post: dict) -> str:
        depth = post.get("depth", 0)
        indent = INDENT_UNIT * depth
        author = post["author"]
        title = post.get("title")
        content = post["content"]
        return f'{indent}{author} - "{title}": {content}'
        
    def build(self, posts: list[dict]) -> list[str]:
        """Returns a list of text chunks. If posts is empty, returns an empty list."""
        if not posts:
            return []

        formatted_lines = [self._format_post(p) for p in posts]

        chunks: list[str] = []
        current_lines: list[str] = []
        current_len = 0

        for line in formatted_lines:
            line_len = len(line) + 1  # +1 for the newline joining the posts

            # If a single post already exceeds max_chunk_chars, keep it as its
            # own chunk (never cut in the middle of a post).
            if current_lines and current_len + line_len > self.max_chunk_chars:
                chunks.append("\n".join(current_lines))
                current_lines = []
                current_len = 0

            current_lines.append(line)
            current_len += line_len

        if current_lines:
            chunks.append("\n".join(current_lines))

        return chunks
