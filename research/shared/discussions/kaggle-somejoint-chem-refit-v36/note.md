# SomeJoint v36: bỏ hiệu chỉnh pha và refit trọng số FeMoCo

Status: ready
Track: shared
Source: https://www.kaggle.com/code/somejoint/quantum-circuits-24-65-local-gm-chem-refit?scriptVersionId=365753941
Version: Kaggle v36 (scriptVersionId 365753941)

- **Nguồn.** Agniv Banerjee (SomeJoint), truy cập 08/11/2026. [Notebook v36](https://www.kaggle.com/code/somejoint/quantum-circuits-24-65-local-gm-chem-refit?scriptVersionId=365753941) · [Snapshot diễn giải](source.md)
- **Phạm vi.** Mô tả kỹ thuật, kết quả hiển thị và phản hồi liên quan. Phần cách chấm điểm, mã và hướng dẫn chạy notebook nằm ngoài phạm vi note.

## Câu hỏi và bối cảnh

SomeJoint ghép các thành phần công khai cho ba bài và thay đổi hai phần: loại các hiệu chỉnh pha thừa ở invsqrt và refit trọng số DFTHCSOS trên word góc đã có. Kaggle hiển thị 24,65393 cho v36. Tác giả báo kết quả local 24,65394. Các kết quả dưới đây giữ nguyên nguồn quy chiếu của từng thành phần. [Notebook v36, phần mở đầu](https://www.kaggle.com/code/somejoint/quantum-circuits-24-65-local-gm-chem-refit?scriptVersionId=365753941)

## Các phương án và lập luận

| Bài | Thay đổi và kết quả nguồn báo cáo | Điều kiện và giới hạn |
| --- | --- | --- |
| **Invsqrt** | Chuyển hai bit kết quả đo thành 0 theo ý tưởng của Kirill Tymchishin trên mạch v33. Tác giả báo giảm 0,5 Toffoli và 3 cổng T trung bình mỗi shot. Mạch 62 qubit, chi phí 97.921,58. Phần giảm bốn Toffoli thành hai ở accumulator đã nằm trong v33. qiuqiuh được ghi công vì công bố mức giảm ở cùng vị trí sớm hơn. [Notebook v36, mục invsqrt](https://www.kaggle.com/code/somejoint/quantum-circuits-24-65-local-gm-chem-refit?scriptVersionId=365753941) | Thay đổi chỉ hợp lệ nếu các dây được đo đã ở trạng thái 0 trên mọi nhánh hợp lệ và mọi phép dùng hai bit sau đó có thể bỏ mà vẫn bảo toàn pha. Tác giả báo đã replay 3.133.452 đầu vào với mọi kết quả đo và đạt bốn lượt verifier. Lỗi xấu nhất được báo bằng 0,99932 lần dung sai. |
| **DQI** | Dùng nguyên mạch 891 qubit của yoyobar từ lần viết lại thứ ba của decoder C1 của Syed Asad Ali, khoảng 396.918,5 Toffoli trung bình. Tác giả quy một CCZ tiết kiệm thêm cho yoyobar. Narrow return và flag carry thuộc các bước trước trong dòng thiết kế. [Notebook v36, mục DQI](https://www.kaggle.com/code/somejoint/quantum-circuits-24-65-local-gm-chem-refit?scriptVersionId=365753941) | Đây là số liệu của mạch được nhập. Một bình luận về việc thiếu phần lõi tái dựng nhắm vào decoder ở phiên bản cũ. Chưa xác minh khả năng dựng lại đúng mạch 891 qubit từ mô tả của notebook. |
| **DFTHCSOS** | Dùng 15 mạch nạp góc của qwertykeypadapple trên bảng (8, 143, 45) của Lera. Giữ word góc và chỉ refit hai mảng trọng số W và H2_I qua các bước tiếp tuyến có kiểm soát xen kẽ quét gauge. Sau năm lượt, tác giả báo λ_eff giảm từ 47,266713 xuống 47,184436, với 427 qubit, 15.347 Toffoli và chi phí 309.207.580. [Notebook v36, mục Chemistry](https://www.kaggle.com/code/somejoint/quantum-circuits-24-65-local-gm-chem-refit?scriptVersionId=365753941) | Hai sai số được báo là 11,195 và 19,999999 mHa, gap là 3,9148990 Ha. Dựa trên các chữ số hiển thị, sai số thứ hai cách ngưỡng khoảng 10⁻⁹ Ha và gap cao hơn sàn khoảng 10⁻⁶ Ha. Biên nhỏ khiến precision và môi trường tái lập đáng kiểm tra. |

## Kết luận hiện tại

- **Đối chiếu trong repo.** Verifier DFTHCSOS kiểm riêng hai sai số ở mức tối đa 0,020 Ha, gap phải lớn hơn 3,914898 Ha. Đây là điều kiện chấp nhận có thể đối chiếu từ mã verifier. Các giá trị sát ngưỡng trong bảng vẫn là số liệu nguồn báo cáo. [Verifier DFTHCSOS](../../../../verifiers/dfthcsos/verify.py)
- **Phản hồi và giới hạn.** Manwithacat gợi ý thử nhiều ngân sách tài nguyên và kiểm tương đương từng đoạn, chưa có phép đo bổ sung trong bình luận đó. Tobias Oberrauch nêu khó khăn khi tái dựng decoder cũ. SomeJoint nói phần thiếu có thể nằm trong notebook. Các hỏi đáp về ghi công và giấy phép cũng nhắm vào những phiên bản cũ hơn v36. [Bình luận trên Kaggle](https://www.kaggle.com/code/somejoint/quantum-circuits-24-65-local-gm-chem-refit/comments?scriptVersionId=365753941)

## Hypothesis đề xuất và kiểm chứng tiếp

- **Invsqrt.** Nếu một dây đã sạch trên mọi đầu vào và mọi nhánh liên quan, thử bỏ riêng hiệu chỉnh điều khiển bởi bit đo đó. So giá trị, pha và workspace với đối chứng trước khi ghi nhận tiết kiệm cổng.
- **DQI.** Cô lập phép giảm CCZ giữa hai lần viết lại liên tiếp của yoyobar. Kiểm tương đương trên đoạn được sửa, gồm pha và việc hoàn tác thanh ghi. Phép so cần hai mạch đúng phiên bản để tách thay đổi cục bộ khỏi khác biệt kiến trúc.
- **DFTHCSOS.** Giữ word góc và mạch cố định, so refit với trọng số đối chứng trong cùng môi trường. Kiểm hai sai số và gap bằng số chưa làm tròn trước khi kết luận rằng phần giảm λ_eff có thể tái lập với biên chấp nhận ổn định.

## Liên kết và câu hỏi còn mở

- [Mốc invsqrt trong repo](../../../../src/invsqrt/SCORES.md) · [DQI](../../../../src/dqi/SCORES.md) · [DFTHCSOS](../../../../src/dfthcsos/SCORES.md)
- Note ghi lại các kết quả được công bố, chưa tái chạy mạch, xác nhận phép replay hoặc xác minh số liệu local bằng artifact. Cần đúng phiên bản và số đo đầy đủ để dùng kết quả như mốc đối chứng định lượng.
