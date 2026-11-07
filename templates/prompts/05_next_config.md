# 05 — Vòng thử tiếp của cùng hướng

```text
Đọc AGENTS.md và CONTRIBUTING.md trước khi làm.

TRACK: <bài>
EXPERIMENT_ID: <ID>
ISSUE: <URL>
BRANCH: <branch>
KẾT QUẢ ĐÃ PHÂN TÍCH: <run hoặc config làm mốc>
VÒNG THỬ ĐƯỢC GIAO: <setting cụ thể, hoặc "chọn một config tiếp theo trong phạm vi Issue">

Tôi giao bạn thực hiện vòng tiếp trong cùng hypothesis. Đọc kết quả và mô tả,
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
hoặc cần đổi hypothesis, báo nguyên nhân và trao đổi với tôi.

Bàn giao artifact, hash và TRACK/MODE/ID/OWNER/CONFIG_NAME chọn trong notebook rồi dừng. Tôi tự
chạy notebook local. Không tự chạy notebook, mở browser, theo dõi runtime, tự tạo điểm, merge hoặc đóng Issue.
Cuối lượt liệt kê file thực sự đã tạo/sửa kèm link thật để tôi kiểm tra thủ công.

```
