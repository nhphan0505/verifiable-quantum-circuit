# Instructions postprocessing

Đọc [quy tắc chung](../README.md), [CONTRIBUTING](../../CONTRIBUTING.md) và
AGENTS.md. Đây là luồng phát triển phương pháp postprocessing (PP) độc lập,
không phải vòng cập nhật experiment nguồn. Dùng lại dữ kiện trong chat, xác minh
bằng repo/GitHub và chỉ hỏi phần còn thiếu. Việc viết hoặc đọc instructions
không cấp quyền thực hiện các bước.

## Giao việc bằng số bước

| Bước | Instructions | Đầu ra / điều kiện chuyển tiếp |
| --- | --- | --- |
| 1 | [Tìm hypothesis](01_find_hypothesis.md) | Đề xuất có căn cứ, chỉ đọc; chọn hypothesis trước bước 2 |
| 2 | [Nhận Issue, mã và branch](02_claim.md) | Issue thật, owner, mã PP và branch riêng |
| 3 | [Viết DESCRIPTION](03_describe.md) | Thuật toán và kế hoạch kiểm chứng trước triển khai |
| 4 | [Triển khai và tests](04_implement.md) | API, tests có ý nghĩa, commit nguồn trước chấm |
| 5 | [Chấm kiểm chứng riêng PP](05_validate.md) | Chấm thật trên mạch cũ; không lưu run/results/config mới |
| 6 | [Kết luận và push](06_push.md) | DESCRIPTION hoàn thiện, checks, commit và push; bàn giao |

Luồng thường: **1 → chọn hypothesis → 2 → 3 → 4 → 5 → 6**.
Thử tiếp cùng hypothesis: cập nhật mô tả/code/tham số, commit rồi kiểm chứng lại
theo bước 4–5, trong giới hạn đã giao. Không tự mở rộng thành quét vô hạn.
Phát triển PP kết thúc ở push; không bắt buộc áp dụng vào experiment cũ.
Review, PR và merge chỉ làm khi được giao riêng, theo quy tắc review/check thật
của repository; push không có nghĩa đã review/merge hoặc được đóng Issue.

## Phạm vi và cấu trúc

Mã phương pháp có dạng `PP-001`, duy nhất toàn repo, độc lập số Issue GitHub.
Không đánh số lại theo track. Một phương pháp có một owner và một Issue quản lý
hypothesis PP; experiment cung cấp mạch chỉ là nguồn benchmark.

```text
src/common/postprocessing/
  METHODS.md                       # Danh mục mã PP toàn repo
  PP-001/
    DESCRIPTION.md
    solution.py
    tests/
src/<track>/postprocessing/
  PP-002/
    DESCRIPTION.md
    solution.py
    tests/
```

`<track>` là `invsqrt`, `dqi` hoặc `dfthcsos`. Chỉ chọn một vị trí cho mỗi
phương pháp. Mã giữ nguyên khi chuyển phạm vi; việc di chuyển cần được giao.
METHODS.md ghi mã, tên, phạm vi, owner, link Issue và link DESCRIPTION.

File thêm/sửa có chủ đích chỉ nằm trong `src/common/postprocessing/` hoặc
`src/<track>/postprocessing/`: thư mục phương pháp được giao và dòng danh mục
của nó. Không sửa experiment, configs, EXPERIMENTS.md, SCORES.md, results,
verifier, notebook, checker hoặc hạ tầng khác. API/pipeline chung vượt phạm vi
một phương pháp cần nhiệm vụ hạ tầng riêng, không tự bổ sung trong lúc thử PP.

Không tạo thư mục configs hoặc bản ghi kết quả cho lần kiểm chứng PP. Tham số
được truyền qua API/CLI và mô tả trong DESCRIPTION; tests có thể chứa các giá
trị kiểm thử. API phải cho phép experiment gọi lại sau này, nhưng tích hợp và
config của experiment thuộc công việc khác do người dùng chủ động giao khi
mở lại experiment.

## Quy tắc kiểm chứng

- Phải có hypothesis và DESCRIPTION trước khi triển khai/thử.
- Chỉ bật PP đang kiểm chứng. Đầu vào chưa qua PP khác, xác minh bằng nguồn và
  pipeline tạo mạch; hash giống nhau không tự chứng minh chưa có PP.
- Đối chứng và ứng viên dùng cùng bytes mạch gốc, cùng điều kiện chấm. Không
  đổi tham số dựng mạch nguồn để làm PP có lợi hơn.
- Chấm theo [LOCAL_GRADING](../../docs/LOCAL_GRADING.md): hiện dùng
  kickmix-engine 0.6.0, chỉ `smoke`/`full`; Windows dùng WSL và môi trường engine
  Linux. Không fallback sang engine cũ khi thiếu môi trường. Giữ nguyên verifier
  và điều kiện bài, không chỉ đếm qubit/Toffoli. Kiểm tra tính đúng trên
  mạch nhỏ và đánh giá đúng đại lượng chi phí của bài.
- Khác luồng experiments, bước 5 cho phép agent chạy chấm local phục vụ kiểm
  chứng PP. Không tạo run, provenance JSON, bảng điểm hoặc log lưu lâu dài.
- Artifact/log cần cho verifier chỉ tồn tại tạm trong thư mục tạm riêng của
  lần kiểm tra, ngoài thư mục experiment/results. Không commit chúng. Trước
  khi dọn, xác minh đường dẫn tuyệt đối và chỉ xóa dữ liệu tạm do mình tạo.
- DESCRIPTION lưu cách kiểm chứng, nguồn/hash đầu vào, phiên bản, tham số,
  kết luận và giới hạn; không chép bảng điểm hoặc log chấm. Báo số đo thực tế
  trong chat, phân biệt smoke/full và chưa kiểm tra. `dev_5min` chỉ là dữ liệu
  lịch sử, không dùng làm mode cho lần chấm mới.
- Chỉ bật nhiều PP trong một công việc kết hợp riêng được giao, sau kiểm chứng
  độc lập; không lấy kết quả phối hợp làm bằng chứng cho một PP đơn lẻ.

Khi đổi chat, không coi kết luận trong mô tả là một run chấm còn lưu. Nếu cần
xác nhận lại mà bằng chứng tạm đã mất, chạy lại khi được giao; không bịa kết quả.
Nếu công cụ hiện có bắt buộc ghi vào results hoặc checker chưa hỗ trợ cấu trúc
PP, báo xung đột; không sửa/bypass hạ tầng hoặc tạo miễn trừ để nghiệm thu.
