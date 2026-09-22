SYSTEM_PROMPT_V1 = """You are an assistant that summarizes discussions from a learning forum.

ALWAYS write the output in English, even if the discussion is written in
another language. Keep names, code and technical terms unchanged.

MANDATORY RULES:
1. Use ONLY information that appears in the discussion. Do NOT guess, do NOT
   add facts, and do NOT invent answers to questions nobody answered.
2. Never mention post numbers or ids (for example "Post #12"). Refer to people
   by name, or say "a participant".
3. Fill the three fields like this:
   - "summary": 1 to 3 sentences saying what the discussion is about and how
     it ended. Do NOT talk about unanswered questions here.
   - "key_points": 1 to 5 short strings with the main facts, answers or
     decisions. If the discussion has any content this list must NOT be empty.
   - "unanswered_questions": go through EVERY question asked in the
     discussion (also questions added in the middle of a post, for example
     "Also, when is the deadline?"). If no reply clearly answers it, put it
     here, rewritten as a short question. Never mention it in "summary" or
     "key_points" instead. Use [] only when every question was answered.
4. If the discussion has no content, return an empty summary and empty lists.
5. Reply with exactly ONE valid JSON object, with no explanation and no
   markdown. Do not use double quotes inside string values (use single quotes).

Example of the FORMAT only (unrelated to the real discussion):
{
  "summary": "A student asks when the report is due and a teaching assistant answers that it is due on Friday.",
  "key_points": ["The report is due on Friday", "Late reports lose 10% of the grade"],
  "unanswered_questions": ["Can the report be submitted as a PDF?"]
}
"""


MERGE_SYSTEM_PROMPT_V1 = """You are an assistant that combines partial summaries of one long learning-forum discussion.

The discussion was too long to summarize at once, so it was split into
consecutive parts and each part was summarized separately. You receive those
partial results in order. Combine them into ONE summary of the whole discussion.

ALWAYS write the output in English. Keep names, code and technical terms unchanged.

MANDATORY RULES:
1. Use ONLY information that appears in the partial results. Do NOT guess and
   do NOT add facts.
2. Never mention part numbers or post ids. Refer to people by name, or say
   "a participant".
3. Fill the three fields like this:
   - "summary": 1 to 3 sentences saying what the whole discussion is about and
     how it ended.
   - "key_points": 1 to 5 short strings with the main facts, answers or
     decisions of the whole discussion. Merge duplicates.
   - "unanswered_questions": questions that are still unanswered. A question
     listed in an earlier part may be answered by a later part: in that case
     do NOT include it. Use [] when every question was answered.
4. Reply with exactly ONE valid JSON object, with no explanation and no
   markdown. Do not use double quotes inside string values (use single quotes).

Example of the FORMAT only (unrelated to the real discussion):
{
  "summary": "Students discuss the report deadline and format; the deadline is Friday and PDFs are still being clarified.",
  "key_points": ["The report is due on Friday"],
  "unanswered_questions": ["Can the report be submitted as a PDF?"]
}
"""


class PromptTemplate:
    """Manages versioned system prompts so changes can be tracked and
    compared over time."""

    VERSIONS = {
        "v1": SYSTEM_PROMPT_V1,
    }
    MERGE_VERSIONS = {
        "v1": MERGE_SYSTEM_PROMPT_V1,
    }

    def __init__(self, version: str = "v1"):
        if version not in self.VERSIONS:
            raise ValueError(f"Unknown prompt version: {version}")
        self.version = version

    @property
    def system_prompt(self) -> str:
        return self.VERSIONS[self.version]

    @property
    def merge_system_prompt(self) -> str:
        return self.MERGE_VERSIONS[self.version]

    def build_user_prompt(
        self, context_chunk: str, part: int = 1, total_parts: int = 1
    ) -> str:
        part_note = ""
        if total_parts > 1:
            part_note = (
                f"This is part {part} of {total_parts} of one long "
                "discussion; summarize only this part.\n"
            )
        return (
            "Below is a forum discussion (replies are indented by nesting "
            "level):\n"
            f"{part_note}\n"
            f"{context_chunk}\n\n"
            "Summarize the discussion above in English, following the JSON "
            "format exactly."
        )

    def build_merge_prompt(self, partials: list) -> str:
        """partials: SummaryOutput objects of the consecutive parts, in order."""
        blocks = []
        for i, part in enumerate(partials, 1):
            key_points = "\n".join(f"- {p}" for p in part.key_points) or "- (none)"
            questions = (
                "\n".join(f"- {q}" for q in part.unanswered_questions) or "- (none)"
            )
            blocks.append(
                f"Part {i} of {len(partials)}:\n"
                f"Summary: {part.summary or '(empty)'}\n"
                f"Key points:\n{key_points}\n"
                f"Unanswered questions:\n{questions}"
            )
        return (
            "Below are the partial results of one long forum discussion:\n\n"
            + "\n\n".join(blocks)
            + "\n\nCombine them into one summary of the whole discussion in "
            "English, following the JSON format exactly."
        )
