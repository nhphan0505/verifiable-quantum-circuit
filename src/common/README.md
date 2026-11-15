# Hạ tầng chấm dùng chung

`local_grade.py` chấm smoke/full bằng kickmix-engine; `engine_runtime.py` chọn native
Linux/macOS hoặc WSL trên Windows. Xem [hướng dẫn](../../docs/LOCAL_GRADING.md).
Giữ kickmix để compile và làm dependency import của verifier chính thức.

`package_submission.py` là tiện ích đóng gói DFTHC dùng chung, không compile,
refit hay chấm điểm. Xem [hướng dẫn track](../dfthcsos/README.md#tách-compile-tối-ưu-và-đóng-gói).
