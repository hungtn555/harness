import time

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from harness.context_builder import ContextBuilder
from harness.logger import HarnessLogger
from harness.model_client import ModelClient, ModelClientError
from harness.output_parser import OutputParser, OutputParserError
from harness.prompts import PromptTemplate
from schemas import SummaryOutput

app = FastAPI()

MODEL_TIMEOUT = 360  # qwen3:8b chạy CPU có thể mất 1-3 phút


class ForumPost(BaseModel):
    id: int
    depth: int
    author: str
    content: str


class SummarizeRequest(BaseModel):
    posts: list[ForumPost]
    prompt_version: str = "v1"

@app.get("/health")
def health():
    return {"status": "ok"}
@app.post("/summarize", response_model=SummaryOutput)
def summarize(request: SummarizeRequest):
    posts = [p.model_dump() for p in request.posts]

    builder = ContextBuilder()
    chunks = builder.build(posts)

    if not chunks:
        return SummaryOutput(summary="", key_points=[], unanswered_questions=[])

    try:
        template = PromptTemplate(version=request.prompt_version)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    client = ModelClient(timeout=MODEL_TIMEOUT)
    parser = OutputParser()
    logger = HarnessLogger(
        feature="forum_summary",
        prompt_version=request.prompt_version,
        model=client.model,
    )

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
        return result
    except ModelClientError as exc:
        duration = time.monotonic() - start
        logger.log(tokens_used, duration, success=False, error=str(exc))
        raise HTTPException(status_code=504, detail=str(exc)) from exc
    except OutputParserError as exc:
        duration = time.monotonic() - start
        logger.log(tokens_used, duration, success=False, error=str(exc))
        raise HTTPException(status_code=502, detail=str(exc)) from exc
