# 03 — Viết code/config và compile để bàn giao chấm

```text
Đọc AGENTS.md và CONTRIBUTING.md trước khi làm.

TRACK: <bài>
EXPERIMENT_ID: <ID>
ISSUE: <URL>
BRANCH: <branch của hướng>

Tôi giao bạn triển khai hướng đã nhận và commit source/config. Kiểm tra đúng
branch/owner; đọc DESCRIPTION.md và nguồn kế thừa trước khi code. Nếu phát hiện
ý tưởng không đúng hoặc ngoài phạm vi, giải thích thay vì tự đổi hypothesis.

Viết solution.py có docstring chi tiết, đọc --config từ configs/<name>.json.
Đặt source/config/artifact/provenance đúng cấu trúc quy định trong AGENTS.md.
Đồng bộ mô tả với implementation và Issue. Không sửa verifier, notebook hoặc
hạ tầng chung. Mỗi setting dùng JSON riêng, không sao chép Python.

Tự chọn config ban đầu phù hợp nhất để kiểm tra hypothesis; tôi không cung
cấp tên hoặc setting. Đọc DESCRIPTION/Issue, config của nguồn kế thừa, kết quả
đã có và các ràng buộc verifier trước khi chọn. Không hỏi tôi chọn tham số
thường lệ nếu có thể quyết định từ những thông tin này.

Ưu tiên một config đầu tiên có sức kiểm chứng rõ: chỉ thay các tham số liên
quan trực tiếp đến hypothesis, giữ phần còn lại theo mốc đối chiếu phù hợp.
Cân bằng khả năng giảm chi phí với điều kiện đúng, dư địa sai số, workspace
và giới hạn của bài. Có thể sàng lọc bằng phân tích hoặc mô hình local đúng
với thuật toán; không chọn chỉ vì tạo được artifact nhỏ hơn.

Chỉ thêm config đối chứng khi thật sự cần phân biệt tác động của hypothesis
và chưa có kết quả đối chứng tương thích; không tự quét hàng loạt setting
khi mỗi artifact sẽ phải chấm thủ công. Đặt tên JSON rõ ràng và ghi trong
DESCRIPTION lý do chọn giá trị, mốc đối chiếu, dự đoán và kết quả nào sẽ ủng hộ
hoặc bác bỏ hypothesis. Đây là lựa chọn ban đầu, chưa được gọi là config tối
ưu hoặc khẳng định mức cải thiện khi chưa có results.

Trước khi thử, hoàn thiện kế hoạch kiểm chứng trong DESCRIPTION theo template:
mốc đối chứng cụ thể, tiêu chí ủng hộ/bác bỏ và điều kiện dừng; nêu kiểm tra bổ
sung độc lập hoặc full cho ứng viên cuối. Không đổi tiêu chí theo results mà
không ghi lý do.

Chạy kiểm tra local phù hợp; commit mô tả, code và config trước khi compile.
Ghi SHA thực tế, dựng bằng .venv và xuất artifacts/<TRACK>/<ID>/<name>.kmb
hoặc .zip đúng định dạng task 3. Sau build ghi provenance theo AGENTS.md:
commit nguồn, đường dẫn/hash config, hash artifact, lệnh dựng và môi trường.
Nếu sửa source/config thì commit và dựng lại; không dùng SHA cũ cho build mới.

Nếu compile lỗi, tự đọc lỗi và sửa code/config trong phạm vi Issue, commit
phiên bản mới rồi compile lại bằng .venv đến khi thành công. Không bàn giao
artifact cũ hoặc file sinh dở như kết quả lần build mới. Chỉ báo BUILT khi
compile không lỗi và artifact mới đã được tạo đúng tên/đường dẫn. Nếu bị chặn
hoặc cần đổi hypothesis, báo nguyên nhân và trao đổi với tôi.

Dừng khi có artifact BUILT và provenance. Báo file cần upload, hash, TRACK,
ID/config/mode đề xuất, lý do chọn config và cách lấy results. Nếu có hơn
một artifact, chỉ rõ thứ tự chấm và mục đích của từng config. Tôi tự chấm Colab: không mở browser,
không chạy Colab/MCP, không theo dõi runtime, không gọi BUILT là PASS.
Cuối lượt liệt kê file đã tạo/sửa kèm link thật để tôi kiểm tra thủ công.
Không merge hoặc đóng Issue.
```
