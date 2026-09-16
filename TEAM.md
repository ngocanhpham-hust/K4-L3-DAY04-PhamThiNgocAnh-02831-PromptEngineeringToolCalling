# TEAM — Day04, K4-L3B

## Thông tin bài nộp

- Hình thức: cá nhân (được giảng viên cho phép).
- Người thực hiện: Phạm Thị Ngọc Anh.
- MSSV: 2A202602831.
- GitHub: [ngocanhpham-hust](https://github.com/ngocanhpham-hust).
- Repo: `K4-L3-DAY04-PhamThiNgocAnh-02831-PromptEngineeringToolCalling`.
- URL/branch nộp: <https://github.com/ngocanhpham-hust/K4-L3-DAY04-PhamThiNgocAnh-02831-PromptEngineeringToolCalling>, branch `main`.
- Commit kỹ thuật chốt evidence: `d695a90` (commit report/checkout nằm sau commit này).
- Deadline: theo thông báo chính thức của lớp/VLearn.

## Người thực hiện

| Họ và tên | MSSV | GitHub | Vai trò và công việc | File/commit |
|---|---|---|---|---|
| Phạm Thị Ngọc Anh | 2A202602831 | ngocanhpham-hust | Toàn bộ project: baseline, prompt/tool iterations, eval, runtime safety, chat UI, transcript, report | `5339e60`, `4fcaea3`, `acf131f`, `d695a90` |

## Nhận xét chung

- Kết quả: base tăng `21/30 → 27/30 → 29/30 → 30/30`; run chốt adversarial `12/12`, group `10/10`, đều không có provider error.
- Bằng chứng chính: [REPORT.md](starter_v0/artifacts/REPORT.md), [version_log.csv](starter_v0/artifacts/version_log.csv), [base final](starter_v0/runs/v3_B_base_openrouter_20260916T065816872910.json), [safety final](starter_v0/runs/v3_B_adversarial_openrouter_20260916T065921668154.json), [group final](starter_v0/runs/v3_B_group_openrouter_20260916T072402799739.json).
- Thay đổi hiệu quả nhất: tách confirmation lifecycle ở v2; thêm runtime guard ở v3 sau khi safety run chứng minh model vẫn có thể thực thi pseudo-code dù prompt đã cấm.
- Giới hạn còn lại: cùng hash/model/temperature, group từng dao động 9/10 rồi 10/10 ở category printing; external web search chưa demo do không có Tavily key.
- Cách thực hiện: cá nhân nên không có bước phân công/tích hợp giữa thành viên; mọi thay đổi được lưu theo commit v0–v3 và kiểm tra hồi quy trên cùng dataset.

## INDIVIDUAL

### Phạm Thị Ngọc Anh — 2A202602831

- Phần việc: tự thực hiện toàn bộ prompt/tool design, bộ 10 case cá nhân, runner evidence, safety guard, unit test, CLI chat, transcript và báo cáo.
- Quyết định chính: giữ lĩnh vực Helpdesk để dùng đúng bộ cố định; tách giả thuyết v1 routing, v2 confirmation, v3 taxonomy/trust; không sửa expected case để tạo cải tiến giả.
- Khó khăn và xử lý: v1 tạo ticket trước xác nhận; safety run đầu vẫn bị argument smuggling; bổ sung guard ở runtime và đọc `tool_results`/filesystem thay vì chỉ tin automatic score. Một OpenRouter request bị treo nên adapter được thêm timeout 60 giây và retry hữu hạn.
- Điều đã học: mô tả tool quyết định routing, system prompt quản lý hội thoại, còn hành động ghi và dữ liệu nhạy cảm cần enforcement trong code; temperature 0 không loại bỏ hoàn toàn biến thiên của provider.
- AI/công cụ đã dùng: Codex hỗ trợ đọc trace, sửa code/tài liệu và chạy lệnh; OpenRouter `openai/gpt-4o-mini` tạo tool calls. Tôi kiểm tra bằng run JSON, 9 unit test, transcript, Git diff/status và đối chiếu tool result thực tế.
- Evidence kỹ thuật: commit `d695a90`, [tool_guard.py](starter_v0/tool_guard.py), [test_tool_guard.py](starter_v0/tests/test_tool_guard.py), [eval_group.json](starter_v0/data/eval_group.json), [REPORT.md](starter_v0/artifacts/REPORT.md).
- Thời điểm tự nộp URL repo trên VLearn: sẽ điền sau khi push commit cuối và nộp.
