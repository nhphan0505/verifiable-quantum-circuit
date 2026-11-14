# Dependency runtime

Cài requirements.txt của repo vào .venv Windows Python 3.13. Chỉ cần source trong repo: solution.py, circuit.py, tables.json và configs/reconstructed.json. Không cần tải bundle tác giả, thư mục engine, Linux .so hoặc verifier để compile.

```powershell
.venv/Scripts/python.exe src/invsqrt/INV-51/solution.py --config src/invsqrt/INV-51/configs/reconstructed.json
```

Output: artifacts/invsqrt/INV-51/reconstructed.kmb. Lưu bản output cũ trước khi chạy lại; không tự ghi đè. engine_manifest.json kiểm tra source/data. LICENSE.txt và NOTICE.txt giữ attribution Apache-2.0. Chi tiết refactor ở INTEGRATION.md; nguồn lineage công khai ở DESCRIPTION.md.

## Tách postprocessing (Issue #62)

Các implementation hậu xử lý đã được chuyển nguyên thuật toán sang
[PP-001](../postprocessing/PP-001/DESCRIPTION.md) (giữ tích),
[PP-002](../postprocessing/PP-002/DESCRIPTION.md) (rewrite affine),
[PP-003](../postprocessing/PP-003/DESCRIPTION.md) (gộp Z_POW) và
[PP-004](../postprocessing/PP-004/DESCRIPTION.md) (relocate CS).
Các đoạn nói ba file runtime phía trên mô tả bản trước khi tách: hiện cần thêm
bốn solution.py của PP. circuit.py giữ simulator/backend và adapter nạp PP;
engine_manifest.json khóa cả source PP, check_committed kiểm tra snapshot Git
của dependency mới. Không dùng bản sao implementation cũ làm fallback.
Thứ tự pipeline, tham số và target hash không thay đổi. Records lịch sử vẫn
tham chiếu đúng source cũ; không suy ra verifier PASS mới từ việc di chuyển.
