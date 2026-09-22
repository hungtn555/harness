import time

import requests

OLLAMA_CHAT_URL = "http://localhost:11434/api/chat"
DEFAULT_MODEL = "qwen3.5:0.8b"
DEFAULT_TIMEOUT = 60
MAX_RETRIES = 3
BACKOFF_SECONDS = [1, 2, 4]


class ModelClientError(Exception):
    pass


class ModelClient:
    """Calls Ollama through /api/chat, retrying with backoff on connection
    errors. A read timeout is NOT retried: the model is just slow, and a retry
    would only repeat the same long wait."""

    def __init__(
        self,
        model: str = DEFAULT_MODEL,
        base_url: str = OLLAMA_CHAT_URL,
        timeout: int = DEFAULT_TIMEOUT,
    ):
        self.model = model
        self.base_url = base_url
        self.timeout = timeout

    def chat(
        self, system_prompt: str, user_prompt: str, deadline: float | None = None
    ) -> dict:
        """Sends a chat request to Ollama and returns a dict with:
        content (str), prompt_tokens, completion_tokens, total_tokens.

        deadline is an optional time.monotonic() value shared by every call of
        one request: each attempt's timeout is capped by the time left, so the
        whole request never runs past it.
        Raises ModelClientError if it fails, times out or runs out of time."""
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "stream": False,
            "think": False,
            "format": "json",
            "options": {"temperature": 0},
        }

        last_error: Exception | None = None

        for attempt in range(MAX_RETRIES):
            timeout = self.timeout
            if deadline is not None:
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    raise ModelClientError(
                        "Time budget for this request was used up before Ollama answered"
                    ) from last_error
                timeout = min(timeout, remaining)

            try:
                response = requests.post(
                    self.base_url, json=payload, timeout=timeout
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
            except requests.exceptions.ReadTimeout as exc:
                raise ModelClientError(
                    f"Ollama did not answer within {timeout:.0f}s: {exc}"
                ) from exc
            except requests.exceptions.ConnectionError as exc:
                # Includes ConnectTimeout. Ollama may still be starting up.
                last_error = exc
                if attempt < MAX_RETRIES - 1:
                    time.sleep(BACKOFF_SECONDS[attempt])
                continue
            except requests.exceptions.RequestException as exc:
                raise ModelClientError(f"Ollama request failed: {exc}") from exc

        raise ModelClientError(
            f"Could not reach Ollama after {MAX_RETRIES} attempts: {last_error}"
        ) from last_error
