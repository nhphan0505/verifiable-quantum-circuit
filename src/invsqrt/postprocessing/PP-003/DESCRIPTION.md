# [PP-003] Gộp pha Z_POW trên cùng hàm Boolean

Owner: nhphan0505. Issue: [#62](https://github.com/nhphan0505/verifiable-quantum-circuit/issues/62).
Phạm vi: invsqrt; di chuyển phương pháp đã có, không phải hypothesis tối ưu mới.
Nguồn: Syed Asad Ali, Apache-2.0; xem [LICENSE](LICENSE.txt), [NOTICE](NOTICE.txt).
Kế thừa [circuit.py](../../INV-51/circuit.py) tại commit
`1390fe402fb1779d3798ae344de3ce73edac93f5`.

## Hypothesis của việc di chuyển

Tách vị trí source và giữ nguyên AST thuật toán cùng namespace mutable sẽ giữ
nguyên output từng stage và KMB cuối có SHA-256
`321aff83636214196daa9cbc9dcc9c5e12a155bcff8d9989e98b8cee40935177`.
Không dự đoán cải thiện chi phí; bác bỏ refactor nếu output khác hoặc mất dependency.

## API và dependency

[solution.py](solution.py) chứa implementation thật của các stage: tools/merge_zpow.py.
`run(backend, stage, args)` nhận backend circuit INV-51 và danh sách tham số CLI;
output ghi tới đường dẫn do caller truyền, không sửa input tại chỗ. Tham số giữ
nguyên CLI upstream; xem các khai báo argparse trong source. `initialize` là
adapter giữ globals của component trong backend; không dùng chuỗi source/exec.
Nạp module theo đường dẫn vì mã PP có dấu gạch ngang. INV-51 tự nạp module mới
qua registry adapter khi chạy pipeline hiện có. Parser/simulator và bảng dữ liệu
vẫn nằm trong INV-51, do đó đây chưa phải thư viện độc lập với backend đó.
Không có config JSON hoặc kết quả chấm mới cho việc di chuyển.

## Kế hoạch kiểm chứng và giới hạn

Tests khóa AST của implementation gốc và kiểm tra API từ chối stage/factory sai.
Kiểm tra từng stage cũ/mới trên cùng input và tham số, rồi đối chiếu KMB cuối;
chỉ dùng output tạm. Đây là kiểm tra tương đương refactor pipeline cũ đã có
nhiều PP, không phải thử một hypothesis PP mới. Không dùng kết quả pipeline
làm bằng chứng lợi ích riêng từng PP. Tests AST không thay chứng minh thuật toán.
Không sửa records lịch sử, không tạo config/run/results hoặc bảng điểm mới.
## Kết quả kiểm tra refactor

12 tests của bốn module đã chạy đạt. Integration test
[finishing pipeline](../tests/test_inv51_pipeline.py) chạy bốn stage giữ tích,
rewrite affine, merge Z_POW và relocate trên cùng dữ liệu trung gian trước khi
di chuyển: các KMX khớp từng byte, KMB cuối khớp target SHA-256 ở trên.
Các bước audit_pairs/audit_affine được khóa AST gốc, chưa chạy lại audit toàn
miền trong integration test này; records audit cũ chỉ là input test.
Không chạy lại generator từ đầu hoặc verifier smoke/full; không tuyên bố PASS
mới. Không tạo config/results hay thay records lịch sử.

Để chạy lại, đặt biến môi trường INV51_REFERENCE_BUILD tới build gốc có raw/
và final/, chạy unittest discover tại src/invsqrt/postprocessing/tests. Outputs
được tạo và dọn trong TemporaryDirectory. Fixture lớn không được commit.
Checker đã được cập nhật để kiểm tra phương pháp PP riêng với experiment: mã
duy nhất, DESCRIPTION, implementation, tests và không có configs kiểm chứng.

## Thuật toán và điều kiện đúng

Nhóm Z_POW vô điều kiện khi vector giá trị Boolean trên miền input giống nhau; cộng góc bằng Fraction modulo 2. Giữ Clifford, T và generic rotation đúng phân loại. Điều kiện: biểu thức pha và nhánh đo phải phù hợp; hash vector không tự là chứng minh cho miền ngoài phạm vi.
