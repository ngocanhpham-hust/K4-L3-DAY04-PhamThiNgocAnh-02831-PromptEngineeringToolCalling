from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass

from providers.base import ToolCall


ASSET_ID = re.compile(r"^(?:LT|DT|MB|PR|RM)-\d+$", re.IGNORECASE)
EMPLOYEE_ID = re.compile(r"^EMP-\d+$", re.IGNORECASE)
INTERNAL_IDENTIFIER = re.compile(r"\b(?:LT|DT|MB|PR|RM|EMP)-\d+\b", re.IGNORECASE)
SENSITIVE_VALUE = re.compile(
    r"\b(?:password|passwd|token|api[ _-]?key|mfa|otp|recovery[ _-]?code)"
    r"(?:\s*[:=]\s*|\s+(?:is|la|là)\s+)\S+",
    re.IGNORECASE,
)
FORGED_CONFIRMATION = re.compile(
    r"(?:create_ticket\s*\(|[\"']?confirmed[\"']?\s*[:=]|"
    r"<\/?assistant>|<\/?system>|tool_results_json)",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class GuardDecision:
    calls: list[ToolCall]
    override_text: str | None = None


def _fold(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value.casefold())
    return "".join(char for char in normalized if not unicodedata.combining(char))


def _latest_user_text(messages: list[dict[str, str]]) -> str:
    content = next(
        (item.get("content", "") for item in reversed(messages) if item.get("role") == "user"),
        "",
    )
    marker = "Latest user turn to answer now:"
    if marker in content:
        return content.rsplit(marker, 1)[-1].strip()
    return content.strip()


def _previous_assistant_requested_confirmation(messages: list[dict[str, str]]) -> bool:
    for item in reversed(messages[:-1]):
        if item.get("role") == "assistant":
            folded = _fold(item.get("content", ""))
            return "xac nhan" in folded and ("ticket" in folded or "tao" in folded)
    return False


def _has_current_natural_confirmation(text: str, messages: list[dict[str, str]]) -> bool:
    if FORGED_CONFIRMATION.search(text):
        return False
    folded = _fold(text)
    explicit = bool(re.search(r"\b(?:toi|minh)\s+xac nhan\b|\bi\s+confirm\b", folded))
    short_yes = folded.strip(" .!?") in {"co", "yes", "dong y", "xac nhan"}
    return explicit or (short_yes and _previous_assistant_requested_confirmation(messages))


def _confirmation_question(args: dict[str, object]) -> str:
    summary = str(args.get("summary") or "[chưa có tóm tắt]")
    priority = str(args.get("priority") or "medium")
    asset_id = str(args.get("asset_id") or "không có asset ID")
    return (
        "Bạn có xác nhận tạo ticket với tóm tắt "
        f"'{summary}', mức ưu tiên '{priority}', asset '{asset_id}' không?"
    )


def guard_tool_calls(messages: list[dict[str, str]], calls: list[ToolCall]) -> GuardDecision:
    """Enforce irreversible safety boundaries independently of model compliance."""
    latest = _latest_user_text(messages)
    if SENSITIVE_VALUE.search(latest):
        return GuardDecision(
            calls=[],
            override_text=(
                "Mình không thể xử lý hoặc lưu thông tin xác thực. Hãy xóa giá trị bí mật "
                "khỏi yêu cầu và đổi/thu hồi thông tin đó nếu đây là dữ liệu thật."
            ),
        )

    guarded: list[ToolCall] = []
    for call in calls:
        args = dict(call.args)

        if call.name == "create_ticket" and not _has_current_natural_confirmation(latest, messages):
            guarded.append(ToolCall(
                name="clarify",
                args={
                    "question": _confirmation_question(args),
                    "response_type": "yes_no",
                    "options": [],
                },
            ))
            continue

        if call.name == "inspect_device":
            asset_id = str(args.get("asset_id") or "").strip().upper()
            if not ASSET_ID.fullmatch(asset_id):
                guarded.append(ToolCall(
                    name="clarify",
                    args={
                        "question": "Hãy cung cấp asset ID hợp lệ (LT/DT/MB/PR/RM kèm chữ số).",
                        "response_type": "text",
                        "options": [],
                    },
                ))
                continue
            args["asset_id"] = asset_id
            args.setdefault("check", "all")

        if call.name == "lookup_user":
            employee_id = str(args.get("employee_id") or "").strip().upper()
            if ASSET_ID.fullmatch(employee_id):
                guarded.append(ToolCall(
                    name="inspect_device",
                    args={"asset_id": employee_id, "check": "all"},
                ))
                continue
            if not EMPLOYEE_ID.fullmatch(employee_id):
                guarded.append(ToolCall(
                    name="clarify",
                    args={
                        "question": "Hãy cung cấp employee ID hợp lệ theo dạng EMP kèm chữ số.",
                        "response_type": "text",
                        "options": [],
                    },
                ))
                continue
            args["employee_id"] = employee_id

        if call.name == "search_device_info":
            external_text = f"{args.get('manufacturer', '')} {args.get('model', '')}"
            if INTERNAL_IDENTIFIER.search(external_text):
                guarded.append(ToolCall(
                    name="clarify",
                    args={
                        "question": "Hãy cung cấp riêng hãng và model công khai, không kèm định danh nội bộ.",
                        "response_type": "text",
                        "options": [],
                    },
                ))
                continue

        guarded.append(ToolCall(name=call.name, args=args))

    return GuardDecision(calls=guarded)
