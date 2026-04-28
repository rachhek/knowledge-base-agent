from __future__ import annotations

import pytest

from quality_agent_demo.app import _resolve_input_text
from quality_agent_demo.checks import QCResult, check_contradiction


def test_resolve_input_text_prefers_non_empty_custom_text() -> None:
    assert _resolve_input_text("policy_clean", "  Custom policy text  ") == "Custom policy text"


def test_resolve_input_text_falls_back_to_selected_document() -> None:
    resolved = _resolve_input_text("policy_clean", "   ")

    assert resolved
    assert resolved == _resolve_input_text("policy_clean")


@pytest.mark.asyncio
async def test_check_contradiction_returns_mock_pass_result() -> None:
    result = await check_contradiction("Example policy text")

    assert result == QCResult(
        decision="pass",
        issues=[],
        reasoning="[mock] Contradiction detection not yet implemented.",
    )
