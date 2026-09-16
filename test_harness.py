import sys
import time

if sys.stdout.encoding is None or sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

from harness.context_builder import ContextBuilder
from harness.logger import HarnessLogger
from harness.model_client import ModelClient, ModelClientError
from harness.output_parser import OutputParser, OutputParserError
from harness.prompts import PromptTemplate
from sample_data import (
    DISCUSSION_EMPTY,
    DISCUSSION_MIXED_LANGUAGE,
    DISCUSSION_NO_ANSWER,
    DISCUSSION_NORMAL,
)

SEPARATOR = "=" * 78


def print_result(name: str, duration: float, tokens: int, result):
    print(SEPARATOR)
    print(f"BO DU LIEU: {name}")
    print(SEPARATOR)
    print(f"Thoi gian chay : {duration:.2f}s")
    print(f"So token dung  : {tokens}")
    print()
    print("--- SUMMARY ---")
    print(result.summary or "(rong)")
    print()
    print("--- KEY POINTS ---")
    if result.key_points:
        for i, kp in enumerate(result.key_points, 1):
            print(f"  {i}. {kp}")
    else:
        print("  (rong)")
    print()
    print(">>> UNANSWERED_QUESTIONS (QUAN TRONG NHAT) <<<")
    if result.unanswered_questions:
        for i, q in enumerate(result.unanswered_questions, 1):
            print(f"  *** {i}. {q}")
    else:
        print("  *** (khong co cau hoi nao chua duoc tra loi) ***")
    print()


def run_discussion(name: str, posts: list[dict], prompt_version: str = "v1"):
    builder = ContextBuilder()
    chunks = builder.build(posts)

    # Dữ liệu rỗng: TỰ CHẶN, không gọi model.
    if not chunks:
        print(SEPARATOR)
        print(f"BO DU LIEU: {name}")
        print(SEPARATOR)
        print("Danh sach bai dang RONG -> tu chan, KHONG goi model.")
        print()
        return

    template = PromptTemplate(version=prompt_version)
    client = ModelClient()
    parser = OutputParser()
    logger = HarnessLogger(
        feature="forum_summary", prompt_version=prompt_version, model=client.model
    )

    # Giả định trường hợp test: mỗi discussion chỉ sinh 1 chunk (do đủ nhỏ
    # hơn giới hạn 8000 ký tự). Nếu có nhiều chunk, chỉ xử lý chunk đầu
    # trong phạm vi bài test này.
    context_chunk = chunks[0]
    user_prompt = template.build_user_prompt(context_chunk)

    start = time.monotonic()
    tokens_used = 0
    try:
        response = client.chat(template.system_prompt, user_prompt)
        tokens_used = response["total_tokens"]
        result = parser.parse(response["content"])
        duration = time.monotonic() - start
        logger.log(tokens_used, duration, success=True)
        print_result(name, duration, tokens_used, result)
    except (ModelClientError, OutputParserError) as exc:
        duration = time.monotonic() - start
        logger.log(tokens_used, duration, success=False, error=str(exc))
        print(SEPARATOR)
        print(f"BO DU LIEU: {name} -> LOI")
        print(SEPARATOR)
        print(str(exc))
        print()


def main():
    run_discussion("DISCUSSION_NORMAL", DISCUSSION_NORMAL)
    run_discussion("DISCUSSION_NO_ANSWER", DISCUSSION_NO_ANSWER)
    run_discussion("DISCUSSION_MIXED_LANGUAGE", DISCUSSION_MIXED_LANGUAGE)
    run_discussion("DISCUSSION_EMPTY", DISCUSSION_EMPTY)


if __name__ == "__main__":
    main()
