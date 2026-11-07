# Prompt mẫu theo giai đoạn

Copy phần trong khối `text`, thay các ô `<...>`, rồi gửi cho coding agent đang mở project.
Mỗi prompt chỉ cấp phạm vi cho giai đoạn đó; việc đọc file mẫu không có nghĩa đã được giao thao tác GitHub.
Đọc AGENTS.md và CONTRIBUTING.md là yêu cầu chung; không cần dán lại toàn bộ quy trình vào từng chat.

Quy ước đường dẫn: `S = src/<TRACK>/<ID>/`, `R = results/<TRACK>/<ID>/<config>/<mode>/<run_id>/`.
Các link thư mục bên dưới mở vị trí thực tế để tìm file của ID đang làm. Với ID chưa tạo thì chưa thể có link file cụ thể; yêu cầu agent trả link thật cuối mỗi lượt. Không dùng link baseline thay cho kết quả của hướng mới.

| Giai đoạn | Prompt | Nội dung cần kiểm tra | Điểm dừng |
| --- | --- | --- | --- |
| 1. Tìm hướng trên main | [Tìm hypothesis](01_find_hypothesis.md) | Hypothesis có nguồn, khác hướng đã có, phạm vi rõ và cách kiểm chứng; chưa sửa file hoặc nhận việc | Đề xuất, chưa sửa hoặc nhận việc |
| 2. Nhận hướng | [Tạo Issue mới và branch](02_claim_issue_branch.md) | ① Có `S/DESCRIPTION.md`; ② `src/<TRACK>/EXPERIMENTS.md` đã thêm dòng của hướng, link mở đúng DESCRIPTION; ③ lên GitHub kiểm tra đã có Issue và branch đúng ID/owner qua URL agent báo — [src](../../../src) | Có mô tả, mục lục và draft PR; chưa code |
| 3. Triển khai | [Code/config/compile](03_implement_compile.md) | ① Có `S/solution.py` đúng chỗ; ② có `S/configs/<name>.json`, setting đúng hướng đang thử; ③ compile ra `artifacts/<TRACK>/<ID>/<name>.kmb` (task 1–2) hoặc `.zip` (task 3), tên trùng config; **Tùy chọn:** mở `S/DESCRIPTION.md` xem có giải thích ý nghĩa các config, khác biệt giữa chúng và lý do chọn setting — [src](../../../src), [artifacts](../../../artifacts) | Có artifact/provenance, bàn giao notebook local |
| 4. Đã tải results | [Phân tích kết quả](04_analyze_results.md) | Không cần kiểm tra file thủ công. Chat với LLM về kết quả và đề xuất để quyết định: thử config tiếp, sửa implementation, tách hướng mới hoặc dừng hướng. Agent tự kiểm tra results và cập nhật tracking theo quy định. | Ghi kết quả, commit và đề xuất quyết định |
| 5. Thử tiếp | [Config tiếp theo](05_next_config.md) | ① Config mới nằm trong `S/configs/<name>.json`; ② artifact mới nằm trong `artifacts/<TRACK>/<ID>/<name>.kmb` (task 1–2) hoặc `.zip` (task 3), tên trùng config — [src](../../../src), [artifacts](../../../artifacts) | Artifact mới, bàn giao notebook local |
| 6. Tác giả chuẩn bị PR | [Chuẩn bị PR](06_prepare_pr.md) | PR mô tả giải pháp cuối, config/run tốt nhất và giới hạn; code/mô tả/điểm/results đồng bộ, link hợp lệ; không đưa artifact lớn vào Git — [src](../../../src), [results](../../../results) | PR sẵn sàng review, chưa merge |
| 7. Teammate review | [Review PR](07_review_pr.md) | Findings có file/dòng, ảnh hưởng và bằng chứng; nêu kiểm tra đã/chưa làm; không sửa/approve/merge | Chưa sửa/approve/merge |
| 7b. Teammate đăng review | [Đăng Approve / Request changes](07b_publish_review.md) | Review có URL, đúng tài khoản reviewer và SHA đã kiểm tra; nếu còn lỗi thì tác giả sửa và quay lại 7 | Đã đăng review, chưa merge |
| 8. Tác giả merge | [Merge và đóng Issue](08_merge_complete.md) | PR thực sự merged, review/check bắt buộc đạt; không mất dòng khi xử lý conflict; Issue đóng nếu phạm vi hoàn tất — xem URL agent báo | PR merged, Issue đúng trạng thái |
| Đổi chat/model | [Khôi phục ngữ cảnh](09_resume.md) | Đúng branch/owner và giai đoạn; trạng thái được xác minh từ file/GitHub; không tạo lại Issue/file/run hoặc chạy lại công việc đã xong | Tiếp tục đúng giai đoạn được giao |

Kiểm tra thủ công giai đoạn 3 gồm ba mục chính trên; có thể đọc thêm DESCRIPTION.md để hiểu ý nghĩa và lý do chọn các config. Hash, provenance, commit nguồn và điều kiện kỹ thuật vẫn do agent tự kiểm tra theo AGENTS.md; không yêu cầu thành viên kiểm lại từng mục đó.

### Link nhanh tới các bảng dùng chung

| Bài | Mục lục | Bảng điểm | Source | Results |
| --- | --- | --- | --- | --- |
| Invsqrt | [EXPERIMENTS.md](../../../src/invsqrt/EXPERIMENTS.md) | [SCORES.md](../../../src/invsqrt/SCORES.md) | [invsqrt](../../../src/invsqrt) | [results](../../../results/invsqrt) |
| DQI | [EXPERIMENTS.md](../../../src/dqi/EXPERIMENTS.md) | [SCORES.md](../../../src/dqi/SCORES.md) | [dqi](../../../src/dqi) | [results](../../../results/dqi) |
| DFTHC | [EXPERIMENTS.md](../../../src/dfthcsos/EXPERIMENTS.md) | [SCORES.md](../../../src/dfthcsos/SCORES.md) | [dfthcsos](../../../src/dfthcsos) | [results](../../../results/dfthcsos) |

Sau mỗi prompt, thành viên chỉ thực hiện phần kiểm tra/trao đổi ghi trong bảng trước khi giao giai đoạn tiếp theo. Giai đoạn 4 chỉ trao đổi với LLM để quyết định bước tiếp, không yêu cầu kiểm tra file thủ công. Với task 3, kiểm tra ZIP có submission.npz và các angle_k_*.kmb liên tục từ 0 ở gốc ZIP. BUILT chỉ xác nhận đã dựng artifact, chưa phải verifier PASS. Results được notebook local lưu đúng thư mục; agent không được tự bịa JSON verifier để đủ danh sách.

Luồng thường: **1 → chọn hướng → 2 → 3 → tự chạy notebook local → 4 → quyết định**.
Nếu thử tiếp: **5 → tự chạy notebook → 4**. 
Nếu dừng: **6 → 7 → tác giả sửa/push nếu cần → teammate review lại → 7b → 8**.
Nếu 7b yêu cầu sửa, quay lại tác giả sửa/push rồi 7 và 7b.
Tác giả làm 6 và 8; teammate làm 7 và 7b bằng phiên agent riêng, tài khoản GitHub khác tác giả. Một Issue/branch vẫn thuộc một owner; reviewer không sửa branch tác giả. HEAD đổi sau approval thì cần review/approval lại trên HEAD mới.

Ví dụ điền trường: TRACK `invsqrt`, ID `INV-123`, config `balanced`.
Đây chỉ là ví dụ; dùng số Issue và URL thật, không sao chép thành ID đã được đăng ký.
Nếu chưa kết nối GitHub, agent phải báo phần chưa xác minh/thực hiện; không tự tạo Issue hoặc URL giả.

Mốc commit: code/config trước compile; results/provenance/score/kết luận sau chấm.
Thành viên tự chạy notebook local với 5 tham số; results lưu trực tiếp vào project; agent làm phần còn lại
trong phạm vi prompt được giao. Prompt 07 trả findings về chat; teammate dùng 07b để giao agent đăng review lên PR.
Prompt 08 chỉ merge sau khi approval GitHub và các check đạt.

Các prompt này chưa tự thiết lập CI hay branch protection. Điều kiện merge dựa trên
cấu hình thật của repository và review được cung cấp.

Prompt 02 mặc định tạo Issue mới; thành viên chỉ điền TRACK, hypothesis và owner. Agent lấy số Issue thật, đặt title/ID, rồi đọc lại để kiểm tra title trùng H1 và mục lục. Nếu trùng phạm vi đã có thì báo để thống nhất, không tạo Issue trùng.

Prompt 03 tự chọn config khởi đầu dựa trên hypothesis, baseline, kết quả sẵn có và ràng buộc verifier. Thành viên không phải điền setting. Agent giải thích lựa chọn và mặc định dựng một ứng viên đầu tiên; chỉ thêm đối chứng khi cần.
