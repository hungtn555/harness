import os
import time

import requests
from dotenv import load_dotenv

load_dotenv()  # đọc file .env ở thư mục làm việc (không ghi đè biến môi trường đã set sẵn)

VLLM_BASE_URL = os.getenv("VLLM_BASE_URL", "http://localhost:8000/v1/chat/completions")
VLLM_API_KEY = os.getenv("VLLM_API_KEY")
DEFAULT_MODEL = os.getenv("VLLM_MODEL", "llama3.1")
DEFAULT_TIMEOUT = 60
MAX_RETRIES = 3
BACKOFF_SECONDS = [1, 2, 4]

if not VLLM_API_KEY:
    raise RuntimeError(
        "VLLM_API_KEY chưa được set. Hãy thêm nó vào file .env hoặc biến môi trường."
    )


class ModelClientError(Exception):
    pass


class ModelClient:
    """Calls vLLM through its OpenAI-compatible /v1/chat/completions endpoint,
    retrying with backoff on connection errors. A read timeout is NOT retried:
    the model is just slow, and a retry would only repeat the same long wait."""

    def __init__(
        self,
        model: str = DEFAULT_MODEL,
        base_url: str = VLLM_BASE_URL,
        api_key: str | None = VLLM_API_KEY,
        timeout: int = DEFAULT_TIMEOUT,
    ):
        self.model = model
        self.base_url = base_url
        self.api_key = api_key
        self.timeout = timeout

    def chat(
        self, system_prompt: str, user_prompt: str, deadline: float | None = None
    ) -> dict:
        """Sends a chat request to vLLM and returns a dict with:
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
            "temperature": 0,
            "response_format": {"type": "json_object"},
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        last_error: Exception | None = None

        for attempt in range(MAX_RETRIES):
            timeout = self.timeout
            if deadline is not None:
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    raise ModelClientError(
                        "Time budget for this request was used up before vLLM answered"
                    ) from last_error
                timeout = min(timeout, remaining)

            try:
                # print(f"[DEBUG] Calling URL: {self.base_url}")
                response = requests.post(
                    self.base_url, json=payload, headers=headers, timeout=timeout,
                    verify = False,
                )
                response.raise_for_status()
                data = response.json()

                choice = (data.get("choices") or [{}])[0]
                message = choice.get("message", {})
                content = message.get("content", "")
                usage = data.get("usage", {})
                prompt_tokens = usage.get("prompt_tokens", 0)
                completion_tokens = usage.get("completion_tokens", 0)

                return {
                    "content": content,
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                    "total_tokens": usage.get(
                        "total_tokens", prompt_tokens + completion_tokens
                    ),
                }
            except requests.exceptions.ReadTimeout as exc:
                raise ModelClientError(
                    f"vLLM did not answer within {timeout:.0f}s: {exc}"
                ) from exc
            except requests.exceptions.HTTPError as exc:
                status = exc.response.status_code if exc.response is not None else None
                if status in (401, 403):
                    raise ModelClientError(
                        f"vLLM từ chối request (HTTP {status}) — kiểm tra lại VLLM_API_KEY: {exc}"
                    ) from exc
                raise ModelClientError(f"vLLM request failed: {exc}") from exc
            except requests.exceptions.ConnectionError as exc:
                # Includes ConnectTimeout. Server may still be starting up.
                last_error = exc
                if attempt < MAX_RETRIES - 1:
                    time.sleep(BACKOFF_SECONDS[attempt])
                continue
            except requests.exceptions.RequestException as exc:
                raise ModelClientError(f"vLLM request failed: {exc}") from exc

        raise ModelClientError(
            f"Could not reach vLLM after {MAX_RETRIES} attempts: {last_error}"
        ) from last_error


# import time

# import requests

# OLLAMA_CHAT_URL = "http://localhost:11434/api/chat"
# DEFAULT_MODEL = "llama3.1:latest "
# DEFAULT_TIMEOUT = 60
# MAX_RETRIES = 3
# BACKOFF_SECONDS = [1, 2, 4]


# class ModelClientError(Exception):
#     pass


# class ModelClient:
#     """Calls Ollama through /api/chat, retrying with backoff on connection
#     errors. A read timeout is NOT retried: the model is just slow, and a retry
#     would only repeat the same long wait."""

#     def __init__(
#         self,
#         model: str = DEFAULT_MODEL,
#         base_url: str = OLLAMA_CHAT_URL,
#         timeout: int = DEFAULT_TIMEOUT,
#     ):
#         self.model = model
#         self.base_url = base_url
#         self.timeout = timeout

#     def chat(
#         self, system_prompt: str, user_prompt: str, deadline: float | None = None
#     ) -> dict:
#         """Sends a chat request to Ollama and returns a dict with:
#         content (str), prompt_tokens, completion_tokens, total_tokens.

#         deadline is an optional time.monotonic() value shared by every call of
#         one request: each attempt's timeout is capped by the time left, so the
#         whole request never runs past it.
#         Raises ModelClientError if it fails, times out or runs out of time."""
#         payload = {
#             "model": self.model,
#             "messages": [
#                 {"role": "system", "content": system_prompt},
#                 {"role": "user", "content": user_prompt},
#             ],
#             "stream": False,
#             "think": False,
#             "format": "json",
#             "options": {"temperature": 0},
#         }

#         last_error: Exception | None = None

#         for attempt in range(MAX_RETRIES):
#             timeout = self.timeout
#             if deadline is not None:
#                 remaining = deadline - time.monotonic()
#                 if remaining <= 0:
#                     raise ModelClientError(
#                         "Time budget for this request was used up before Ollama answered"
#                     ) from last_error
#                 timeout = min(timeout, remaining)

#             try:
#                 response = requests.post(
#                     self.base_url, json=payload, timeout=timeout
#                 )
#                 response.raise_for_status()
#                 data = response.json()

#                 message = data.get("message", {})
#                 content = message.get("content", "")
#                 prompt_tokens = data.get("prompt_eval_count", 0)
#                 completion_tokens = data.get("eval_count", 0)

#                 return {
#                     "content": content,
#                     "prompt_tokens": prompt_tokens,
#                     "completion_tokens": completion_tokens,
#                     "total_tokens": prompt_tokens + completion_tokens,
#                 }
#             except requests.exceptions.ReadTimeout as exc:
#                 raise ModelClientError(
#                     f"Ollama did not answer within {timeout:.0f}s: {exc}"
#                 ) from exc
#             except requests.exceptions.ConnectionError as exc:
#                 # Includes ConnectTimeout. Ollama may still be starting up.
#                 last_error = exc
#                 if attempt < MAX_RETRIES - 1:
#                     time.sleep(BACKOFF_SECONDS[attempt])
#                 continue
#             except requests.exceptions.RequestException as exc:
#                 raise ModelClientError(f"Ollama request failed: {exc}") from exc

#         raise ModelClientError(
#             f"Could not reach Ollama after {MAX_RETRIES} attempts: {last_error}"
#         ) from last_error
