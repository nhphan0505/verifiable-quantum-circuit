# Kết quả từng lần chạy

Đường dẫn: `<TRACK>/<EXPERIMENT_ID>/<CONFIG_NAME>/<MODE>/<run_id>/`.

- config.json: tham số chấm thực tế; JSON dựng mạch nằm tại src/<TRACK>/<ID>/configs/<config-name>.json.
- metadata.json: ID, tên config, người chạy, phiên bản môi trường, lệnh và hash mạch/verifier.
- verifier.json: JSON gốc của verifier, không sửa điểm/trạng thái.
- verify.stdout.txt, verify.stderr.txt: output gốc; review.json và launch.json nếu có.

Tên config lấy từ artifact upload; run-id là thời gian UTC kèm hậu tố duy nhất. Thư mục mode gồm smoke/dev_5min/full; build_only dành cho record dựng mạch không có điểm chấm.

Dev lưu cả profile/seed/profile_version/input_sha256 (invsqrt). Chỉ so cùng cấu hình. Ghi dev/full PASS vào cột tương ứng trong SCORES.md. TIMEOUT không có điểm và không kết luận mạch sai.

Các run lịch sử đã chuyển sang config baseline và đúng mode. Nội dung JSON/log giữ nguyên để bảo toàn bằng chứng; đường dẫn bên trong chúng có thể phản ánh cấu trúc lúc chạy. results/setup/structure_migration.json lưu ánh xạ đường dẫn cũ → mới. Không dùng đường dẫn lịch sử để suy ra file hiện tại.

results/setup/ lưu biên bản setup/migration, không phải các experiment được chấm.

Notebook mới ghi `metadata.json → upload_artifact.sha256` là hash file upload gốc (KMB hoặc ZIP), dùng để nối với build_only. `submission_sha256` vẫn là hash các thành phần sau giải nén. Run cũ thiếu trường mới được giữ nguyên; không tự bổ sung hash ZIP nếu không còn bằng chứng.

Run mới dùng [schema provenance](../templates/run/provenance.json) theo [hướng dẫn check](../docs/REPOSITORY_CHECKS.md).
