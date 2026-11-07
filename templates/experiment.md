# [<EXPERIMENT-ID>] <Thao tác/thành phần + phương pháp + phạm vi thử>

<!-- Mẫu cho src/<TRACK>/<EXPERIMENT_ID>/DESCRIPTION.md.
H1 phải trùng nguyên văn tiêu đề GitHub Issue và tiêu đề link trong EXPERIMENTS.md.
Tiêu đề tự đủ nghĩa để phân công: nêu rõ thành phần, cách thay đổi và phạm vi; tránh tên chung như tối ưu baseline. Phần dưới H1 dùng làm Issue description.
Chọn đúng một loại bên dưới, bỏ các loại còn lại và bỏ comment hướng dẫn khi dùng.
Không ghi điểm, owner, trạng thái hay log vận hành vào DESCRIPTION.md. -->

Loại: <Tinh chỉnh một phương án / Kết hợp nhiều phương án / Ý tưởng mới>.

<!-- LOẠI 1: TINH CHỈNH MỘT PHƯƠNG ÁN -->

## File gốc

<Link file Python gốc; link DESCRIPTION gốc nếu có. Ghi commit hoặc hash để xác định phiên bản.>

## Phần tinh chỉnh và lý do

<Nêu rõ sửa phần nào, hành vi trước/sau và vì sao dự kiến có lợi.>

## Cách thực hiện và đánh đổi

<Mô tả chi tiết phần sửa, công thức/tham số liên quan, điều kiện để vẫn đúng,
ảnh hưởng sai số và đánh đổi tài nguyên. Dẫn lại nguồn cho phần giữ nguyên.>

<!-- LOẠI 2: KẾT HỢP NHIỀU PHƯƠNG ÁN -->

## Các file gốc và thành phần kế thừa

<Link từng file gốc và phiên bản; nói rõ lấy phần nào từ từng phương án.>

## Cách kết hợp

<Mô tả thứ tự ghép, dữ liệu/thanh ghi trao đổi và phần phải điều chỉnh.>

## Xử lý chỗ không tương thích

<Giải thích cách xử lý khác biệt về biểu diễn, precision, workspace, compute/uncompute,
sửa pha hoặc giả định thuật toán; nêu điều kiện đúng và đánh đổi của cách ghép.>

<!-- LOẠI 3: Ý TƯỞNG MỚI -->

## Thuật toán và công thức

<Mô tả đầy đủ bài toán, đầu vào/đầu ra, biểu diễn dữ liệu, công thức và các bước thuật toán.
Dẫn paper/nguồn tham khảo nếu có.>

## Điều kiện đúng và sai số

<Giải thích invariant, trường hợp biên, làm tròn/cắt cụt, khôi phục input,
xóa workspace, sửa pha và giới hạn sai số.>

## Tài nguyên dự kiến

<Nêu số qubit, Toffoli/phép quay hoặc cách ước lượng; giải thích tác động lên hàm điểm.>

<!-- PHẦN CHUNG: giữ cho cả ba loại. -->

## Kế hoạch kiểm chứng hypothesis

- Mốc đối chứng: <link source/config và commit/hash; link run cùng mode/profile/seed/môi trường nếu có, hoặc ghi chưa chấm>.
- Dự đoán: <đại lượng dự kiến thay đổi, cơ chế và đánh đổi; phân biệt dự đoán với kết quả đã đo>.
- Ủng hộ / bác bỏ: <kết quả quan sát và tiêu chí cụ thể để quyết định; trường hợp chưa đủ bằng chứng>.
- Điều kiện dừng: <mức đạt mục tiêu, dấu hiệu bác bỏ, giới hạn số vòng hoặc tài nguyên; khi nào thử tiếp/tách hướng>.
- Kiểm tra ứng viên cuối: <tập mẫu/seed bổ sung chưa dùng chọn config, kiểm tra biên độc lập hoặc full; nêu giới hạn còn lại>.

<!-- Ghi kế hoạch trước khi thử. Giai đoạn 02 có thể chưa có JSON/run;
chỉ rõ mốc dự kiến và phần cần hoàn thiện ở 03 trước compile/chấm.
Nếu đổi tiêu chí sau khi thấy kết quả, giải thích lý do, không viết lại như dự đoán ban đầu. -->

## Kết luận và phiên bản tái lập

<Điền sau khi có results: hypothesis được ủng hộ/bác bỏ hay chưa đủ bằng chứng,
đánh đổi, kiểm tra bổ sung đã/chưa làm. Không chép bảng điểm hoặc log ở đây.>

| Mốc tốt nhất | Config | Commit nguồn | Run / provenance |
| --- | --- | --- | --- |
| Dev | <tên/link JSON tại commit dùng dựng> | <SHA thực tế hoặc chưa có> | <link run và provenance, hoặc chưa chấm> |
| Full | <tên/link JSON tại commit dùng dựng> | <SHA thực tế hoặc chưa có> | <link run và provenance, hoặc chưa chấm> |

<!-- Hai mode có thể chọn config/commit khác nhau. Khi sửa solution.py, giữ mapping
của mốc cũ; tên JSON cũ chạy với code mới không tái lập run cũ. Không điền SHA giả.
Dẫn permalink source/config hoặc git show <SHA>:<path> để tái lập đúng phiên bản. -->

Mã triển khai: [solution.py](solution.py). Cấu hình: [configs](configs/).
Điểm và các run: [SCORES.md](../SCORES.md).
