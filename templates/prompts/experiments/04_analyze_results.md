# 04 — Nhận results, phân tích và quyết định bước tiếp

```text
Đọc AGENTS.md, CONTRIBUTING.md và docs/EXPERIMENT_WORKFLOW.md trước khi làm.

TRACK: <bài>
EXPERIMENT_ID: <ID>
ISSUE: <URL>
BRANCH: <branch của hướng>
RESULTS: <"đã lưu tự động trong project" hoặc đường dẫn run>

Tôi đã chạy notebook chấm local. Tìm run mới trước khi hỏi lại vị trí. Kiểm tra
TRACK/ID/config/mode, PASS/FAIL/TIMEOUT, số mẫu, profile/seed và hash verifier.
Đối chiếu hash submission với record build_only để xác định đúng commit/config;
không suy đoán phiên bản từ HEAD hoặc tên file. Nếu thiếu provenance, ghi rõ.

Giữ nguyên JSON/log gốc. Thêm provenance/review riêng nếu cần. Cập nhật
SCORES.md từ kết quả hợp lệ: một hướng một dòng, hai cột full/dev, link đúng
run/config tốt nhất; cải thiện = baseline/candidate (lần), cùng profile.
Smoke/FAIL/TIMEOUT không có điểm trong bảng. Đừng đổi dev thành full.

Phân tích giả thuyết, tài nguyên, sai số và xu hướng giữa các config. Ghi kết
luận kỹ thuật vào DESCRIPTION; đồng bộ Issue description. Commit results,
provenance, điểm và phân tích sau chấm. Ghi config/run tốt nhất từng mode với
SHA nguồn và link provenance trong DESCRIPTION; giữ phiên bản mốc tốt cũ nếu
solution.py đã đổi, không coi JSON cùng tên chạy với HEAD là tái lập run cũ.
Đối chiếu kết quả với tiêu chí đã ghi trước khi thử và điều kiện dừng. Với ứng
viên cuối, đề xuất kiểm tra bổ sung độc lập hoặc full nếu chưa có; nêu giới hạn
của bộ dev cố định và đối chứng cần chấm. Tôi vẫn tự chạy notebook local.

Đề xuất quyết định có lý do: tiếp tục cùng hướng với setting cụ thể, sửa
implementation, tách hypothesis mới, hoặc dừng hướng. Chưa tự triển khai vòng
mới hay merge ở bước này. Báo commit, kết quả thật và việc còn thiếu.
Cuối lượt liệt kê file thực sự đã tạo/sửa kèm link thật để tôi kiểm tra thủ công.

```
