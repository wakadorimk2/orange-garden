from __future__ import annotations

import pytest

from personal_mcp.tools.worker_claim import (
    PROTOCOL_MARKER,
    PROTOCOL_NAME,
    build_worker_claim_event,
    derive_worker_claim_state,
    parse_worker_claim_comment,
    serialize_worker_claim_event,
)


def _comment(
    comment_id: int,
    body: str,
    *,
    created_at: str,
    login: str = "worker-bot",
) -> dict:
    return {
        "id": comment_id,
        "body": body,
        "created_at": created_at,
        "user": {"login": login},
    }


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


def test_derive_worker_claim_state_keeps_first_claim_on_conflict() -> None:
    comments = [
        _comment(
            101,
            serialize_worker_claim_event(
                build_worker_claim_event(
                    event_type="claim",
                    worker_id="codex-1",
                    runtime="codex",
                    issue_number=378,
                    reason="take issue",
                )
            ),
            created_at="2026-03-13T10:00:00Z",
        ),
        _comment(
            102,
            serialize_worker_claim_event(
                build_worker_claim_event(
                    event_type="claim",
                    worker_id="claude-1",
                    runtime="claude",
                    issue_number=378,
                    reason="conflicting claim",
                )
            ),
            created_at="2026-03-13T10:01:00Z",
        ),
    ]

    state = derive_worker_claim_state(comments, issue_number=378, repo_owner="wakadorimk2")

    assert state["state"] == "claimed"
    assert state["owner"] == "codex-1"
    assert state["claim_ref"] == "101"
    assert state["events"][0]["valid"] is True
    assert state["events"][1]["valid"] is False


def test_derive_worker_claim_state_transfers_owner_on_handoff_accept() -> None:
    comments = [
        _comment(
            101,
            serialize_worker_claim_event(
                build_worker_claim_event(
                    event_type="claim",
                    worker_id="codex-1",
                    runtime="codex",
                    issue_number=378,
                    reason="take issue",
                )
            ),
            created_at="2026-03-13T10:00:00Z",
        ),
        _comment(
            102,
            serialize_worker_claim_event(
                build_worker_claim_event(
                    event_type="handoff_offer",
                    worker_id="codex-1",
                    runtime="codex",
                    issue_number=378,
                    reason="needs claude review",
                    ref="101",
                    target_worker_id="claude-1",
                )
            ),
            created_at="2026-03-13T10:01:00Z",
        ),
        _comment(
            103,
            serialize_worker_claim_event(
                build_worker_claim_event(
                    event_type="handoff_accept",
                    worker_id="claude-1",
                    runtime="claude",
                    issue_number=378,
                    reason="taking review",
                    ref="102",
                )
            ),
            created_at="2026-03-13T10:02:00Z",
        ),
    ]

    state = derive_worker_claim_state(comments, issue_number=378, repo_owner="wakadorimk2")

    assert state["state"] == "claimed"
    assert state["owner"] == "claude-1"
    assert state["claim_ref"] == "103"
    assert all(event["valid"] is True for event in state["events"])


def test_derive_worker_claim_state_keeps_handoff_pending_on_wrong_accept() -> None:
    comments = [
        _comment(
            101,
            serialize_worker_claim_event(
                build_worker_claim_event(
                    event_type="claim",
                    worker_id="codex-1",
                    runtime="codex",
                    issue_number=378,
                    reason="take issue",
                )
            ),
            created_at="2026-03-13T10:00:00Z",
        ),
        _comment(
            102,
            serialize_worker_claim_event(
                build_worker_claim_event(
                    event_type="handoff_offer",
                    worker_id="codex-1",
                    runtime="codex",
                    issue_number=378,
                    reason="needs claude review",
                    ref="101",
                    target_worker_id="claude-1",
                )
            ),
            created_at="2026-03-13T10:01:00Z",
        ),
        _comment(
            103,
            serialize_worker_claim_event(
                build_worker_claim_event(
                    event_type="handoff_accept",
                    worker_id="copilot-1",
                    runtime="copilot",
                    issue_number=378,
                    reason="incorrect accept",
                    ref="102",
                )
            ),
            created_at="2026-03-13T10:02:00Z",
        ),
    ]

    state = derive_worker_claim_state(comments, issue_number=378, repo_owner="wakadorimk2")

    assert state["state"] == "handoff_pending"
    assert state["owner"] == "codex-1"
    assert state["handoff_target_worker_id"] == "claude-1"
    assert state["offer_ref"] == "102"
    assert state["events"][2]["valid"] is False


def test_derive_worker_claim_state_allows_owner_release() -> None:
    comments = [
        _comment(
            101,
            serialize_worker_claim_event(
                build_worker_claim_event(
                    event_type="claim",
                    worker_id="codex-1",
                    runtime="codex",
                    issue_number=378,
                    reason="take issue",
                )
            ),
            created_at="2026-03-13T10:00:00Z",
        ),
        _comment(
            102,
            serialize_worker_claim_event(
                build_worker_claim_event(
                    event_type="release",
                    worker_id="codex-1",
                    runtime="codex",
                    issue_number=378,
                    reason="done",
                    ref="101",
                )
            ),
            created_at="2026-03-13T10:01:00Z",
        ),
    ]

    state = derive_worker_claim_state(comments, issue_number=378, repo_owner="wakadorimk2")

    assert state["state"] == "unclaimed"
    assert state["owner"] is None
    assert state["claim_ref"] is None
    assert all(event["valid"] is True for event in state["events"])


def test_derive_worker_claim_state_requires_repo_owner_for_override() -> None:
    comments = [
        _comment(
            101,
            serialize_worker_claim_event(
                build_worker_claim_event(
                    event_type="claim",
                    worker_id="codex-1",
                    runtime="codex",
                    issue_number=378,
                    reason="take issue",
                )
            ),
            created_at="2026-03-13T10:00:00Z",
        ),
        _comment(
            102,
            serialize_worker_claim_event(
                build_worker_claim_event(
                    event_type="maintainer_override",
                    worker_id="maintainer",
                    runtime="human",
                    issue_number=378,
                    reason="clear stale claim",
                    ref="101",
                )
            ),
            created_at="2026-03-13T10:01:00Z",
            login="outside-user",
        ),
        _comment(
            103,
            serialize_worker_claim_event(
                build_worker_claim_event(
                    event_type="maintainer_override",
                    worker_id="maintainer",
                    runtime="human",
                    issue_number=378,
                    reason="clear stale claim",
                    ref="101",
                )
            ),
            created_at="2026-03-13T10:02:00Z",
            login="wakadorimk2",
        ),
    ]

    state = derive_worker_claim_state(comments, issue_number=378, repo_owner="wakadorimk2")

    assert state["state"] == "unclaimed"
    assert state["events"][1]["valid"] is False
    assert state["events"][2]["valid"] is True
