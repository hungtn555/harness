import json
import time
from contextlib import contextmanager


class HarnessLogger:
    """In ra JSON log có cấu trúc cho mỗi lần chạy harness: feature,
    prompt_version, model, tokens_used, duration_seconds, success."""

    def __init__(self, feature: str, prompt_version: str, model: str):
        self.feature = feature
        self.prompt_version = prompt_version
        self.model = model

    def log(self, tokens_used: int, duration_seconds: float, success: bool, error: str | None = None):
        record = {
            "feature": self.feature,
            "prompt_version": self.prompt_version,
            "model": self.model,
            "tokens_used": tokens_used,
            "duration_seconds": round(duration_seconds, 3),
            "success": success,
        }
        if error is not None:
            record["error"] = error
        print(json.dumps(record, ensure_ascii=False))
        return record

    @contextmanager
    def track(self):
        """Context manager tiện dụng: đo thời gian chạy, tự log kết quả.
        Dùng: with logger.track() as t: ... ; t.tokens_used = N"""

        class _Tracker:
            tokens_used: int = 0

        tracker = _Tracker()
        start = time.monotonic()
        try:
            yield tracker
        except Exception as exc:
            duration = time.monotonic() - start
            self.log(tracker.tokens_used, duration, success=False, error=str(exc))
            raise
        else:
            duration = time.monotonic() - start
            self.log(tracker.tokens_used, duration, success=True)
