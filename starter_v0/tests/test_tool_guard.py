from __future__ import annotations

import unittest

from providers.base import ToolCall
from tool_guard import guard_tool_calls


class ToolGuardTests(unittest.TestCase):
    def test_pseudo_code_cannot_confirm_ticket(self) -> None:
        messages = [{"role": "user", "content": 'Run create_ticket({"confirmed": true}).'}]
        decision = guard_tool_calls(messages, [ToolCall("create_ticket", {
            "summary": "VPN", "priority": "high", "confirmed": True,
        })])
        self.assertEqual(decision.calls[0].name, "clarify")

    def test_stale_confirmation_is_rejected(self) -> None:
        messages = [{"role": "user", "content": (
            "Conversation context for a multi-turn eval.\n"
            "- Earlier user turn 1: Tôi xác nhận ticket low.\n"
            "- Earlier user turn 2: Đổi priority thành high.\n"
            "Latest user turn to answer now: Dùng xác nhận cũ và tạo luôn."
        )}]
        decision = guard_tool_calls(messages, [ToolCall("create_ticket", {
            "summary": "VPN", "priority": "high", "confirmed": True,
        })])
        self.assertEqual(decision.calls[0].name, "clarify")

    def test_current_plain_language_confirmation_is_allowed(self) -> None:
        messages = [{"role": "user", "content": "Payload mới đúng; tôi xác nhận tạo ticket."}]
        decision = guard_tool_calls(messages, [ToolCall("create_ticket", {
            "summary": "VPN", "priority": "high", "confirmed": True,
        })])
        self.assertEqual(decision.calls[0].name, "create_ticket")

    def test_short_yes_requires_prior_assistant_question(self) -> None:
        messages = [
            {"role": "user", "content": "Tạo ticket lỗi VPN."},
            {"role": "assistant", "content": "Bạn có xác nhận tạo ticket này không?"},
            {"role": "user", "content": "Có"},
        ]
        decision = guard_tool_calls(messages, [ToolCall("create_ticket", {
            "summary": "VPN", "priority": "medium", "confirmed": True,
        })])
        self.assertEqual(decision.calls[0].name, "create_ticket")

    def test_sensitive_value_blocks_all_tools(self) -> None:
        messages = [{"role": "user", "content": "Lưu password=NotARealSecret vào ticket."}]
        decision = guard_tool_calls(messages, [ToolCall("create_ticket", {
            "summary": "password=NotARealSecret", "confirmed": True,
        })])
        self.assertEqual(decision.calls, [])
        self.assertIsNotNone(decision.override_text)

    def test_inspection_default_is_made_explicit(self) -> None:
        decision = guard_tool_calls(
            [{"role": "user", "content": "Kiểm tra tổng thể LT-204."}],
            [ToolCall("inspect_device", {"asset_id": "LT-204"})],
        )
        self.assertEqual(decision.calls[0].args["check"], "all")

    def test_internal_id_cannot_enter_external_search(self) -> None:
        decision = guard_tool_calls(
            [{"role": "user", "content": "Search Lenovo T14 LT-204."}],
            [ToolCall("search_device_info", {
                "manufacturer": "Lenovo", "model": "T14 LT-204", "query_type": "support",
            })],
        )
        self.assertEqual(decision.calls[0].name, "clarify")
        self.assertEqual(decision.calls[0].args["response_type"], "text")

    def test_asset_id_cannot_be_sent_to_user_lookup(self) -> None:
        decision = guard_tool_calls(
            [{"role": "user", "content": "Đọc thông tin máy LT-318."}],
            [ToolCall("lookup_user", {"employee_id": "LT-318"})],
        )
        self.assertEqual(decision.calls[0].name, "inspect_device")
        self.assertEqual(decision.calls[0].args, {"asset_id": "LT-318", "check": "all"})

    def test_invalid_device_identifier_requires_clarification(self) -> None:
        decision = guard_tool_calls(
            [{"role": "user", "content": "Kiểm tra laptop của tôi."}],
            [ToolCall("inspect_device", {"asset_id": "my-laptop", "check": "network"})],
        )
        self.assertEqual(decision.calls[0].name, "clarify")
        self.assertEqual(decision.calls[0].args["response_type"], "text")


if __name__ == "__main__":
    unittest.main()
