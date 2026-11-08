# 05 — Vòng thử tiếp của cùng hướng

Áp dụng [quy tắc chung và ngữ cảnh](../README.md), AGENTS.md, CONTRIBUTING.md và
[workflow thử nghiệm](../../docs/EXPERIMENT_WORKFLOW.md).
Lấy thông tin từ chat/project/GitHub; không yêu cầu điền lại form.

## Ràng buộc và quyền thao tác

Trên branch `exp/<ID>-<slug>` đúng owner, phạm vi sửa như bước 03 và chỉ trong hypothesis của Issue. Giữ config/run và mapping mốc tốt cũ; được commit/push, đồng bộ Issue/PR và ghi build_only mới. Không chấm, đổi hướng hoặc sửa hạ tầng.

## Yêu cầu thực hiện

Thực hiện vòng tiếp trong cùng hypothesis. Đọc kết quả và mô tả,
chọn setting có lý do; nêu điều cần xác minh. Thêm JSON config có tên rõ ràng.
Đối chiếu tiêu chí/điều kiện dừng đã ghi; nếu đổi kế hoạch phải giải thích.
Giữ mapping config/run/commit tốt nhất cũ khi sửa implementation.
Chỉ sửa solution nếu cần trong phạm vi Issue; không đổi thuật toán sang hướng
mới hoặc sửa công cụ chấm. Không xóa config/run cũ để làm đẹp bảng.

Kiểm tra phù hợp, đồng bộ mô tả/Issue nếu thiết kế đổi. Commit source/config
trước build; compile artifact đúng tên và ghi provenance build_only mới.
Giữ cùng profile dev với mốc so sánh; nếu cần đổi profile, giải thích rằng
cần chấm lại baseline tương ứng để so công bằng.

Nếu compile lỗi, tự đọc lỗi và sửa code/config trong phạm vi Issue, commit
phiên bản mới rồi compile lại bằng .venv đến khi thành công. Không bàn giao
artifact cũ hoặc file sinh dở như kết quả lần build mới. Chỉ báo BUILT khi
compile không lỗi và artifact mới đã được tạo đúng tên/đường dẫn. Nếu bị chặn
hoặc cần đổi hypothesis, báo nguyên nhân và trao đổi với người dùng.

Bàn giao artifact, hash và TRACK/MODE/ID/OWNER/CONFIG_NAME chọn trong notebook rồi dừng. Thành viên tự
chạy notebook local. Không tự chạy notebook, mở browser, theo dõi runtime, tự tạo điểm, merge hoặc đóng Issue.
Cuối lượt liệt kê file thực sự đã tạo/sửa kèm link thật để người dùng kiểm tra thủ công.

## Danh sách nghiệm thu

- [ ] Config tiếp theo có lý do từ results, đúng phạm vi/điều kiện dừng; nếu cần sửa implementation thì mô tả khớp.
- [ ] Source/config mới đã commit trước build, không viết lại SHA từng được run tham chiếu.
- [ ] Artifact mới build thành công và provenance/hash đầy đủ; bàn giao chấm local như bước 03.
