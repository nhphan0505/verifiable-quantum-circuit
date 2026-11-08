# Instructions nghiên cứu thử nghiệm

Áp dụng [quy tắc chung](../README.md) và [workflow](../../docs/EXPERIMENT_WORKFLOW.md).
Trong chat luồng này chỉ cần giao “thực hiện các bước 1 2 3”; agent dùng ngữ cảnh,
tra repo/GitHub và chỉ hỏi thông tin chưa xác định được. Ví dụ thiếu track hoặc
hypothesis đã chọn thì hỏi; không bắt người dùng lặp ID/owner/PR đã biết.

| Bước | Instructions | Đầu ra / điều kiện chuyển tiếp |
| --- | --- | --- |
| 1 | [Tìm hypothesis](01_find_hypothesis.md) | Đề xuất có căn cứ, chỉ đọc; chọn hypothesis trước bước 2 |
| 2 | [Nhận Issue/branch](02_claim_issue_branch.md) | Issue thật bắt buộc, DESCRIPTION/mục lục, branch và draft PR |
| 3 | [Triển khai/compile](03_implement_compile.md) | solution.py, JSON config, commit nguồn, artifact BUILT và provenance; chờ chấm local |
| 4 | [Phân tích results](04_analyze_results.md) | Run thật, điểm/kết luận/provenance và commit kết quả |
| 5 | [Vòng thử tiếp](05_next_config.md) | Config/artifact/provenance mới trong cùng hướng; chờ chấm local |
| 6 | [Chuẩn bị PR](06_prepare_pr.md) | PR/checks sẵn sàng review |
| 7 | [Review độc lập](07_review_pr.md) | Findings và SHA trong chat; chưa đăng GitHub |
| 7b | [Đăng review](07b_publish_review.md) | Review GitHub bằng tài khoản reviewer khác tác giả, đúng HEAD |
| 8 | [Merge/hoàn thành](08_merge_complete.md) | Merge commit sau approval/check; Issue đóng nếu hoàn tất |
| 9 | [Khôi phục](09_resume.md) | Trạng thái xác minh, tiếp tục đúng bước đã giao |

Luồng thường: **1 → 2 → 3 → thành viên chấm local → 4 → quyết định**.
Thử tiếp: **5 → chấm local → 4**. Kết thúc: **6 → reviewer 7 → sửa/review lại nếu cần
→ reviewer 7b → tác giả 8**. Tác giả không làm review độc lập cho chính PR của mình.
Giao nhiều bước không bỏ qua quyết định hypothesis, chấm local hoặc review/check.
Chỉ đề xuất config tiếp chưa cấp quyền làm vòng 5; nếu bước 5 đã được giao thì
agent tiếp tục khi đầu vào rõ và nghiệm thu bước trước đạt.

Phạm vi mặc định: source/config/mô tả/artifact/results của ID và dòng riêng trong
EXPERIMENTS/SCORES. Không sửa verifier, notebook, hạ tầng hay run cũ.
Mốc bắt buộc: **commit nguồn/config → build → bàn giao chấm → commit kết quả**.
BUILT chưa phải PASS; dev PASS chưa phải full PASS. Mỗi bước có checklist riêng;
thành viên không phải điền form hoặc kiểm lại hash/provenance thay agent.
