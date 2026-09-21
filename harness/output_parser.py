import json
import re

from pydantic import ValidationError

from schemas import SummaryOutput

CODE_FENCE_PATTERN = re.compile(
    r"```(?:json)?\s*(.*?)\s*```", re.DOTALL | re.IGNORECASE
)
THINK_TAG_PATTERN = re.compile(r"<think>.*?</think>", re.DOTALL | re.IGNORECASE)


class OutputParserError(Exception):
    pass


class OutputParser:
    """Parses the JSON returned by the model, handling output wrapped in
    ```json``` or accompanied by <think>...</think>, then validates it
    with Pydantic."""

    def _strip_think_tags(self, raw: str) -> str:
        return THINK_TAG_PATTERN.sub("", raw).strip()

    def _extract_json_text(self, raw: str) -> str:
        text = self._strip_think_tags(raw)

        match = CODE_FENCE_PATTERN.search(text)
        if match:
            return match.group(1).strip()

        # No code fence: try to find the first JSON object in the text by
        # taking everything from the first { to the last }.
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            return text[start : end + 1].strip()

        return text.strip()

    def parse(self, raw_output: str) -> SummaryOutput:
        json_text = self._extract_json_text(raw_output)

        try:
            data = json.loads(json_text)
        except json.JSONDecodeError as exc:
            raise OutputParserError(
                f"Model không trả về JSON hợp lệ: {exc}\n"
                f"--- Raw output ---\n{raw_output}"
            ) from exc

        try:
            return SummaryOutput.model_validate(data)
        except ValidationError as exc:
            raise OutputParserError(
                f"JSON trả về không khớp schema SummaryOutput: {exc}\n"
                f"--- Parsed JSON ---\n{json.dumps(data, ensure_ascii=False)}"
            ) from exc
