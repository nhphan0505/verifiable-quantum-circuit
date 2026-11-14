# 05 — Chấm kiểm chứng riêng PP, không lưu kết quả mới

Áp dụng [workflow PP](README.md). Đầu vào: commit PP đã xác minh, tests đạt,
mạch cũ và kế hoạch kiểm chứng. Bước này cho phép agent chạy chấm local;
không phải bước bàn giao chấm và lưu results của luồng experiments.

## Thực hiện

1. Xác minh phiên bản code PP khớp commit; nguồn/hash mạch gốc và bằng chứng
   chưa qua PP khác. Nếu không xác minh được thì chọn đầu vào khác hoặc báo
   thiếu dữ kiện, không dùng mạch đó như đối chứng không PP.
2. Đọc [LOCAL_GRADING](../../docs/LOCAL_GRADING.md) và kiểm tra cách gọi engine
   hiện hành trước khi chạy: kickmix-engine 0.6.0, smoke/full; Windows dùng WSL
   với môi trường engine Linux. Không fallback sang engine cũ hoặc chạy mode
   dev_5min mới. Dùng chế độ không lưu hoặc
   chuyển mọi output sang thư mục tạm riêng. Không dùng đường chạy notebook/
   wrapper tự ghi results, SCORES hoặc metadata experiment. Không sửa verifier
   để đáp ứng điều này; nếu chưa có cách chạy phù hợp thì báo blocker.
3. Chạy đối chứng và ứng viên trên cùng bytes đầu vào, cùng profile, seed và
   số mẫu khi có. Ứng viên chỉ chạy PP đang thử; không xếp chuỗi với PP khác.
   Kết quả cũ chỉ dùng tham khảo nếu điều kiện chấm không tương thích.
4. Kiểm tra artifact hợp lệ, chấm bằng engine hiện hành theo điều kiện bài và
   giữ nguyên verifier gốc, đo tài nguyên trước/sau theo công thức của bài.
   Phân biệt smoke/full, FAIL/TIMEOUT và PASS thật;
   giảm qubit/Toffoli không đủ nghiệm thu tính đúng.
5. So với tiêu chí dự đoán; thử trong giới hạn đã ghi. Dùng mẫu/mạch chưa dùng
   tinh chỉnh cho kiểm tra bổ sung nếu đã có trong kế hoạch; không tuyên bố
   tương đương tổng quát chỉ vì verifier kiểm tra mẫu đạt.
6. Báo trong chat lệnh/profile, commit/hash, tham số, kết quả verifier và số đo
   trước/sau. Chỉ dùng artifact/log tạm trong lần kiểm tra; không lưu config,
   run, results, provenance JSON hoặc bảng điểm mới. Dọn đúng dữ liệu tạm do
   mình tạo sau khi đã đọc kết quả và xác minh đường dẫn an toàn.

Không sửa file experiment, dựng lại đè artifact cũ, hoặc tự mở lại Issue của
experiment nguồn. Nếu mạch thiếu, báo giới hạn hoặc dùng mạch sẵn có khác;
không tự chạy lại workflow experiment để bổ sung đầu vào.

## Nghiệm thu

- [ ] Đã chấm thật và quan sát output; báo đúng mức bằng chứng, kể cả không cải thiện.
- [ ] Chỉ PP đang thử được bật, đối chứng tương thích và đầu vào gốc bất biến.
- [ ] Không có file mới/thay đổi trong experiment, artifacts/results hay bảng điểm.
- [ ] Nêu kết luận và giới hạn; không coi dữ liệu tạm đã xóa là run lưu lâu dài.
