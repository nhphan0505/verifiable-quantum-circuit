# Chọn luồng làm việc

| Luồng | Bộ prompt | Đầu ra | Người thực hiện thủ công |
| --- | --- | --- | --- |
| Nghiên cứu thử nghiệm | [experiments](experiments/README.md) | Hypothesis, Issue, code/config, artifact, results và PR | Chấm notebook local, quyết định thử tiếp/dừng |
| Đọc paper/discussion | [literature](literature/README.md) | note.md có căn cứ, được review và merge | Giao nguồn, chọn phạm vi và chuyển bước |

Dùng agent/chat riêng cho từng luồng, workspace/worktree riêng nếu chạy đồng thời.
Agent nghiên cứu chỉ đọc note ready đã merge; agent tài liệu được đọc nguồn gốc.
Mỗi prompt chỉ giao quyền cho giai đoạn được gửi; không tự chạy toàn bộ chuỗi.
Nguồn chỉ có PDF chưa được coi là tri thức đã đọc. Không tự tạo note khi sinh hypothesis.

Tài liệu dùng branch cá nhân `research/<username>` cho nhiều resource/note; nhóm
họp quyết định rồi mới giao merge PR vào main. Không thay bước nhận hypothesis
và branch `exp/<ID>-...` của luồng experiment.
