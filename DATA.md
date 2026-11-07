# Dữ liệu và binary local

Các file có sẵn trên máy vẫn được giữ nguyên. .gitignore chỉ ngăn thêm chúng vào Git về sau.
Sau khi clone, lấy đúng bộ dữ liệu ban tổ chức và đặt lại đúng đường dẫn:

- kickmix/kickmix.so
- sample_submission/invsqrt.kmb
- sample_submission/dqi.kmb (khoảng 886 MB)
- sample_submission/dfthcsos/submission.npz và angle_k_*.kmb
- verifiers/dfthcsos/FeMoCo76o113e.fcidump
- verifiers/dfthcsos/FeMoCo76o113e.fixed_shifts.npz
- verifiable_circuit_compilation.pdf (tài liệu tham khảo)

Repo giữ mã verifier và các LICENSE.txt. Manifest SHA-256 bộ gốc nằm tại data_manifest.json;
đối chiếu hash trước khi so sánh điểm giữa các máy. Chưa cấu hình tải dữ liệu tự động hoặc Git LFS.

Chấm trực tiếp artifact bằng [notebook local](docs/LOCAL_GRADING.md); không cần đóng gói ZIP verifier.
