# mrmeows v3 — mạch mở, tối ưu tài nguyên và các hướng đã thử

Status: ready
Track: shared
Source: https://www.kaggle.com/code/mrmeows/qcc-14-50-everything-i-learned-open-circuits?scriptVersionId=362387953
Version: Kaggle v3 (scriptVersionId 362387953)

- mrmeows, truy cập 08/11/2026. Phạm vi gồm các ô Markdown và số liệu tác giả ghi trong đó. [Notebook v3](https://www.kaggle.com/code/mrmeows/qcc-14-50-everything-i-learned-open-circuits?scriptVersionId=362387953) · [Snapshot diễn giải](source.md)

## Câu hỏi và bối cảnh

Tác giả ghi lại các biến đổi giúp giảm chi phí ba bài và các hướng từng thử trên những mạch cụ thể. Markdown nêu điểm public 14,49721 và ba tỉ số đối chứng trên chi phí là 17,27 cho invsqrt, 27,41 cho DQI và 6,435 cho DFTHCSOS. Đây là số liệu tác giả ghi cho bản phát hành. [Notebook v3, mục Summary](https://www.kaggle.com/code/mrmeows/qcc-14-50-everything-i-learned-open-circuits?scriptVersionId=362387953)

## Các phương án và lập luận

| Bài | Biến đổi và số liệu do nguồn báo cáo | Điều kiện và giới hạn |
| --- | --- | --- |
| **Invsqrt** | Tính lại đầu ra QROM phụ thuộc ngay trước khi dùng. Dọn sớm tiền tố carry bằng đo X và hiệu chỉnh Clifford. Tạm xóa bit cao của accumulator, đổi buffer ở lượt pha thứ hai và cất bit vào dây đã giải phóng. Giữ đa thức và góc quay, giảm 78 xuống 68 qubit với lỗi xấu nhất bằng 0,99966 lần dung sai. [Notebook, mục invsqrt](https://www.kaggle.com/code/mrmeows/qcc-14-50-everything-i-learned-open-circuits?scriptVersionId=362387953) | Tác giả báo đối chiếu các đồng nhất thức trên toàn bộ 3.133.452 đầu vào hợp lệ. Mức 1.450–1.550 Toffoli tương đương là ước lượng cho kiến trúc cụ thể. Phương án 67 qubit với curvature block chung là kết quả được nhắc ngoài gói phát hành. |
| **DQI** | Dùng nguyên Gluzdov round12, với extraction continued fraction tại chỗ và giải pha Bézout/Hankel. Mạch được báo 881 qubit, trung bình 964.394 Toffoli. Tác giả dẫn một lần chấm của nhóm khác có hai lỗi pha trong 102.400 shot. [Notebook, mục DQI](https://www.kaggle.com/code/mrmeows/qcc-14-50-everything-i-learned-open-circuits?scriptVersionId=362387953) | Sweep biên độ không dùng nghịch đảo được báo khoảng 45.000 Toffoli ở giai đoạn pha. Tiền xử lý Bézoutian được báo 871 qubit và khoảng 73.000 Toffoli chiều thuận với bậc 35 và pivot đều. Các số này thuộc những cấu phần riêng. Trường hợp tụt bậc sâu và chi phí của mạch đầy đủ vẫn cần kiểm. |
| **DFTHCSOS** | Tập địa chỉ 0…875 đóng dưới phép lấy tập con bit, nên có thể biểu diễn bit output bằng XOR các tích bit địa chỉ. Loader bốn địa chỉ giảm thanh ghi góc giữ lâu. Chia miền và dùng chung tích giảm chi phí trên factorization cố định. Mức cải thiện tiếp theo đến từ fit word 8 bit, giảm tổng Q từ 742 xuống 448 với từ điển khoảng B = 300–350. Bản phát hành có R = 4, B = 303, C = 128 và 23.500 Toffoli. [Notebook, mục DFTHCSOS](https://www.kaggle.com/code/mrmeows/qcc-14-50-everything-i-learned-open-circuits?scriptVersionId=362387953) | Cần phân biệt đổi loader bảo toàn word với refit thay đổi word. Tác giả báo làm tròn fit 10 bit xuống 8 bit cho error₂ khoảng 111 mHa. Rời rạc hóa có ràng buộc, chuyển hệ số và tăng từ điển giúp lấy lại độ chính xác trong fit được thử. |

## Kết luận hiện tại

- **Đối chiếu repo.** DQI mặc định dùng 70 syndrome 12 bit, tương ứng 840 qubit đầu vào và 102.400 shot cho một lượt. Cận nhân GF(64) trong nhận xét về một hướng Forney thuộc riêng mô hình tác giả đang xét. Verifier DFTHCSOS kiểm riêng hai sai số tối đa 20 mHa, giúp xác định vì sao các bản làm tròn được nêu chưa đủ độ chính xác. [Verifier DQI](../../../../verifiers/dqi/verify_submission_dqi.py) · [Verifier DFTHCSOS](../../../../verifiers/dfthcsos/verify.py)
- **Đặc số 2.** Nếu σ(x) = E(x²) + x·O(x²), với E và O gom hệ số bậc chẵn và lẻ, thì đạo hàm hình thức σ′(x) = O(x²). Với σ bậc 35, O có bậc tối đa 17. Để áp dụng tiền xử lý mà tác giả mô tả, vẫn cần chứng minh các phép biến đổi Bézoutian, điều kiện pivot và xử lý bước tụt bậc cho mạch đích. [Notebook, mục DQI](https://www.kaggle.com/code/mrmeows/qcc-14-50-everything-i-learned-open-circuits?scriptVersionId=362387953)
- **Kết quả âm.** Newton, đoạn bậc ba và các độ rộng bảng invsqrt khác chưa cải thiện thiết kế được thử. Với DFTHCSOS, các bản 7 bit và một số shape có chi phí thấp hơn về lý thuyết vẫn vượt ngưỡng sai số sau lượng tử hóa. Cận cải thiện λ_eff dưới 0,3% được tác giả nêu cho phép xoay hoặc đẳng cự trên factorization cố định của họ. [Notebook, mục invsqrt và DFTHCSOS](https://www.kaggle.com/code/mrmeows/qcc-14-50-everything-i-learned-open-circuits?scriptVersionId=362387953)

## Hypothesis đề xuất và kiểm chứng tiếp

- **Invsqrt.** So một biến đổi liveness hay dọn carry riêng với mạch đã định phiên bản. Kiểm đồng nhất giá trị và pha trên toàn miền, sau đó so qubit đỉnh và chi phí cổng.
- **DQI.** Kiểm mô-đun Bézoutian trên các ca pivot đều và ca tụt bậc sâu. Đo riêng chiều thuận, chiều đảo và workspace trước khi đánh giá mạch đầy đủ.
- **DFTHCSOS.** Với loader, đối chiếu word hiệu dụng ở từng địa chỉ hợp lệ và điều kiện xóa workspace. Với fit word ngắn, dùng đối chứng làm tròn trực tiếp và so hai sai số, λ_eff, workspace cùng chi phí lookup.

## Liên kết và câu hỏi còn mở

- [Mốc invsqrt](../../../../src/invsqrt/SCORES.md) · [DQI](../../../../src/dqi/SCORES.md) · [DFTHCSOS](../../../../src/dfthcsos/SCORES.md)
- Các số liệu và kiểm chứng của tác giả được trích từ Markdown. Chưa chạy lại notebook hoặc đối chiếu artifact. Phần code, output của cell code và tab bình luận nằm ngoài snapshot.
