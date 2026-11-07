# Nguồn baseline

- `invsqrt/INV-BASELINE/solution.py` kế thừa `verifiers/invsqrt/nr_reference_circuit.py`.
- `dqi/DQI-BASELINE/solution.py` kế thừa `verifiers/dqi/dqi_reference_circuit.py`.
- `dfthcsos/DFT-BASELINE/solution.py` kế thừa `verifiers/dfthcsos/example_submission/angle_k_reference_circuit.py`.

Các hàm dựng mạch giữ nguyên thuật toán. Phần main được thay để đọc `--config`, xuất artifact theo tên config, kiểm soát ghi đè và đóng gói ZIP DFTHC. DFTHC chỉnh đường dẫn import theo vị trí mới.
Giữ tài liệu thuật toán gốc trong source. Giấy phép Apache-2.0 tại LICENSE.txt; hash file gốc tại ../data_manifest.json.
