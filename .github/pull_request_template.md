<!-- PR thử nghiệm dùng mẫu bên dưới. PR đọc paper/discussion dùng
templates/research/pull_request.md; không yêu cầu compile hoặc điểm cho tài liệu. -->

## Experiment và vấn đề

Closes #...
ID / owner:
Mô tả chuẩn: src/<bài>/<ID>/DESCRIPTION.md
Giả thuyết và thay đổi so với nguồn kế thừa:

## Kết quả

Commit source/config dùng để dựng artifact:
Commit kết quả/phân tích:
Link run JSON, config và provenance.json:
Score, baseline so sánh, verification level:
Tiêu chí ủng hộ/bác bỏ và điều kiện dừng đã đặt trước khi thử:
Config/run tốt nhất của từng mode và SHA nguồn tương ứng:
Kiểm tra độc lập hoặc full cho ứng viên cuối (hoặc giới hạn chưa kiểm tra):
Kết luận (kể cả không cải thiện):

## Kiểm tra

- [ ] Đã nhận Issue và kiểm tra hướng trùng
- [ ] File Python có solution docstring chi tiết
- [ ] Source/config đã commit trước build/chấm; provenance.json ghi đúng SHA nguồn và hash artifact
- [ ] Đã commit kết quả/phân tích sau chấm; có lệnh chạy và thông tin môi trường
- [ ] EXPERIMENTS.md có ID/title/link Issue/link mô tả; <ID>/DESCRIPTION.md đã đồng bộ với Issue
- [ ] Ghi full/dev_5min PASS vào SCORES.md với chế độ/profile rõ ràng
- [ ] Không thay đổi verifier gốc hoặc đưa artifact lớn vào Git

Giới hạn / phần chưa kiểm tra:
