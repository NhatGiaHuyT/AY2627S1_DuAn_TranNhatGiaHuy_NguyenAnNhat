# AY2627S1_DuAn_TranNhatGiaHuy_NguyenAnNhat

Dự án CNTT HK1 năm 2025-2026.

## Hướng dẫn chạy code (hmp_gsa)

### Yêu cầu

- Python >= 3.9
- Chạy từ thư mục gốc dự án (chứa thư mục `hmp_gsa/`)

### Cài đặt

```powershell
pip install -e ./hmp_gsa
```

### Chạy thí nghiệm

Chỉnh sửa config trong `hmp_gsa/configs/` (ví dụ `baseline.json` hoặc `real_data_500.json`), sau đó chạy:

```powershell
python -m hmp_gsa.experiments.run --config hmp_gsa/configs/baseline.json
```

Kết quả được ghi vào `results/<timestamp>/` (file `runs.csv` và `summary.csv`).
