# 05 — Viết Python tái dựng

Đầu vào: bước 4 đạt. Được sửa source/config/data/mô tả/manifest của ID, commit/push
và đồng bộ Issue/draft PR; không sửa hạ tầng, verifier, SCORES hoặc run cũ.

1. Viết solution.py theo [mẫu](../../templates/solution.py), docstring giải thích
   biểu diễn, cách dựng, giả định, precision, compute/uncompute/sửa pha, giới hạn
   và lệnh chạy. Suy ra TRACK/ID từ vị trí; --config phải resolve trong configs
   của hướng; output theo stem config và cấu trúc artifacts chuẩn.
2. Ưu tiên bản dựng chính xác từng lệnh; có thể sinh KMX bằng Python rồi tạo
   km.Circuit. Sau đó gom hàm/vòng lặp/tham số có căn cứ. Không thay bằng các helper
   số học nếu chúng sinh chuỗi cổng khác, dù cùng chức năng. Không đổi cấp phát
   qubit, thứ tự register, điều kiện, góc hay metadata chỉ để code đẹp.
3. Không nhận nghiệm thu với wrapper đọc lại submission/KMX nguyên bản, base64
   nguyên binary hoặc script chép file. Code sinh chuỗi lệnh rõ ràng vẫn là mức
   tái dựng thấp; phải ghi chưa khôi phục thuật toán cấp cao. Dữ liệu bảng thật sự
   cần thiết được khai báo riêng; không ngụy trang toàn mạch thành bảng dữ liệu.
4. Task 3: khai báo nguồn các mảng NPZ; không mặc nhiên nhận đã khôi phục phương
   pháp sinh mảng. Muốn bytes container trùng phải xét NPY headers, thứ tự member,
   metadata ZIP, phương pháp/mức nén và phiên bản thư viện. Không sửa dữ liệu gốc.
5. reconstruction.json ghi schema_version, track, input hash/bytes, nguồn đã biết,
   manifest thành phần, environment, references, dependencies (path/hash/cách lấy),
   reconstruction_level và limitations. Dùng null/ghi chưa biết thay vì bịa.
   Đây là manifest bổ sung, không thay schema provenance; không ghi hash artifact
   tương lai hoặc tự tạo SHA commit nguồn trong manifest trước commit.
6. Config đầu tiên tên reconstructed; chỉ tham số có nghĩa và đủ tái lập. Bản
   dựng không phụ thuộc file gốc/scratch hoặc đường dẫn máy tác giả. Dữ liệu ngoài
   Git phải có hash và cách lấy thật; thiếu dữ liệu thì chưa gọi tái lập được.
7. Chạy kiểm tra source/config phù hợp, hoàn thiện mô tả rồi commit nguồn/config
   và dependency trước build bước 6. Không chạy solution đầy đủ trước commit để
   né mốc provenance; sau sửa source phải tạo mốc mới cho lần build mới.

Nghiệm thu: source có thể đọc/sửa, config và manifest đầy đủ, dependency rõ, commit
thật đã xác minh. Chưa tuyên bố exact hoặc verifier PASS.
