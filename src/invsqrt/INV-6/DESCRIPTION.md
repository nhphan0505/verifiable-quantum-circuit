# [INV-6] Giảm độ rộng thanh ghi và bù thiên lệch cắt cụt trong hệ số Horner cùng hằng số Newton

Loại: Tinh chỉnh một phương án.

## File gốc

Kế thừa [INV-BASELINE/solution.py](../INV-BASELINE/solution.py) và
[baseline.json](../INV-BASELINE/configs/baseline.json) tại commit
`be1a7e71e02f8d0de459465690a0295bcf5caa9d`; attribution Apache-2.0 tại
[src/LICENSE.txt](../../LICENSE.txt). Verifier và reference gốc giữ nguyên,
hash trong [data_manifest.json](../../../data_manifest.json).
Nguồn ý tưởng offset: [note ready đã merge](../../../research/invsqrt/papers/arxiv-2308.12352/note.md),
mục một bước hiệu chỉnh và hypothesis; không coi ước lượng 15 bit của paper là bảo đảm cho mạch này.

## Phần tinh chỉnh và lý do

Horner và Newton dùng phép nhân bỏ từng cột partial product dưới LSB, khác với
làm tròn một tích chính xác. Giảm bit có thể gây thiên lệch tích lũy. Thử dịch bảng
hệ số bằng số nguyên và hằng số Newton để cân bằng sai số có dấu quanh 0.
Chỉ sửa Precision.coefficient_table, Precision và hằng số _correct cùng mô hình
fixed_point_model tương ứng. Không lấy lịch trình cấp phát của INV-3; giữ nguyên
compute/phase/uncompute, bộ cộng, chuẩn hóa và mọi primitive baseline.

## Cách thực hiện và đánh đổi

Bảng bốn khoảng có công thức `C[i,j] = round(a[i,j]*2^wc) + coefficient_bias[i][j]`.
Bias có shape 4 x 4, là số nguyên theo đơn vị 2^-wc, được XOR bằng gf2_iadd nên
không thêm Toffoli. Bias hệ số không phải offset thực rất nhỏ trong paper.
Newton đổi `correction = (3<<wz) + z_bias - T(M*T(y0^2))`, với z_bias nguyên theo
đơn vị 2^-wz. _correct compute dùng phép đảo bit rồi cộng `(3<<wz)+1+z_bias`;
uncompute trừ đúng cùng hằng số rồi đảo bit. Mọi bước nhân dùng truncation và
scale baseline; `p` có wp+1 bit, `y1=p<<s` có wp+n_p+1 bit.

Config balanced giảm `(d,wc,wsq,wz,wp)` từ `(14,17,28,28,29)` xuống
`(13,16,27,27,28)`, bias c0=-2 LSB ở cả bốn khoảng, ba cột còn lại bằng 0,
z_bias=-1 LSB. Lịch cấp phát tĩnh giữ nguyên. Phải kiểm tra mọi hệ số vừa thanh
ghi, các trung gian Horner dương dưới 2^wc, correction trong [0,2^(wz+2)) và
mọi tích không tràn. Nếu overflow thì không được wrap để che lỗi mô hình.
Độ rộng nhỏ hơn giảm qubit/Toffoli, nhưng margin nhỏ hơn có thể tăng chi phí tổng
hợp Z_POW. Giá trị hằng số thay đổi cũng có thể thay số cổng cộng hằng.

## Kế hoạch kiểm chứng hypothesis

- Đối chứng: baseline source/config tại commit trên; [dev baseline](../../../results/invsqrt/INV-BASELINE/baseline/dev_5min/20261107T180810Z-local-dev_5min-eb9c85/verifier.json),
  profile seed=20261106, samples=4096, repeats=2, Python 3.13.14/Kickmix 1.0.0.
- Sàng lọc ban đầu bằng mô hình (không dựng artifact): 7 bộ độ rộng, c0 bias
  thuộc {0,-1,-2,-3}, z_bias từ -10 đến 6 trên lưới đều 32768 điểm cộng x=1..4096
  và biên lũy thừa hai; không dùng tập dev để chọn. Đây là tìm cấu hình, không
  phải kiểm tra độc lập. Balanced có max error/tolerance khoảng 0.725 trên lưới.
- Trước build kiểm tra toàn bộ 3,133,452 số x bằng mô hình từng bit; so balanced
  với cùng độ rộng nhưng bias=0 và baseline. Không tràn, max ratio <0.95 là điều
  kiện chọn balanced; nếu không đạt chỉ thử tối đa hai cấu hình an toàn hơn có
  wsq hoặc wz cao hơn. Không tối ưu tiếp trên dev.
- Dự đoán: Q giảm khoảng 12–16, Toffoli giảm khoảng 900–1300; Q*C có thể giảm
  15–22%. Đây là dự đoán, chưa có điểm verifier. Bù bias phải giúp giảm cực đại
  sai số so cùng widths không bias hoặc tăng margin đủ để giảm widths.
- Kiểm tra local mô hình với compute_only trên mẫu độc lập gồm biên bốn khoảng,
  biên normalize và random seed chưa dùng chọn config; kiểm tra compute-phase-
  uncompute với nhiều seed đo, x phục hồi, scratch=0 và pha bằng mô hình.
- Dev chỉ được coi ủng hộ khi PASS, score thấp hơn baseline cùng profile và
  đủ provenance/môi trường để so. FAIL/overflow hoặc mọi ứng viên hẹp có ratio>=1
  là bằng chứng bác bỏ cấu hình tương ứng; tăng synthesis làm mất lợi ích cũng
  bác bỏ lợi ích Q*C. Không suy ra PASS chỉ từ mô hình hay tài nguyên build.
- Dừng khi có một artifact để bàn giao notebook local. Ứng viên cuối cần full
  hoặc tập/seed bổ sung và đối chứng tương thích trước khẳng định chất lượng;
  dev không thay thế full. Không đổi verifier hay hạ tầng trong Issue này.

## Vòng thử tiếp: delta12

Theo yêu cầu bước 05, tạm hoãn full và mở đúng một vòng config bổ sung; đây là
thay đổi kế hoạch sau dev balanced, không sửa tiêu chí của lần thử balanced.
Không chọn theo bộ mẫu dev. Giữ balanced/dev tại source commit cũ làm mốc.

Ứng viên delta12 lấy bộ đã sàng lọc bằng lưới mô hình trước dev: widths
(12,16,27,27,28), c0 bias=-3 ở cả bốn khoảng, z_bias=-2, các hệ số khác bias=0.
Chỉ giảm delta_bits một bit so balanced, bù lại bằng bias đã chọn trên lưới cũ;
giữ nguyên lịch cấp phát, model/circuit implementation và độ rộng Newton.
Trên lưới sàng lọc cũ max ratio khoảng 0.8093, chưa là bảo đảm toàn miền.

Trước build phải chạy validate_model trên toàn miền, không overflow và
max ratio <0.95, rồi mô phỏng biên/random với sample-seed=20261109 và ba seed
đo đã có. Không nới ngưỡng nếu thất bại. Nếu không đạt thì loại delta12 trước
build và ưu tiên một config bù bias tăng margin ở cùng widths balanced thay vì
quét thêm độ rộng Newton. Tối đa một artifact bàn giao cho vòng này.

Dự đoán trước build: giảm hàng nhân Horner nên Toffoli có thể giảm, Q có thể
không đổi vì độ rộng thanh ghi vật lý không đổi; bias hằng Newton có thể đổi
chi phí cộng hằng. Không suy ra tổng score từ giảm Toffoli vì synthesis phụ
thuộc margin. Đối chứng dev: balanced run 20261108T015743Z-local-dev_5min-d222d7,
seed=20261106, samples=4096, repeats=2. Chỉ chọn thay balanced nếu dev PASS và
score nhỏ hơn 1843434.5705617426; nếu kém hoặc FAIL thì giữ balanced và dừng
vòng này. Không sửa điểm hoặc mapping balanced khi chưa có run mới.

Kiểm tra trước build delta12: max ratio mô hình toàn miền 0.9309830032 tại
x=284671, khoảng có dấu [-0.9309830032,0.8817613535], không overflow.
Cùng widths nhưng bias=0 có max ratio 1.5035512019. Mô phỏng 374 đầu vào với
sample-seed=20261109 và ba measurement seeds khớp output/pha mô hình, x phục hồi,
scratch=0. Tài nguyên đo local Q=251, Toffoli=6989, giảm 108 Toffoli so balanced;
Q không đổi như dự đoán. Kết quả dev sau đó được phân tích bên dưới.
validate_model.py nhận --config và --sample-seed để tái lập từng cấu hình;
solution.py giữ nguyên, mapping/source commit của balanced không đổi.

Artifact delta12 đã BUILT từ source/config commit `8d14de54075cf006040358a5bf91a1ef48adbb17`.
[Provenance delta12](../../../results/invsqrt/INV-6/delta12/build_only/20261108T020740Z-local-build/provenance.json),
[báo cáo kiểm tra delta12](../../../results/invsqrt/INV-6/delta12/build_only/20261108T020740Z-local-build/model_validation.json).
Chấm notebook local trong D:/GQA: TRACK=invsqrt, MODE=dev_5min,
EXPERIMENT_ID=INV-6, OWNER=nhphan0505, CONFIG_NAME=delta12. Results mới dự kiến
ở results/invsqrt/INV-6/delta12/dev_5min/. Delta12 đã dev PASS trong run bên
dưới và thay balanced làm mốc dev tốt nhất; chưa có kết quả full.

## Kết luận và phiên bản tái lập

Delta12 đạt dev_5min PASS trong run `20261108T021502Z-local-dev_5min-b9ca90`,
4096 đầu vào x 2 lần đo (8192 shots), seed=20261106. Hash artifact, provenance
build, source/config commit, môi trường Python/package và toàn bộ hash verifier/
dev harness khớp cả baseline và balanced; tập input hash giống nhau và stdout
JSON khớp verifier.json. [Phân tích đối chiếu](../../../results/invsqrt/INV-6/delta12/dev_5min/20261108T021502Z-local-dev_5min-b9ca90/analysis.json).

Kết quả đạt tiêu chí đã ghi trước vòng thử: Q giữ 251, Toffoli giảm 7097 xuống
6989, C giảm 7344.360838891405 xuống 7235.947049161165, điểm giảm thêm 1.48%
so balanced. So baseline, Q giảm 260 xuống 251 (3.46%), Toffoli giảm 7735 xuống
6989 (9.64%), số phép quay bậc cao giảm 37 xuống 36. Điểm giảm 12.53%
so baseline, tương đương 1.1433 lần. Mức này vẫn thấp hơn dự đoán ban đầu
15–22%; không chỉnh lại dự đoán sau kết quả.

Sai số/dung sai trên dev của delta12 là 0.71875 tại x=1, cao hơn balanced
0.607265916966737. Tuy vậy rotation_eps tăng từ 1.2290081659190529e-12 lên
1.3009771637362466e-12: verifier dùng margin pha tuyệt đối nhỏ nhất trên các x,
không chỉ tỷ lệ sai số tương đối xấu nhất. Vì tol(x) phụ thuộc x nên hai đại
lượng không nhất thiết biến thiên cùng chiều; không coi eps tăng là mâu thuẫn.
Cùng 36 phép quay và 1 T cơ sở, phần chi phí synthesis không triệt tiêu lợi ích
108 Toffoli tiết kiệm. Mô hình toàn miền max ratio 0.9309830032 so balanced
0.9355210699; cả hai vẫn có margin toàn miền hẹp, không đồng nghĩa full PASS.

Hypothesis được ủng hộ trong phạm vi dev và mô hình: cùng widths delta12 nhưng
bias=0 có max ratio toàn miền 1.5035512019, bù bias đưa xuống dưới 0.95 mà không
đổi primitive số học hoặc lịch cấp phát. So với INV-3 pebble_square, điểm dev
của delta12 vẫn cao hơn 0.37%; ghép precision/bias với lịch cấp phát cần
Issue kết hợp riêng và chưa thực hiện.

Quyết định sau vòng này: chọn delta12 làm config dev tốt nhất và dừng chọn thêm
config trong lượt hiện tại. Người dùng hoãn full; không chạy hoặc yêu cầu full
như điều kiện hoàn thành bước phân tích này. Hai config đã có dev PASS, mô hình
exhaustive và kiểm tra simulation mẫu biên/random riêng. Chưa có verifier full
hoặc lượt chấm bổ sung với profile/seed độc lập cho ứng viên cuối; giới hạn này
được giữ rõ khi bàn giao. Không khẳng định đã tìm tối ưu. Issue giữ mở, chưa tạo
PR hoặc merge; bước chuẩn bị PR là giai đoạn tiếp theo nếu được giao. Khi cần
xác nhận full sau này, hệ số full cần đối chứng cùng môi trường, không dùng
baseline full Colab hiện tại để suy ra cải thiện tương thích.

### Các mốc tái lập được giữ lại

| Mốc | Config | Commit nguồn | Run / provenance |
| --- | --- | --- | --- |
| Dev tốt nhất | [delta12.json tại commit nguồn](https://github.com/nhphan0505/verifiable-quantum-circuit/blob/8d14de54075cf006040358a5bf91a1ef48adbb17/src/invsqrt/INV-6/configs/delta12.json) | `8d14de54075cf006040358a5bf91a1ef48adbb17` | [verifier.json](../../../results/invsqrt/INV-6/delta12/dev_5min/20261108T021502Z-local-dev_5min-b9ca90/verifier.json) / [provenance.json](../../../results/invsqrt/INV-6/delta12/dev_5min/20261108T021502Z-local-dev_5min-b9ca90/provenance.json) |
| Dev trước đó | [balanced.json tại commit nguồn](https://github.com/nhphan0505/verifiable-quantum-circuit/blob/f8083621416e45354f8c89015cd72bb39b7b2bd4/src/invsqrt/INV-6/configs/balanced.json) | `f8083621416e45354f8c89015cd72bb39b7b2bd4` | [verifier.json](../../../results/invsqrt/INV-6/balanced/dev_5min/20261108T015743Z-local-dev_5min-d222d7/verifier.json) / [provenance.json](../../../results/invsqrt/INV-6/balanced/dev_5min/20261108T015743Z-local-dev_5min-d222d7/provenance.json) |
| Full | Chưa chấm | Chưa có mốc full | Chưa chấm |

Mô hình và simulation balanced: [biên bản](../../../results/invsqrt/INV-6/balanced/build_only/20261108T014525Z-local-build/model_validation.json).
Mô hình và simulation delta12: [biên bản](../../../results/invsqrt/INV-6/delta12/build_only/20261108T020740Z-local-build/model_validation.json).
Tái lập dùng source/config đúng commit của từng dòng; không suy từ HEAD sau
các commit phân tích và không sửa run/provenance cũ theo mốc mới.

Kiểm tra tái lập: [validate_model.py](validate_model.py), chạy `python src/invsqrt/INV-6/validate_model.py --config src/invsqrt/INV-6/configs/delta12.json --sample-seed 20261109 --output artifacts/invsqrt/INV-6/delta12_model_validation.json`.

Mã: [solution.py](solution.py). Config: [delta12.json](configs/delta12.json) (dev tốt nhất), [balanced.json](configs/balanced.json) (mốc cũ).
Điểm: [SCORES.md](../SCORES.md).
