import time
import os
import secrets

from fastapi import FastAPI, HTTPException, Depends, Header
from pydantic import BaseModel

from harness.context_builder import ContextBuilder
from harness.logger import HarnessLogger
from harness.model_client import ModelClient, ModelClientError
from harness.output_parser import OutputParser, OutputParserError
from harness.prompts import PromptTemplate
from schemas import SummaryOutput

app = FastAPI()

MODEL_TIMEOUT = 360  # upper bound for one Ollama call (qwen3:8b on CPU can take 1-3 minutes)

# Total time budget for one /summarize request, shared by every model call
# (all chunks + the merge step). It must stay BELOW the Moodle side curl
# timeout (CURLOPT_TIMEOUT = 380 in summarize_discussion.php), so that Moodle
# receives a clean 504 from us instead of giving up while we keep running.
REQUEST_DEADLINE = 350

API_KEY=os.environ.get("FORUMAI_API_KEY")

def verify_api_key(authorization: str = Header(default="")) -> None:
    """Checks the 'Authorization: Bearer <key>' header sent by Moodle against
    FORUMAI_API_KEY. Runs before summarize()'s body, as a FastAPI dependency."""
    if not API_KEY:
        # Misconfiguration on our side: fail closed, not open.
        raise HTTPException(status_code=500, detail="FORUMAI_API_KEY is not configured on the server")

    expected = f"Bearer {API_KEY}"
    # secrets.compare_digest: constant-time comparison, avoids leaking the key
    # length/content through response-time differences (timing attack).
    if not secrets.compare_digest(authorization, expected):
        raise HTTPException(status_code=401, detail="Invalid or missing API key")


class ForumPost(BaseModel):
    id: int
    depth: int
    author: str
    title: str
    content: str


class SummarizeRequest(BaseModel):
    posts: list[ForumPost]
    prompt_version: str = "v1"

@app.get("/health")
def health():
    return {"status": "ok"}
@app.post("/summarize", response_model=SummaryOutput, dependencies=[Depends(verify_api_key)])
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

    start = time.monotonic()
    deadline = start + REQUEST_DEADLINE
    tokens_used = 0

    def run_model(system_prompt: str, user_prompt: str) -> SummaryOutput:
        nonlocal tokens_used
        response = client.chat(system_prompt, user_prompt, deadline=deadline)
        tokens_used += response["total_tokens"]
        return parser.parse(response["content"])

    try:
        # Map: summarize every chunk (a long discussion is split into several).
        partials = [
            run_model(
                template.system_prompt,
                template.build_user_prompt(chunk, part=i, total_parts=len(chunks)),
            )
            for i, chunk in enumerate(chunks, 1)
        ]
        # Reduce: merge the partial summaries into one.
        if len(partials) == 1:
            result = partials[0]
        else:
            result = run_model(
                template.merge_system_prompt,
                template.build_merge_prompt(partials),
            )
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
