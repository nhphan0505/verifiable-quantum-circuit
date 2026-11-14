# 08 — Bàn giao chấm và phân tích results

Đầu vào: artifact/build provenance đã nghiệm thu theo tiêu chí được chấp thuận.
Áp dụng [LOCAL_GRADING](../../docs/LOCAL_GRADING.md) và
[experiments 04](../experiments/04_analyze_results.md).

Giao bước 8 cấp quyền bàn giao và phân tích/commit/push kết quả, không mặc nhiên
cấp quyền tự chạy verifier. Thành viên tự chạy notebook; agent chỉ tự chấm khi
người dùng giao rõ lượt đó. Không mở Colab, tự theo dõi runtime hoặc tạo run giả.

Bàn giao artifact/hash, TRACK, ID, OWNER, CONFIG_NAME, MODE đề xuất và thư mục
results dự kiến. Chưa có results thì dừng phần phụ thuộc; không vượt sang kết luận.
Sau khi có kết quả, tìm trong repo trước khi hỏi lại, nối run với build bằng hash,
đối chiếu profile/seed/môi trường, giữ bất biến logs/raw JSON. Bổ sung sidecar mới
theo schema, phân tích và cập nhật SCORES khi đủ điều kiện theo workflow hiện tại.

Hash input giống nhau không xác nhận điểm lịch sử không có bằng chứng. dev PASS
không phải full PASS; TIMEOUT không chứng minh mạch sai. Có điểm PASS hợp lệ của
cùng bài là được so cải thiện, không cần trùng phiên bản/môi trường/profile;
ghi rõ bối cảnh và giữ hai cột full/dev riêng. Hypothesis suy ra chỉ được kết luận trong giới hạn phép kiểm
thật; một run PASS không chứng minh ý định ban đầu của tác giả.

Nghiệm thu: kết quả thật được nối provenance, mô tả/điểm đúng bằng chứng và commit
kết quả. Tối ưu tiếp cần phạm vi được giao, giữ mốc exact làm đối chứng, không
ghi đè bản tái dựng hoặc ngầm mở rộng sang hypothesis mới.
