import time

import requests

OLLAMA_CHAT_URL = "http://localhost:11434/api/chat"
DEFAULT_MODEL = "qwen3:1.7b"
DEFAULT_TIMEOUT = 60
MAX_RETRIES = 3
BACKOFF_SECONDS = [1, 2, 4]


class ModelClientError(Exception):
    pass


class ModelClient:
    """Gọi Ollama qua /api/chat, có retry với backoff khi gặp lỗi
    timeout/connection."""

    def __init__(
        self,
        model: str = DEFAULT_MODEL,
        base_url: str = OLLAMA_CHAT_URL,
        timeout: int = DEFAULT_TIMEOUT,
    ):
        self.model = model
        self.base_url = base_url
        self.timeout = timeout

    def chat(self, system_prompt: str, user_prompt: str) -> dict:
        """Gửi request chat tới Ollama, trả về dict gồm:
        content (str), prompt_tokens, completion_tokens, total_tokens.
        Ném ModelClientError nếu thất bại sau toàn bộ số lần retry."""
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "stream": False,
            "think": False,
            "format": "json",          # <-- thêm dòng này
            "options": {"temperature": 0},
        }


        last_error: Exception | None = None

        for attempt in range(MAX_RETRIES):
            try:
                response = requests.post(
                    self.base_url, json=payload, timeout=self.timeout
                )
                response.raise_for_status()
                data = response.json()

                message = data.get("message", {})
                content = message.get("content", "")
                prompt_tokens = data.get("prompt_eval_count", 0)
                completion_tokens = data.get("eval_count", 0)

                return {
                    "content": content,
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                    "total_tokens": prompt_tokens + completion_tokens,
                }
            except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as exc:
                last_error = exc
                if attempt < MAX_RETRIES - 1:
                    time.sleep(BACKOFF_SECONDS[attempt])
                continue
            except requests.exceptions.RequestException as exc:
                raise ModelClientError(f"Lỗi gọi Ollama: {exc}") from exc

        raise ModelClientError(
            f"Gọi Ollama thất bại sau {MAX_RETRIES} lần thử: {last_error}"
        ) from last_error
