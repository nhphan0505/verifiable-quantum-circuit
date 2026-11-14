# [INV-51] Tái lập mạch invsqrt 46 qubit bằng source tác giả và đối chiếu KMX/KMB exact

Loại: Tái dựng từ submission (theo instructions/decompiler/04_claim.md).

## Nguồn và mục tiêu

Kế thừa generator Syed Asad Ali, Apache-2.0; [LICENSE](LICENSE.txt), [NOTICE](NOTICE.txt). Nguồn công khai: [Kaggle dataset version 12](https://www.kaggle.com/datasets/syed3000/vqcc-own-circuit-portfolio/versions/12), [discussion #758815](https://www.kaggle.com/competitions/google-verifiable-quantum-circuit-compilation/discussion/758815). Archive `invsqrt_source_zip` có SHA-256 `7d9801ae20e942dba2211a656bba6014a0a16d57da534c0b60328d1c5d9d8254`; [bằng chứng tải công khai](evidence/public_source.json). Bundle chỉ là nguồn lineage, không cần tải để compile.

Mục tiêu duy nhất là dựng KMB 291626 bytes trùng SHA-256 `321aff83636214196daa9cbc9dcc9c5e12a155bcff8d9989e98b8cee40935177`. Không thay precision, phân bổ qubit, phép quay hay thuật toán để rút gọn source. Không dùng submission/KMX nguyên bản hoặc gate payload làm dữ liệu của generator.

## Cấu trúc gọn

- [solution.py](solution.py): CLI/config, kiểm tra source đã commit và hash, điều phối build, lưu provenance.
- [circuit.py](circuit.py): các hàm số học, quản lý qubit/HMR và pass tối ưu viết bằng Python thông thường. Không nhúng source string/archive, không exec/eval code từ dữ liệu.
- [tables.json](tables.json): chỉ các trường hệ số, chương trình loader/Boolean và cấu hình thực sự cần. Giữ nguyên giá trị, thứ tự và độ dài mảng; bỏ hồ sơ thử nghiệm không được dùng.

112 file trong engine cũ được thay bởi hai file `circuit.py`/`tables.json`; cả entry point là ba file runtime. 89 định nghĩa không cần và các biến khởi tạo thừa đã bỏ. Namespace nội bộ giữ các binding có thể thay đổi và bốn ngữ cảnh carry độc lập; các nhãn đường dẫn trong registry chỉ định danh component, không nạp file Python từ đĩa. Chi tiết tại [INTEGRATION.md](INTEGRATION.md), lineage/refactor tại [upstream_changes.json](upstream_changes.json), hash source/data tại [engine_manifest.json](engine_manifest.json).

## Thuật toán và điều kiện đúng

Register `x` duy nhất có 22 qubit little-endian, x trong [1,3133452]. Mạch dùng tối đa 46 qubit và tạo pha `exp(2πi/√x)`, sau đó khôi phục input trên đúng qubit vật lý và đưa scratch về zero. Dung sai verifier là `2^-24/√x` turns; rotation synthesis dùng ngân sách dư theo verifier, không bị thay đổi bởi refactor.

1. Chuẩn hóa với bốn cờ; root.forward chuyển input chuẩn hóa thành root12 và residual10, dùng lại vùng dữ liệu.
2. Hai bộ loader dùng địa chỉ `v[5:]` để tạo D/H. Lượt đầu tạo hệ số, seed và product; từ word16 giữ signed product P15. D được đo bỏ, giữ transcript cho lượt tái dựng sau.
3. Divider dựng các hàng và history, áp phase endpoint ring26 với 33 generic rotations rồi cleanup trả P. Các history được retire và tái dựng trước khi đảo hàng tương ứng.
4. Bảng thứ hai và coefficient_forward dựng lại D để trả transcript bằng Z có điều kiện; product_inverse và seed_cleanup khôi phục residual. Tail dựng lại các root bit và trả table/debt/pha còn chờ.
5. root.inverse, normalization.inverse và restore_input_layout đưa x về đúng owner ban đầu.

Việc xóa temporary AND `t=a·b` bằng HMR cần CZ(a,b) theo outcome. Ví dụ root a6 đo sớm được tái dựng bằng `D10 XOR D11 XOR D12 XOR ((D10 XOR a5) AND (D11 XOR a5))`, rồi trả pha bằng Z(a6) có điều kiện. Khôi phục giá trị cổ điển mà thiếu correction chưa đủ đúng. Hai root bit v9/v10 được retire qua endpoint; cấu hình cố định dùng certificate e2 và v10 tái dùng gate g1 khi tái dựng. Chỉ hỗ trợ config reconstructed Q46 đã nghiệm thu, không giữ các nhánh environment thí nghiệm cũ.

Các pass hoàn thiện quét toàn miền để giữ tích tính lặp trên qubit rảnh, thay tích affine bằng Clifford/HMR correction, gộp góc Z_POW và relocate pha cuối. Chúng thao tác trên mạch vừa sinh. Metadata/preflight nguồn lịch sử được thay bằng manifest của source hiện tại; invariant số học, owner/debt và sửa pha được giữ.

## Chạy và kiểm chứng

Dùng Python 3.13 trong .venv Windows, Kickmix 1.0.0, NumPy 2.5.4, SciPy 1.18.1. Từ repo root:

```powershell
.venv/Scripts/python.exe src/invsqrt/INV-51/solution.py --config src/invsqrt/INV-51/configs/reconstructed.json
```

Config phải resolve trong configs của INV-51, gồm target hash và timeout 600s mỗi stage. Output lấy tên config dưới artifacts/invsqrt/INV-51, không ghi đè âm thầm. Không cần Linux .so, verifier hay bundle khi compile. Unix RAM limits không được enforce trên Windows. Xem [DEPENDENCIES.md](DEPENDENCIES.md).

- Đối chứng: bytes/hash submission và bản INV-51 full PASS trước refactor.
- Dự đoán: bỏ source/data dư nhưng giữ nguyên toàn bộ gate stream và metadata KMB.
- Ủng hộ: build từ source commit thật trong checkout không có engine cũ, bundle hay artifact; audit không đọc ngoài source/data mới và runtime; so bytes/hash độc lập đạt exact.
- Bác bỏ/dừng: bất kỳ byte khác, dependency cũ còn cần hoặc dữ liệu toán học bị đổi; không vá output bằng input gốc và không hạ tiêu chí exact.
- Kiểm tra: source/data manifest, so giá trị JSON được giữ với bản trước, checker/scope, unit tests và reviewer build độc lập. Không dùng trace một lần làm chứng minh; build sạch lại sau pruning là điều kiện bắt buộc.

## Kết quả lịch sử và giới hạn

Các run dưới đây giữ đúng source commit lịch sử, không gán cho source rút gọn. Full đã PASS trên 200540928 shots, default salt; worst error/tolerance 0.973575996935943 tại x=54566. Dev PASS trên 4096 input/8192 shots, cùng môi trường baseline local; hệ số dev 25.97×. Không ghi hệ số full vì baseline full khác Python/package. Điểm ở [SCORES.md](../SCORES.md).

| --- | --- | --- |
| Mốc | Config | Commit nguồn | Run / provenance |
| --- | --- | --- | --- |
| Build exact | [reconstructed](configs/reconstructed.json) | `bfe070108c6dd02649c6ba4ab3400b2f0ed50249` | [provenance](../../../results/invsqrt/INV-51/reconstructed/build_only/20261113T083955Z-exact-wopk8bm7/provenance.json), [đối chiếu](../../../results/invsqrt/INV-51/reconstructed/build_only/20261113T083955Z-exact-wopk8bm7/reconstruction_check.json) |
| Build sau review | [reconstructed](configs/reconstructed.json) | `48729436b421e7320d86e48cc0e451be0d84260e` | [provenance](../../../results/invsqrt/INV-51/reconstructed/build_only/20261113T160603Z-exact-8fe62qjo/provenance.json), [đối chiếu](../../../results/invsqrt/INV-51/reconstructed/build_only/20261113T160603Z-exact-8fe62qjo/reconstruction_check.json) |
| Dev | [reconstructed](configs/reconstructed.json) | `bfe070108c6dd02649c6ba4ab3400b2f0ed50249` | [run](../../../results/invsqrt/INV-51/reconstructed/dev_5min/20261113T084759Z-local-dev_5min-127a3b/verifier.json), [provenance](../../../results/invsqrt/INV-51/reconstructed/dev_5min/20261113T084759Z-local-dev_5min-127a3b/provenance.json) |
| Full | [reconstructed](configs/reconstructed.json) | `48729436b421e7320d86e48cc0e451be0d84260e` | [run](../../../results/invsqrt/INV-51/reconstructed/full/20261113T161038Z-local-full-c530d9/verifier.json), [provenance](../../../results/invsqrt/INV-51/reconstructed/full/20261113T161038Z-local-full-c530d9/provenance.json) |

Source rút gọn đã được build từ checkout sạch và đối chiếu exact riêng. Không tạo run verifier hoặc điểm mới từ run lịch sử; full một salt không phải liệt kê mọi transcript HMR. Reviewer phải đánh giá lại HEAD sau refactor trước merge.


## Nghiệm thu bản gọn

Commit source `d89769f0fd76190159d33298ff43948a846faad3` đã build trong checkout không có engine/worker cũ, bundle hay artifact đầu vào. KMB 291626 bytes, SHA-256 `321aff83636214196daa9cbc9dcc9c5e12a155bcff8d9989e98b8cee40935177`, so độc lập từng block với input gốc đạt RECONSTRUCTED_EXACT. Audit stage reads không có đường dẫn ngoài source mới, build directory, .venv và Python chuẩn. 13464 giá trị scalar trong dữ liệu còn lại khớp bản trước, giữ chiều/thứ tự mảng; checker/scope và 21 tests đạt.

| Mốc | Config | Commit nguồn | Bằng chứng |
| --- | --- | --- | --- |
| Compiler gọn | [reconstructed](configs/reconstructed.json) | `d89769f0fd76190159d33298ff43948a846faad3` | [provenance](../../../results/invsqrt/INV-51/reconstructed/build_only/20261114T045124Z-exact-sj15ngzo/provenance.json), [bytes/hash](../../../results/invsqrt/INV-51/reconstructed/build_only/20261114T045124Z-exact-sj15ngzo/reconstruction_check.json), [dependency audit](../../../results/invsqrt/INV-51/reconstructed/build_only/20261114T045124Z-exact-sj15ngzo/dependency_audit.json) |

Lõi engine cũ 2717606 bytes/112 file được thay bằng circuit.py + tables.json tổng 683415 bytes, giảm khoảng 75%; entry point solution.py là file runtime thứ ba. Source cũ vẫn có ở Git commit cơ sở và backup ngoài Git, không bị mất lịch sử. Không tự ghi nhận điểm/full run mới; artifact hiện tại trùng bytes bản full PASS trong bảng lịch sử.
