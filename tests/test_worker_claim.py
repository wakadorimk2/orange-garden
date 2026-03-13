from __future__ import annotations

import pytest

from personal_mcp.tools.worker_claim import (
    PROTOCOL_MARKER,
    PROTOCOL_NAME,
    build_worker_claim_event,
    parse_worker_claim_comment,
    serialize_worker_claim_event,
)


def test_build_worker_claim_event_normalizes_issue_and_reason() -> None:
    event = build_worker_claim_event(
        event_type="claim",
        worker_id=" codex-1 ",
        runtime=" codex ",
        issue_number="#378",
        reason="  draft   implementation  ",
    )

    assert event == {
        "protocol": PROTOCOL_NAME,
        "event_type": "claim",
        "worker_id": "codex-1",
        "runtime": "codex",
        "issue_number": 378,
        "reason": "draft implementation",
    }


def test_build_worker_claim_event_requires_ref_for_release() -> None:
    with pytest.raises(ValueError, match="ref is required for release"):
        build_worker_claim_event(
            event_type="release",
            worker_id="codex-1",
            runtime="codex",
            issue_number=378,
            reason="done",
        )


def test_build_worker_claim_event_requires_target_for_handoff_offer() -> None:
    with pytest.raises(ValueError, match="target_worker_id is required for handoff_offer"):
        build_worker_claim_event(
            event_type="handoff_offer",
            worker_id="codex-1",
            runtime="codex",
            issue_number=378,
            reason="needs docs review",
            ref="12345",
        )


def test_serialize_worker_claim_event_uses_stable_field_order() -> None:
    body = serialize_worker_claim_event(
        {
            "event_type": "handoff_offer",
            "worker_id": "codex-1",
            "runtime": "codex",
            "issue_number": 378,
            "reason": "needs docs review",
            "ref": "12345",
            "target_worker_id": "claude-1",
        }
    )

    assert body == "\n".join(
        [
            PROTOCOL_MARKER,
            "protocol: worker-claim/v1",
            "event_type: handoff_offer",
            "worker_id: codex-1",
            "runtime: codex",
            "issue_number: 378",
            "reason: needs docs review",
            "ref: 12345",
            "target_worker_id: claude-1",
        ]
    )


def test_parse_worker_claim_comment_round_trips_protocol_body() -> None:
    body = "\n".join(
        [
            PROTOCOL_MARKER,
            "protocol: worker-claim/v1",
            "event_type: handoff_accept",
            "worker_id: claude-1",
            "runtime: claude",
            "issue_number: 378",
            "reason: taking verification pass",
            "ref: 12346",
        ]
    )

    parsed = parse_worker_claim_comment(body)

    assert parsed == {
        "protocol": PROTOCOL_NAME,
        "event_type": "handoff_accept",
        "worker_id": "claude-1",
        "runtime": "claude",
        "issue_number": 378,
        "reason": "taking verification pass",
        "ref": "12346",
    }


def test_parse_worker_claim_comment_returns_none_for_non_protocol_comment() -> None:
    assert parse_worker_claim_comment("ordinary comment") is None


def test_parse_worker_claim_comment_rejects_invalid_lines() -> None:
    with pytest.raises(ValueError, match="invalid worker claim line"):
        parse_worker_claim_comment(f"{PROTOCOL_MARKER}\nprotocol worker-claim/v1")


def test_parse_worker_claim_comment_rejects_unknown_protocol() -> None:
    body = "\n".join(
        [
            PROTOCOL_MARKER,
            "protocol: worker-claim/v2",
            "event_type: claim",
            "worker_id: codex-1",
            "runtime: codex",
            "issue_number: 378",
            "reason: test",
        ]
    )

    with pytest.raises(ValueError, match="unsupported worker claim protocol"):
        parse_worker_claim_comment(body)
