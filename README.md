## Cấu trúc file

### `filter.py`
Chứa class `EnergyFilter` - logic lọc dữ liệu datapoint năng lượng và công suất.

- **Chức năng**: Kiểm tra tính hợp lệ của datapoint dựa trên baseline (điểm đầu tiên của phiên sạc).
- **Quy tắc lọc**:
  - Năng lượng không được giảm so với baseline.
  - Công suất hiện tại không xét trực tiếp, vì dữ liệu thật có thể dao động do hệ thống điều khiển.
- **Sử dụng**: Được dùng bởi `ChargingSession` để xác thực datapoint.

### `main.py`
Chứa class `ChargingSession` - hệ thống quản lý phiên sạc.

- **Chức năng**: Quản lý toàn bộ phiên sạc, nhận từng datapoint và quyết định chấp nhận hay không.
- **Logic**: Điểm đầu tiên làm baseline, các điểm sau được lọc qua `EnergyFilter`.
- **Sử dụng**: File chính chạy khi bắt đầu phiên sạc tàu.

### `test.py`
Test harness để kiểm tra hệ thống với dữ liệu CSV.

- **Chức năng**: Đọc dữ liệu từ `query_energy.csv` và `query_power.csv`, ghép theo timestamp, chạy `ChargingSession`, và vẽ đồ thị kết quả.
- **Sử dụng**: Chỉ để test và visualize, không phải phần của hệ thống production.

## Ý tưởng phương pháp lọc

### Nguyên lý cơ bản
Hệ thống lọc dựa trên **baseline tuần tự** (sequential baseline validation). Ý tưởng chính là:

1. **Điểm đầu tiên làm mốc**: Khi tàu bắt đầu sạc, datapoint đầu tiên được coi là hợp lệ và dùng làm baseline (điểm chuẩn) cho toàn bộ phiên.

2. **So sánh tuần tự**: Mỗi datapoint mới được so sánh với baseline hiện tại (điểm cuối cùng hợp lệ).

3. **Cập nhật baseline**: Nếu datapoint hợp lệ, nó trở thành baseline mới cho các điểm tiếp theo.

### Quy tắc lọc chi tiết
Trong `EnergyFilter.is_valid()`:

1. **Kiểm tra năng lượng**:
   - Năng lượng phải tăng hoặc giữ nguyên so với baseline.
   - Lý do: Trong quá trình sạc, năng lượng tích lũy không thể giảm (trừ khi có lỗi sensor).

2. **Kiểm tra công suất**:
   - Công suất phải >= 0.
   - Lý do: Công suất âm có nghĩa là đang xả pin, không phải sạc.

3. **Kiểm tra tốc độ thay đổi (Rate of Change)**:
   - Tính độ dốc thực tế và độ dốc lý tưởng dựa trên công suất trung bình.
   - So sánh góc lệch giữa hai độ dốc, phải <= `allowed_angle_deviation` (độ).
   - Lý do: Phát hiện datapoint không khớp với mô hình sạc dự kiến.

4. **Moving Average Baseline** (tùy chọn):
   - Nếu `use_moving_average=True`, dùng trung bình động của `window_size` điểm gần nhất làm baseline.
   - Lý do: Làm mịn baseline, giảm ảnh hưởng của nhiễu ngắn hạn.

## Cách chạy

### Chạy test
```bash
python test.py
```

Cần có file `query_energy.csv` và `query_power.csv` trong thư mục cùng cấp.

### Chạy hệ thống (main.py)
```bash
python main.py
```

## Yêu cầu
- Python 3.6+
- matplotlib (cho test)