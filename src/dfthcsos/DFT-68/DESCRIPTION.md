# [DFT-68] Tái dựng 15 loader DFTHC bằng plan Boolean và dữ liệu factorization cố định

Loại: Tái dựng từ submission; owner nhphan0505.

## Nguồn và mục tiêu
Kế thừa compiler của Syed Asad Ali, Apache-2.0, từ bundle dfthcsos_source.zip (SHA-256 a3e5747c6211c465cc211df4608beab59898e806d1dbddc5624b674dae8d3fea), thuộc [VQCC Own-Circuit Portfolio](https://www.kaggle.com/datasets/syed3000/vqcc-own-circuit-portfolio). Người dùng cung cấp 15 angle_k_0..14.kmb và submission.npz dưới tên dfthcsos__*. Notebook tác giả kiểm hash từng thành phần rồi đóng ZIP chung cả ba bài; không có ZIP DFTHC gốc để so container. Mục tiêu là khớp bytes từng thành phần và tạo ZIP DFTHC ổn định theo tiện ích chung; không tuyên bố hash ZIP gốc đã khớp.

## Thuật toán và phạm vi
Phục hồi loader từ các plan explicit_products đã đóng băng, không chạy lại randomized matching/search. Bảng angle_words có 1220 địa chỉ x 75 word, 8 bit/word; chia 15 batch, 5 word/batch. Selection 11 qubit, 5 register word 8 bit. Compiler hoàn tất 12 địa chỉ padding, phân rã Boolean low/high và các product GF(2), phát CNOT/Toffoli, HMR với CZ sửa pha rồi xóa cache. ANGLE_0 dùng lịch low-cache tám bit sống; ANGLE_8 dùng high-subspace cache; các batch còn lại dùng full high-cache. Giữ kiểm chứng algebra và phase correction của nguồn. Điều kiện loader là hai endpoint hợp lệ theo tác giả, chưa nhận đã chứng minh toàn Hilbert space.

NPZ gồm U(float64,8x143x76), W(float64,8x143x44), H2_I(float64,8x44), H1_I(float32 scalar), Hsym_lower(float32,2926), tree_edges(int64,75x2), angle_words(int64,1220x75). Lưu mảng dưới dạng dữ liệu số text có dtype/shape, dựng lại NPY và NPZ với metadata ZIP xác định. Đây là dữ liệu fitting cuối, không nhận đã phục hồi quá trình tìm factorization. Không tạo postprocessing.py theo yêu cầu người dùng; không tối ưu hay đổi dữ liệu.

## Implementation và dependency
solution.py điều phối, circuit.py gom các hàm compiler thực sự dùng, data.json chứa mảng số/plan/lịch cần thiết; config reconstructed.json và reconstruction.json/hash manifest khai báo nguồn. Giữ LICENSE/NOTICE. Không bê nguyên research/bundle hoặc KMB/KMX vào Git, không dùng local Downloads/scratch làm đầu vào build. Gọi src/common/package_submission.py để đóng gói, không nhân bản logic ZIP. Windows Python 3.13, kickmix 1.0.0 và NumPy 2.5.4 theo requirements, không WSL/so của tác giả.

## Kế hoạch kiểm chứng hypothesis
Hypothesis tái lập: Python phát 15 KMB và NPZ khớp bytes/hash công bố; không phải giả thuyết tối ưu mới. Đã kiểm chuyển trực tiếp và KMB-KMX-KMB cho cả 15 file: tất cả exact. Đã kiểm serialization lại các mảng NPY/NPZ: NPZ khớp SHA-256 6418ec8e10b1a8da967ee26278434f9ac950474741185f4d61363e17a03da77f sau cố định metadata Unix. Source/config phải commit và push trước build; build lại entry point từ checkout GitHub sạch với venv mới, cwd khác, audit input-file reads. So bytes mọi thành phần và NPZ/NPY; đóng ZIP hai lần kiểm determinism. Lưu provenance source/config/helper/data/package/environment/hashes và records mới. Nếu mismatch thì tìm nguyên nhân, commit lại, không vá từ KMB gốc. Thiếu dữ liệu thì báo blocker.

## Tài nguyên, baseline và giới hạn
Manifest tác giả ghi tổng 4074 Toffoli mỗi pass của ANGLE và điểm lịch sử 296635967.5935997; đây là công bố nguồn; kết quả chấm riêng của repo được ghi bên dưới. Baseline DFT-BASELINE là QROM batch 8; không suy điểm cải thiện chỉ từ khác batch hoặc gate count. Đã có run full PASS của repo và dòng DFT-68 trong SCORES; kết quả và provenance được ghi ở mục "Full PASS của nhóm" bên dưới. Giữ data cuối nguyên bytes; fitting/refit thiếu đầu vào v18 không nằm trong build này. Không claim original ZIP exact; chỉ nghiệm thu component-exact cho tập đầu vào đã cung cấp, container mới deterministic.

## Kết quả và tái lập
Build sạch đã thành công từ commit nguồn `7df5dad8ca74a8610dd6597c53057f6cd7f30a4c` trên clone GitHub và venv mới, chạy entry point từ cwd ngoài checkout. Không tạo postprocessing.py. Mốc này là build-only; kết quả chấm full mới ở phần bên dưới. Chờ review độc lập; không tự merge.


## File bàn giao và cách chạy

- [solution.py](solution.py): resolve config, xác minh snapshot nguồn, dựng arrays/NPZ và loaders, audit input reads, gọi tiện ích chung và lưu build_only provenance.
- [circuit.py](circuit.py): 18 hàm compiler thực sự dùng; gom từ các module compiler của tác giả, bỏ CLI/search/matching ngẫu nhiên và nhánh không có trong plan cố định. Không dùng exec/eval hoặc nhúng mã nguồn dạng chuỗi. Các nhánh không có explicit products bị từ chối.
- [data.json](data.json): mảng số có dtype/shape, 15 plan product/cache và lịch ANGLE_0; không phải KMB/KMX hoặc NPZ đóng gói lại dưới dạng mã hóa. Không có dependency bundle hay bản binary tác giả. Dữ liệu float text được kiểm khôi phục đúng bit, bao gồm dtype float32/float64.
- [configs/reconstructed.json](configs/reconstructed.json): batch 5, word 8 bit, plan cố định; [reconstruction.json](reconstruction.json): hash mục tiêu, nguồn/giới hạn và mapping build. Metadata nghiệm thu cập nhật sau build không được gán ngược vào SHA nguồn đã dùng.
- [LICENSE.txt](LICENSE.txt), [NOTICE.txt](NOTICE.txt): giữ Apache-2.0 và attribution tác giả; evidence chỉ giữ manifest, inventory và kết quả roundtrip cần cho review.
- [Tiện ích đóng gói chung](../../common/package_submission.py) ở commit `6ef65d8` là dependency có hash trong provenance. Không đổi helper chung trong hướng này.

Tạo venv Python 3.13, cài `requirements.txt` của checkout. Từ root repo:

```powershell
.venv/Scripts/python.exe src/dfthcsos/DFT-68/solution.py --config src/dfthcsos/DFT-68/configs/reconstructed.json
```

Đầu ra `artifacts/dfthcsos/DFT-68/reconstructed.zip`; từ chối ghi đè. Chạy từ cwd khác bằng đường dẫn tuyệt đối tới Python/solution/config. Dùng `git checkout 7df5dad8ca74a8610dd6597c53057f6cd7f30a4c` trong checkout riêng để tái lập chính xác mốc nguồn build đã nghiệm thu. Tham khảo setup commands trong record bên dưới; không cần Downloads, WSL hoặc kickmix.so.

## Đối chiếu code và thuật toán

`solution.complete` giữ Mobius completion của upstream `rebuild.complete`, bảo toàn 1220 địa chỉ thật. `circuit.apply_padding_completion` xác minh prefix hash rồi thay đúng 12 địa chỉ ngoài miền khi plan có chỉ định. `cross_tensor` tách delta thành high/low Boolean tensor; `basis`, `outer`, `coordinate_basis`, `coordinates` kiểm biểu diễn product và correction trên GF(2). `separate_helpers` xác minh tách low/high helper. `emit_k0_emit` nhận lịch sự kiện k0; `emit_plan_emit` dùng full cache hoặc gọi `high_subspace_emitter_emit` cho ANGLE_8. `synthesize_low_cache` dựng low algebra từ helper đã sống. Mọi compute AND giữ cleanup HMR cùng CZ bù pha và thứ tự nguồn; không tối ưu cổng trong lần tái dựng này.

`solution.write_npz` sinh NPY từ dữ liệu số rồi ghi ZIP_STORED, timestamp 1980, create_system=3, quyền 0600 và local ZIP64. Cần metadata cố định vì `np.savez` mặc định trên Windows cho cùng NPY nhưng khác header ZIP trung tâm so với nguồn Unix. Không vá binary từ submission gốc.

## Nghiệm thu build và giới hạn

Config `reconstructed`, source commit `7df5dad8ca74a8610dd6597c53057f6cd7f30a4c`:

- [Provenance](../../../results/dfthcsos/DFT-68/reconstructed/build_only/20261115T052652Z-build-u3fl7wvi/provenance.json), [setup clone/venv sạch](../../../results/dfthcsos/DFT-68/reconstructed/build_only/20261115T052652Z-build-u3fl7wvi/clean_build_setup.json), [stdout](../../../results/dfthcsos/DFT-68/reconstructed/build_only/20261115T052652Z-build-u3fl7wvi/build.stdout.txt).
- [Đối chiếu độc lập](../../../results/dfthcsos/DFT-68/reconstructed/build_only/20261115T052652Z-build-u3fl7wvi/reconstruction_check.json): 16 thành phần so từng byte theo luồng đều khớp; 7 member NPY có bytes/dtype/shape/order khớp, không allclose. NPZ SHA-256 `6418ec8e10b1a8da967ee26278434f9ac950474741185f4d61363e17a03da77f`.
- [Audit](../../../results/dfthcsos/DFT-68/reconstructed/build_only/20261115T052652Z-build-u3fl7wvi/dependency_audit.json): 22 đường dẫn đọc sau setup/snapshot, không có input ngoài checkout/runtime và file mới tạo của build. Compiler và đóng gói chạy trong một Python process; Git chỉ dùng trước audit để xác minh snapshot/provenance. Không tuyên bố audit Python theo dõi syscall nội bộ thư viện native.
- [Build report](../../../results/dfthcsos/DFT-68/reconstructed/build_only/20261115T052652Z-build-u3fl7wvi/build.json): 15 loader, tổng 4074 Toffoli/pass theo compiler, serialization và packaging hai lần cho cùng ZIP SHA-256 `fc481755b7b97fa73ae9256e775907b82835b835d5520b3c529440d647bcab8a`.

Mức đạt: COMPONENTS_EXACT và BUILT. ZIP mới chứa 16 file DFTHC ở gốc; notebook Kaggle người dùng cung cấp đóng ZIP chung 18 file với ba bài và prefix dfthcsos/. Hai container phục vụ hai giao diện khác nhau; không tuyên bố toàn ZIP gốc exact. Các build-only không chạy lại fitting, exhaustive symbolic proof hoặc official grading; không gọi build-only là verifier PASS. Kết quả chấm riêng được ghi bên dưới.


Lặp lại build sạch sau cập nhật metadata nghiệm thu, source commit `5c97b93`:
[provenance](../../../results/dfthcsos/DFT-68/reconstructed/build_only/20261115T053100Z-build-co4afj7g/provenance.json),
[đối chiếu bytes](../../../results/dfthcsos/DFT-68/reconstructed/build_only/20261115T053100Z-build-co4afj7g/reconstruction_check.json).
Entry point hoàn tất với cùng ZIP hash và 16 thành phần exact. Đây là build mới,
không sửa record của mốc nguồn `7df5dad`. Repository checker/scope: 0 lỗi;
bộ 34 tests repository đã đạt, các thay đổi audit sau đó được kiểm bằng build end-to-end.


## Full PASS của nhóm

Config `reconstructed`: [run full](../../../results/dfthcsos/DFT-68/reconstructed/full/20261115T055007Z-local-full-edb6ea/verifier.json),
[metadata](../../../results/dfthcsos/DFT-68/reconstructed/full/20261115T055007Z-local-full-edb6ea/metadata.json),
[provenance](../../../results/dfthcsos/DFT-68/reconstructed/full/20261115T055007Z-local-full-edb6ea/provenance.json),
[giải quyết build cùng hash](../../../results/dfthcsos/DFT-68/reconstructed/full/20261115T055007Z-local-full-edb6ea/review_resolution.json).
Người dùng chạy notebook bằng kickmix-engine 0.6.0 (Linux/WSL, Python 3.13.18);
compiler/rebuild trước đó chạy native Windows venv. Không trộn hai môi trường.

Full PASS trên 78080 shots = 1220 địa chỉ x 64. Điểm `296635967.5935997`, lambda_eff
`46.907347493481`, Toffoli `14810.0`, qubit `427`;
15 loader, brot=8, batch=5. Error_1 `0.019610371288992456`,
error_2 `0.019998779892854764`, E_gap `3.914898200000607`.
E_gap chỉ cao hơn ngưỡng 3.914898 khoảng 2e-7 Ha và error_2 gần ngưỡng 0.02;
không suy ra biên an toàn rộng hoặc tự thay đổi dữ liệu sau PASS.

Baseline full của nhóm có score `3355599588.3155375`:
[run đối chứng](../../../results/dfthcsos/DFT-BASELINE/baseline/full/20261113T190138Z-local-full-e2ab8f/verifier.json).
Baseline/candidate = `11.31218043` lần. Hai mạch khác brot, batch, factorization và
số địa chỉ; đây là so chi phí toàn phương án, không cô lập tác động của compiler
hoặc một thay đổi thuật toán. Không quy toàn bộ cải thiện cho giảm Toffoli loader.

Artifact đã chấm có ZIP SHA-256 `fc481755b7b97fa73ae9256e775907b82835b835d5520b3c529440d647bcab8a`, 16 component hashes
khớp manifest và build. Nguồn thực tế nối về `7df5dad8ca74a8610dd6597c53057f6cd7f30a4c` qua build_run
`20261115T052652Z-build-u3fl7wvi`, không gán HEAD khi chấm làm SHA nguồn. Notebook giữ nguyên review.json
báo hai build cùng hash; thêm review_resolution.json và provenance.json thay vì sửa
record gốc. Verifier submission_sha256 là fingerprint nội dung, không phải ZIP hash;
ZIP hash được đối chiếu từ upload_artifact trong metadata.

Kết luận: giả thuyết tái dựng từng thành phần được kiểm bằng bytes; phương án cuối
đạt full PASS thực tế. Dừng tái dựng ở đây, không chạy refit hoặc tối ưu thêm trong
hướng này. Bước còn lại là review độc lập code–thuật toán, tái lập và bằng chứng
chấm trên PR #69; chưa có approval/merge.
