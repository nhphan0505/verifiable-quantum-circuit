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
Q không đổi như dự đoán. Chưa có điểm hoặc kết quả verifier cho delta12.
validate_model.py nhận --config và --sample-seed để tái lập từng cấu hình;
solution.py giữ nguyên, mapping/source commit của balanced không đổi.

## Kết luận và phiên bản tái lập

Balanced đạt dev_5min PASS trong run `20261108T015743Z-local-dev_5min-d222d7`, 4096 đầu vào x 2
lần đo (8192 shots), seed=20261106. Hash artifact, provenance build, source/config
commit, môi trường Python/package và toàn bộ hash verifier/dev harness khớp mốc
đối chứng; stdout JSON khớp verifier.json. [Phân tích đối chiếu](../../../results/invsqrt/INV-6/balanced/dev_5min/20261108T015743Z-local-dev_5min-d222d7/analysis.json).

Kết quả ủng hộ hypothesis: bù bias cho phép dùng bộ widths hẹp vốn không đủ dung
sai khi bias=0 trong mô hình toàn miền, và chi phí dev thực tế thấp hơn baseline.
Q giảm 260 xuống 251 (3.46%), Toffoli giảm 7735 xuống 7097 (8.25%), số phép quay
bậc cao giảm 37 xuống 36. Sai số/dung sai trên dev tăng từ
0.37839383360236045 lên 0.607265916966737 tại x=2588367; rotation_eps giảm từ
1.813003214175951e-12 xuống 1.2290081659190529e-12. Tổng chi phí quy đổi C vẫn
giảm từ 7986.319634297497 xuống 7344.360838891405, nên score giảm
11.22% (hệ số 1.1264 lần). Mức giảm thấp hơn dự đoán ban đầu 15–22%;
không coi đây là cấu hình tối ưu hoặc full PASS. So với INV-3 pebble_square đã
có trong bảng, INV-6 vẫn có điểm dev cao hơn khoảng 1.87%; ghép hai ý tưởng cần
Issue kết hợp riêng và chưa thực hiện trong hướng này.

Đề xuất dừng chọn config trên dev, kiểm tra full balanced trước khi xác nhận
ứng viên cuối. Vì baseline full hiện tại khác môi trường Colab, muốn ghi hệ số
full cần chấm đối chứng full với môi trường hiện tại; không dùng điểm dev làm
hệ số full. Issue giữ mở, chưa tạo PR hoặc merge.

Kiểm tra mô hình exhaustive toàn miền: baseline max ratio 0.476911612;
cùng widths giảm nhưng bias=0 là 1.258254701 (không đủ dung sai);
balanced là 0.935521070 tại x=3103229, khoảng sai số có dấu
[-0.873052085, 0.935521070], không overflow. Các giá trị dùng float64 để
ước lượng sai số, không thay cho so pha uint64 chính xác của verifier.
Mô phỏng compute_only và mạch pha trên 374 đầu vào (biên và random seed
20261108), với measurement seeds 17, 982451653, 20261108, khớp từng bit đầu
ra mô hình, pha bằng mô hình, khôi phục x và toàn bộ scratch=0.
Tài nguyên tĩnh đo trong kiểm tra local: Q=251 và Toffoli=7097, so baseline
Q=260 và Toffoli=7735. Giảm 9 qubit và 638 Toffoli, thấp hơn dự đoán ban đầu;
không sửa lại dự đoán sau khi đo. Chi phí rotation synthesis thực tế đã được
tính trong kết quả dev ở trên. Margin mô hình chỉ còn khoảng 6.45% ở điểm
xấu nhất toàn miền; cần kiểm tra full trước khi khẳng định chất lượng.
Kiểm tra mô hình và simulation local được ghi riêng; SCORES chỉ ghi dev PASS,
full để trống. Mốc nguồn build: `f8083621416e45354f8c89015cd72bb39b7b2bd4`.
[Provenance build_only](../../../results/invsqrt/INV-6/balanced/build_only/20261108T014525Z-local-build/provenance.json),
[báo cáo mô hình và simulation](../../../results/invsqrt/INV-6/balanced/build_only/20261108T014525Z-local-build/model_validation.json).
Artifact balanced đã BUILT và dev PASS; chưa chấm full. Tái lập dùng source/config tại
commit trên (`git show <commit>:src/invsqrt/INV-6/solution.py` và config cùng commit),
không suy ra phiên bản build từ HEAD sau các commit phân tích.

| Mốc tốt nhất | Config | Commit nguồn | Run / provenance |
| --- | --- | --- | --- |
| Dev | [balanced.json tại commit nguồn](https://github.com/nhphan0505/verifiable-quantum-circuit/blob/f8083621416e45354f8c89015cd72bb39b7b2bd4/src/invsqrt/INV-6/configs/balanced.json) | `f8083621416e45354f8c89015cd72bb39b7b2bd4` | [verifier.json](../../../results/invsqrt/INV-6/balanced/dev_5min/20261108T015743Z-local-dev_5min-d222d7/verifier.json) / [provenance.json](../../../results/invsqrt/INV-6/balanced/dev_5min/20261108T015743Z-local-dev_5min-d222d7/provenance.json) |
| Full | Chưa chấm | Chưa có mốc full | Chưa chấm |

Kiểm tra tái lập: [validate_model.py](validate_model.py), chạy `python src/invsqrt/INV-6/validate_model.py --output artifacts/invsqrt/INV-6/model_validation.json`.

Mã: [solution.py](solution.py). Config: [balanced.json](configs/balanced.json).
Điểm: [SCORES.md](../SCORES.md).
