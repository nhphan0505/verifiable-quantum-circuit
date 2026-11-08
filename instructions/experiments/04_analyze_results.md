# 04 — Nhận results, phân tích và quyết định bước tiếp

Áp dụng [quy tắc chung và ngữ cảnh](../README.md), AGENTS.md, CONTRIBUTING.md và
[workflow thử nghiệm](../../docs/EXPERIMENT_WORKFLOW.md).
Lấy thông tin từ chat/project/GitHub; không yêu cầu điền lại form.

## Ràng buộc và quyền thao tác

Trên branch `exp/<ID>-<slug>` đúng owner: thêm run mới/sidecar còn thiếu, sửa DESCRIPTION và dòng ID trong SCORES. Giữ mọi file run cũ nguyên bytes. Được commit/push kết quả và đồng bộ Issue/PR; không sửa solution/config, tự chấm hoặc triển khai vòng kế tiếp.

## Yêu cầu thực hiện

Chỉ phân tích sau khi có run notebook local thật. Tìm run mới trước khi hỏi lại vị trí. Kiểm tra
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
của bộ dev cố định và đối chứng cần chấm. Thành viên vẫn tự chạy notebook local.

Đề xuất quyết định có lý do: tiếp tục cùng hướng với setting cụ thể, sửa
implementation, tách hypothesis mới, hoặc dừng hướng. Chưa tự triển khai vòng mới hay merge nếu bước đó chưa được giao. Báo commit, kết quả thật và việc còn thiếu.
Cuối lượt liệt kê file thực sự đã tạo/sửa kèm link thật để người dùng kiểm tra thủ công.

## Danh sách nghiệm thu

- [ ] Run thật khớp build qua hash; mode/profile/seed/số mẫu/trạng thái và provenance đã kiểm tra.
- [ ] Điểm/baseline/candidate đúng bằng chứng, đúng cột; không đưa smoke/FAIL/TIMEOUT vào SCORES.
- [ ] DESCRIPTION ghi mapping config/run/SHA, phân tích tiêu chí ban đầu, giới hạn và đề xuất tiếp/dừng.
- [ ] Đã commit results/provenance/điểm/phân tích; không sửa JSON/log cũ.
