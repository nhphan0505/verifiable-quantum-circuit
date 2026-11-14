# 04 — Triển khai API và tests

Áp dụng [workflow PP](README.md). Đầu vào: DESCRIPTION đã đủ kế hoạch và
hypothesis đã chọn. Được sửa code/tests/mô tả của PP, đồng bộ Issue và commit
nguồn; chưa tự push, mở PR hay tích hợp experiment nếu chưa được giao.

## Yêu cầu

Viết `solution.py` có docstring nêu thuật toán, điều kiện đúng, tham số, cách
gọi và giới hạn. Dùng API Python để các hướng có thể gọi về sau; không yêu cầu
sửa experiment để test. Tên thư mục `PP-NNN` không dùng được trong cú pháp
import thông thường: dùng cơ chế nạp module theo đường dẫn/module registry đã
có, hoặc loader nhỏ trong phạm vi PP, và ghi cách gọi cụ thể. Không tự xây
framework/registry dùng chung ngoài nhiệm vụ được giao.

Không sửa đầu vào tại chỗ hoặc tự ghi đè artifact nguồn. Nhận tham số qua
API/CLI, không thêm configs mới. Chỉ thêm helper/dependency thực sự cần thiết
trong phạm vi được phép; thay dependency/hạ tầng chung cần nhiệm vụ riêng.

`tests/` chứa code kiểm thử tự động, không chứa log hay bảng điểm. Dùng mạch
nhỏ có hành vi biết trước để kiểm tra tính đúng trước/sau, điều kiện từ chối,
trường hợp biên, pha/ancilla khi liên quan và tham số không hợp lệ. Chọn phép
so phù hợp với ngữ nghĩa mạch; không coi thống kê tài nguyên là chứng minh đúng.
Không bắt buộc tách file theo mẫu hoặc viết test chỉ lặp lại implementation.

Chạy tests thích hợp bằng môi trường Python của repo. Cập nhật DESCRIPTION
khớp API/tham số rồi commit source/tests/mô tả trước chấm; lấy SHA thật.
Thay code hoặc tham số kiểm chứng đã mô tả thì cập nhật và commit trước lần
thử tiếp. Không gán SHA cũ cho code đang sửa.

## Nghiệm thu

- [ ] API gọi được, tests có ý nghĩa đã chạy và mô tả khớp implementation.
- [ ] Không thay experiment, không thêm config/run/results.
- [ ] Có commit nguồn thật để bước 5 kiểm chứng; tests đạt chưa có nghĩa verifier PASS.
