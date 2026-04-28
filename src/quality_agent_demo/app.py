"""FastHTML application for the quality agent demo."""

from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv
from fasthtml.common import (
    H1,
    Button,
    Div,
    Li,
    Option,
    P,
    Script,
    Select,
    Span,
    Style,
    Textarea,
    Ul,
    fast_app,
    serve,
)
from openai import RateLimitError
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from quality_agent_demo.checks import QCReport, QCResult, check_contradiction, check_unresolved_content

load_dotenv()

# --- Documents ---

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_DATA_DIR = _PROJECT_ROOT / "data"

_DEMO_DOCUMENTS: dict[str, tuple[str, str]] = {
    "policy_with_issues": (
        "Remote Working Policy (with issues)",
        (_DATA_DIR / "policy_with_issues.md").read_text(),
    ),
    "policy_clean": (
        "Remote Working Policy (clean)",
        (_DATA_DIR / "policy_clean.md").read_text(),
    ),
}


def _resolve_input_text(doc_key: str, custom_text: str = "") -> str:
    custom = custom_text.strip()
    return custom if custom else _DEMO_DOCUMENTS[doc_key][1]


def _serialize_documents() -> str:
    return json.dumps({key: text for key, (_, text) in _DEMO_DOCUMENTS.items()})


# --- UI ---

CSS = """
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: system-ui, sans-serif; background: #0f1117; color: #e2e8f0; line-height: 1.6; }
.wrap { max-width: 780px; margin: 0 auto; padding: 2.5rem 1.5rem; }
h1 { font-size: 1.6rem; color: #f8fafc; margin-bottom: 0.25rem; }
.sub { color: #64748b; font-size: 0.9rem; margin-bottom: 2rem; }
select { background: #1e293b; color: #e2e8f0; border: 1px solid #334155; border-radius: 6px;
         padding: 0.5rem 0.75rem; font-size: 0.9rem; width: 100%; margin-bottom: 0.75rem; }
button { background: #1d4ed8; color: white; border: none; border-radius: 6px;
         padding: 0.55rem 1.25rem; font-size: 0.9rem; cursor: pointer; }
button:hover { background: #2563eb; }
.card { background: #1e293b; border-radius: 8px; padding: 1.25rem; margin-top: 1rem; }
.card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem; }
.tool-name { font-weight: 600; color: #f8fafc; }
.badge { display: inline-block; padding: 0.2rem 0.6rem; border-radius: 999px;
         font-size: 0.72rem; font-weight: 700; font-family: monospace; }
.badge-fail { background: #2d0a0a; color: #f87171; border: 1px solid #7f1d1d; }
.badge-pass { background: #052e16; color: #4ade80; border: 1px solid #166534; }
.badge-mock { background: #1e293b; color: #64748b; border: 1px solid #334155; font-size: 0.65rem; }
.badge-overall { font-size: 1rem; font-weight: 700; }
.issues { list-style: none; margin-top: 0.5rem; }
.issues li { background: #2d0a0a; border-left: 3px solid #ef4444; border-radius: 0 4px 4px 0;
             padding: 0.35rem 0.75rem; margin-bottom: 0.35rem; font-size: 0.83rem; color: #fca5a5; }
.reasoning { font-size: 0.8rem; color: #64748b; margin-top: 0.5rem; font-style: italic; }
.htmx-indicator { display: none; }
.htmx-request .htmx-indicator, .htmx-request.htmx-indicator { display: inline; }
button:disabled, button[disabled] { opacity: 0.5; cursor: not-allowed; }
#spinner { color: #64748b; font-size: 0.85rem; margin-left: 0.75rem; font-family: monospace; }
.error-card { background: #2d0a0a; border: 1px solid #7f1d1d; border-radius: 8px;
              padding: 1.25rem; margin-top: 1rem; color: #fca5a5; font-size: 0.875rem; }
textarea { width: 100%; background: #1e293b; color: #e2e8f0; border: 1px solid #334155; border-radius: 6px;
           padding: 0.6rem 0.75rem; font-size: 0.85rem; font-family: monospace; resize: vertical;
           margin-bottom: 0.75rem; line-height: 1.5; }
textarea:focus { outline: none; border-color: #3b82f6; }
"""

app, rt = fast_app(hdrs=[Style(CSS)])


def _result_card(title: str, result: QCResult, is_mock: bool = False) -> Div:
    badge = Span("FAIL", cls="badge badge-fail") if result.decision == "fail" else Span("PASS", cls="badge badge-pass")
    mock_badge = Span("mock", cls="badge badge-mock") if is_mock else ""
    issues = Ul(*[Li(issue) for issue in result.issues], cls="issues") if result.issues else ""
    return Div(
        Div(
            Span(title, cls="tool-name"),
            Div(badge, mock_badge, style="display:flex;gap:0.4rem;align-items:center;"),
            cls="card-header",
        ),
        issues,
        P(result.reasoning, cls="reasoning"),
        cls="card",
    )


@rt("/")
def get():
    doc_items = list(_DEMO_DOCUMENTS.items())
    _, (_, first_text) = doc_items[0]
    options = [Option(label, value=key) for key, (label, _) in doc_items]
    return Div(
        Script(f"const DOCS = {_serialize_documents()};"),
        H1("Acme Quality Agent"),
        P("Select a pre-built document or paste your own text below.", cls="sub"),
        Select(
            *options,
            id="doc-select",
            name="doc_key",
            onchange="document.getElementById('custom-text').value = DOCS[this.value] || ''",
        ),
        Textarea(
            first_text,
            id="custom-text",
            name="custom_text",
            placeholder="Or paste your own policy text here — this overrides the selection above.",
            rows="6",
        ),
        Div(
            Button(
                "Run QC Check",
                hx_post="/check",
                hx_target="#results",
                hx_include="[name='doc_key'],[name='custom_text']",
                hx_indicator="#spinner",
                hx_disabled_elt="this",
            ),
            Span("Running checks…", id="spinner", cls="htmx-indicator"),
        ),
        Div(id="results", style="margin-top:1.5rem;"),
        cls="wrap",
    )


@retry(
    retry=retry_if_exception_type((RateLimitError, TimeoutError)),
    stop=stop_after_attempt(4),
    wait=wait_exponential(multiplier=1, min=2, max=30),
    reraise=True,
)
async def _run_check(text: str) -> QCReport:
    unresolved_content, contradiction = await asyncio.gather(
        check_unresolved_content(text),
        check_contradiction(text),
    )
    overall: Literal["pass", "fail"] = (
        "fail" if "fail" in {unresolved_content.decision, contradiction.decision} else "pass"
    )
    return QCReport(unresolved_content=unresolved_content, contradiction=contradiction, overall=overall)


@rt("/check")
async def post(doc_key: str, custom_text: str = ""):
    text = _resolve_input_text(doc_key, custom_text)

    try:
        report = await _run_check(text)
    except Exception as exc:
        return Div(
            P("Check failed — could not reach the API.", style="font-weight:600;margin-bottom:0.5rem;"),
            P(str(exc), style="font-family:monospace;font-size:0.78rem;opacity:0.7;"),
            cls="error-card",
        )

    overall: Literal["pass", "fail"] = report.overall
    overall_badge = Span(f"Overall: {overall.upper()}", cls=f"badge badge-{overall} badge-overall")

    return Div(
        Div(overall_badge, style="margin-bottom: 0.5rem;"),
        _result_card("Unresolved Content Detection", report.unresolved_content),
        _result_card("Contradiction Detection — not implemented yet", report.contradiction, is_mock=True),
    )


def main() -> None:
    serve()
