"""Quality check models, backend, and checks."""

from __future__ import annotations

import os
from functools import lru_cache
from typing import Literal

from dotenv import load_dotenv
from openai import AsyncAzureOpenAI, AsyncOpenAI
from pydantic import BaseModel
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider

load_dotenv()


# --- Models ---


class QCResult(BaseModel):
    decision: Literal["pass", "fail"]
    issues: list[str]
    reasoning: str


class QCReport(BaseModel):
    unresolved_content: QCResult
    contradiction: QCResult
    overall: Literal["pass", "fail"]


# --- Backend ---


def _build_agent(model_name: str, system_prompt: str, result_type) -> Agent:
    if os.environ.get("AZURE_OPENAI_ENDPOINT") and os.environ.get("AZURE_OPENAI_API_KEY"):
        client = AsyncAzureOpenAI(
            azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
            api_key=os.environ["AZURE_OPENAI_API_KEY"],
            api_version=os.environ.get("AZURE_OPENAI_API_VERSION", "2024-12-01-preview"),
        )
    elif os.environ.get("OPENAI_API_KEY"):
        client = AsyncOpenAI(api_key=os.environ["OPENAI_API_KEY"])
    else:
        raise EnvironmentError(
            "No API credentials found. Set AZURE_OPENAI_ENDPOINT + AZURE_OPENAI_API_KEY "
            "or OPENAI_API_KEY in your .env file."
        )
    model = OpenAIChatModel(model_name, provider=OpenAIProvider(openai_client=client))
    return Agent(model, output_type=result_type, system_prompt=system_prompt)


# --- Checks ---

_WINNING_PROMPT = """
You are a senior content quality auditor for an enterprise knowledge base.
Your job is to inspect policy document snippets and detect content that is incomplete or unpublishable.

Flag a snippet as FAIL if it contains ANY of the following:
1. EXPLICIT PLACEHOLDERS — tokens that were meant to be replaced before publishing:
   - Bracket styles: [value], {value}, <value>
   - Literal tokens: TBD, TODO, FIXME, INSERT, PLACEHOLDER
   - Blank markers: underscores (____), ellipses used as blanks (...)
2. MISSING CONTACT INFORMATION — a role, team, or department is named as the point of contact
   but no actionable contact detail (email, phone, URL, ticket system) is provided.
3. VAGUE REFERENCES — non-specific phrases that leave the reader unable to act:
   - 'the appropriate team', 'relevant personnel', 'the usual way', 'as required'

Mark as PASS only if the snippet is fully specified: all placeholders are resolved,
every named contact has a reachable detail, and all process references are concrete.

Be precise. Do not flag normal policy language like 'management' or 'HR' when they are
used descriptively rather than as an unresolved contact point.
"""


@lru_cache(maxsize=1)
def _get_unresolved_content_judge():
    return _build_agent("gpt-4.1", _WINNING_PROMPT, QCResult)


async def check_unresolved_content(text: str) -> QCResult:
    """Detect unfilled placeholders, missing contacts, and vague references."""
    result = await _get_unresolved_content_judge().run(f"Inspect this policy document:\n\n{text}")
    return result.output


async def check_contradiction(text: str) -> QCResult:
    """Return the current mock contradiction result."""
    return QCResult(
        decision="pass",
        issues=[],
        reasoning="[mock] Contradiction detection not yet implemented.",
    )
