# [DQI-56] Tái lập decoder q26 từ mã nguồn và giản lược CNOT giao hoán

**Loại** — Tái lập decoder và tinh chỉnh số lệnh Clifford.

## Nguồn và đối chứng

- Mã Python và các kế hoạch compiler của q26 lấy từ gói [QCC C44 Five Helper Release Sources v1 của Atakan Aldemir](https://www.kaggle.com/datasets/atakanaldemir/qcc-c44-five-helper-release-sources/versions/1), đường dẫn kết thúc bằng `packet/blocks/dqi/carry-q26-892/source/`. Xem thêm [notebook QCC Terminal Readout and Phase Folds của Atakan](https://www.kaggle.com/code/atakanaldemir/qcc-terminal-readout-and-phase-folds) để tham khảo hướng compiler.
- [Notebook Quantum Circuits Conditional Uncompute Audit của Kirill](https://www.kaggle.com/code/kirilltym/quantum-circuits-conditional-uncompute-audit?scriptVersionId=367172760) là nguồn đối chiếu V5. [DQI-39](../DQI-39/DESCRIPTION.md) lưu kết quả V5 của repo. q26 dùng mã Python từ gói Atakan.
- Đối chứng trực tiếp cho bước giản lược CNOT là q26 gốc, SHA-256 `b7ca9bce749dcd049f94326446e90cad474b51e6e0abf81561fc37f261abf69b`.

## Phương pháp

Bộ sinh khai báo 70 word syndrome và 4.095 word mask runtime trên GF(2¹²). Nó chiếu mask, đổi biểu diễn syndrome tuyến tính, trích xuất dữ liệu giải mã, tổng hợp locator/evaluator, chuyển biểu diễn rồi quét để áp pha. Các bước ngược hoàn nguyên syndrome và mask; phần unsynthesis tiêu thụ thông tin lịch sử và định tuyến lại thanh ghi. `solution.py` gọi các hàm decoder upstream theo từng bước, sau đó tối ưu luồng cổng của mạch vừa sinh.

Trong một đoạn chỉ gồm CX không điều kiện, CX(a,b) và CX(c,d) giao hoán khi a ≠ d và b ≠ c. Hai CX giống nhau triệt tiêu nếu có thể di chuyển chúng lại gần nhau theo quy tắc đó. Cổng khác, điều kiện và giới hạn bộ đệm chặn việc gộp. Bộ sinh kiểm tra lại khai báo thanh ghi, số qubit/bit, số Toffoli-like tĩnh và chênh lệch số lệnh sau biến đổi.

## Dựng và kiểm chứng

Tải bản ZIP của dataset v1 ở trên, chứa `release_source.xz`. Chạy từ thư mục gốc repo bằng Python 3.13 và Kickmix 1.0.0.

```sh
python src/dqi/DQI-56/solution.py \
  --source-bundle /path/to/qcc-c44-five-helper-release-sources.zip \
  --output /tmp/q26-cx-cancel.kmb
```

Config mặc định `configs/q26_cx_cancel.json` ghim SHA-256 của `release_source.xz`. Bộ sinh chỉ trích xuất tệp Python và JSON của khối q26 vào thư mục tạm. Gói mã nguồn upstream là đầu vào bắt buộc. Không cần mạch `.kmb` upstream và PR không phân phối lại gói mã nguồn.

Bản thử cục bộ trước khi đóng gói CLI đạt 892 qubit và 457.906 Toffoli-like tĩnh ở cả hai phiên bản. Bước giản lược bỏ 7.910.160 CX, giảm tổng số lệnh từ 63.887.951 xuống 55.977.791 (12,38%). Đối chiếu 16 trajectory ghép cặp khớp quantum bits, classical bits và pha. SHA-256 của bản đã giản lược là `7f71a310ac1f61f86f908c3c61375c879da4caca7db9b140e966195e8e4d01d1`.

Phép giản lược giữ `Q²T`. Mục tiêu đo tiếp là thời gian verifier và số lệnh trên cùng harness, seed và profile. Chủ thử nghiệm báo điểm dev `956538238429.3275`; chưa có bản ghi grader liên kết điểm này với hash bản dựng, nên dùng làm số tham khảo. Cần run dev với provenance để đối chiếu chính thức và full nếu tiếp tục báo cáo điểm.
