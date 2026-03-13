from __future__ import annotations

from typing import Any, Dict, Optional


PROTOCOL_MARKER = "<!-- og-worker-claim:v1 -->"
PROTOCOL_NAME = "worker-claim/v1"
EVENT_TYPES = frozenset(
    {
        "claim",
        "release",
        "handoff_offer",
        "handoff_accept",
        "maintainer_override",
    }
)


def _normalize_required(value: str, *, field_name: str) -> str:
    normalized = value.strip()
    if not normalized:
        raise ValueError(f"{field_name} must not be empty")
    return normalized


def _normalize_optional(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    normalized = value.strip()
    return normalized or None


def _normalize_issue_number(value: int | str) -> int:
    if isinstance(value, int):
        if value <= 0:
            raise ValueError("issue_number must be positive")
        return value
    normalized = _normalize_required(value, field_name="issue_number")
    if normalized.startswith("#"):
        normalized = normalized[1:]
    if not normalized.isdigit():
        raise ValueError("issue_number must be numeric")
    issue_number = int(normalized)
    if issue_number <= 0:
        raise ValueError("issue_number must be positive")
    return issue_number


def _normalize_reason(reason: str) -> str:
    normalized = " ".join(reason.split())
    if not normalized:
        raise ValueError("reason must not be empty")
    return normalized


def _normalize_event_type(event_type: str) -> str:
    normalized = _normalize_required(event_type, field_name="event_type")
    if normalized not in EVENT_TYPES:
        raise ValueError(f"unsupported worker claim event_type: {normalized}")
    return normalized


def build_worker_claim_event(
    *,
    event_type: str,
    worker_id: str,
    runtime: str,
    issue_number: int | str,
    reason: str,
    ref: Optional[str] = None,
    target_worker_id: Optional[str] = None,
) -> Dict[str, Any]:
    normalized_event_type = _normalize_event_type(event_type)
    event: Dict[str, Any] = {
        "protocol": PROTOCOL_NAME,
        "event_type": normalized_event_type,
        "worker_id": _normalize_required(worker_id, field_name="worker_id"),
        "runtime": _normalize_required(runtime, field_name="runtime"),
        "issue_number": _normalize_issue_number(issue_number),
        "reason": _normalize_reason(reason),
    }

    normalized_ref = _normalize_optional(ref)
    normalized_target_worker_id = _normalize_optional(target_worker_id)

    if normalized_event_type == "handoff_offer":
        if normalized_target_worker_id is None:
            raise ValueError("target_worker_id is required for handoff_offer")
        event["target_worker_id"] = normalized_target_worker_id
    elif normalized_target_worker_id is not None:
        raise ValueError(
            "target_worker_id is only allowed for "
            f"handoff_offer, got {normalized_event_type}"
        )

    if normalized_event_type == "claim":
        if normalized_ref is not None:
            raise ValueError("ref is not allowed for claim")
    else:
        if normalized_ref is None:
            raise ValueError(f"ref is required for {normalized_event_type}")
        event["ref"] = normalized_ref

    return event


def serialize_worker_claim_event(event: Dict[str, Any]) -> str:
    normalized_event = build_worker_claim_event(
        event_type=str(event.get("event_type", "")),
        worker_id=str(event.get("worker_id", "")),
        runtime=str(event.get("runtime", "")),
        issue_number=event.get("issue_number", ""),
        reason=str(event.get("reason", "")),
        ref=event.get("ref"),
        target_worker_id=event.get("target_worker_id"),
    )

    lines = [
        PROTOCOL_MARKER,
        f"protocol: {normalized_event['protocol']}",
        f"event_type: {normalized_event['event_type']}",
        f"worker_id: {normalized_event['worker_id']}",
        f"runtime: {normalized_event['runtime']}",
        f"issue_number: {normalized_event['issue_number']}",
        f"reason: {normalized_event['reason']}",
    ]
    if "ref" in normalized_event:
        lines.append(f"ref: {normalized_event['ref']}")
    if "target_worker_id" in normalized_event:
        lines.append(f"target_worker_id: {normalized_event['target_worker_id']}")
    return "\n".join(lines)


def parse_worker_claim_comment(body: str) -> Optional[Dict[str, Any]]:
    stripped = body.strip()
    if not stripped:
        return None

    lines = stripped.splitlines()
    if not lines or lines[0].strip() != PROTOCOL_MARKER:
        return None

    values: Dict[str, str] = {}
    for line in lines[1:]:
        if not line.strip():
            continue
        key, separator, raw_value = line.partition(":")
        if separator != ":":
            raise ValueError(f"invalid worker claim line: {line}")
        values[key.strip()] = raw_value.strip()
    if values.get("protocol") != PROTOCOL_NAME:
        raise ValueError(f"unsupported worker claim protocol: {values.get('protocol', '')}")

    return build_worker_claim_event(
        event_type=values.get("event_type", ""),
        worker_id=values.get("worker_id", ""),
        runtime=values.get("runtime", ""),
        issue_number=values.get("issue_number", ""),
        reason=values.get("reason", ""),
        ref=values.get("ref"),
        target_worker_id=values.get("target_worker_id"),
    )
