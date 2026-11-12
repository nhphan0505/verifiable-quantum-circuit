# 07 — DESCRIPTION và hypothesis suy ra

Đầu vào: source/build/báo cáo thật từ bước 5–6. Có thể ghi kết quả thất bại và giới
hạn nếu exact chưa đạt, nhưng không đánh dấu đã nghiệm thu bước 6. Được cập nhật
mô tả/manifest, commit/push và đồng bộ Issue; không đổi thuật toán ngầm.

Hoàn thiện DESCRIPTION theo cấu trúc thích nghi ở bước 4:

1. Nguồn artifact, SHA-256, attribution/giấy phép đã biết và tình trạng source gốc.
2. Mục tiêu, tiêu chí exact và phạm vi (mạch, dữ liệu, container).
3. Input/output, biểu diễn/register, thuật toán/khối đã xác định, sơ đồ hoặc
   pseudocode khi hữu ích, điều kiện đúng/sai số/uncompute/sửa pha.
4. Cách tái dựng và dependency; phần giữ dạng chuỗi lệnh, bảng dữ liệu giữ lại,
   phần chưa suy ra được cách sinh. Ghi mức khôi phục, không chỉ ghi “decompiled”.
5. So sánh baseline có phiên bản; phân biệt quan sát, hypothesis và đo thực tế.
6. Kế hoạch kiểm chứng: tái tạo exact là hypothesis tái lập; hypothesis tối ưu
   riêng cần cơ chế, đối chứng, dự đoán, tiêu chí bác bỏ và điều kiện dừng. Có
   thể ghi chưa đủ căn cứ đề xuất hypothesis thuật toán. Suy ra sau phân tích
   phải ghi là hậu nghiệm, không trình bày như dự đoán trước khi có kết quả.
7. Kết luận kỹ thuật, mapping config → source commit → build/run/provenance,
   giới hạn và kiểm tra còn thiếu. Dẫn báo cáo hash; không chép log/bảng điểm.

H1/title/mục lục/Issue body phải đồng bộ. Nếu chỉ sửa tài liệu sau build, giữ SHA
nguồn đã thực sự dựng; nếu sửa source/config/data thì quay bước 5–6. Không thay
provenance cũ theo HEAD mới. Điểm chưa có thì để chưa chấm.

Nghiệm thu: người mới đọc có thể dựng lại và biết phần nào chắc chắn/chưa biết;
mọi khẳng định exact/điểm có bằng chứng, không đồng nhất trùng hash với hiểu ý tác giả.
