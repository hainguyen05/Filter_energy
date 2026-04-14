# Hệ thống lọc dữ liệu sạc cho trạm sạc tàu

Dự án này triển khai hệ thống quản lý và lọc dữ liệu năng lượng/công suất cho phiên sạc của tàu tại trạm sạc.

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

### Tại sao chọn phương pháp này?
- **Đơn giản và hiệu quả**: Không cần lưu toàn bộ lịch sử, chỉ cần baseline hiện tại.
- **Phù hợp với luồng thời gian thực**: Dễ triển khai trên thiết bị edge với tài nguyên hạn chế.
- **Tự động thích ứng**: Baseline cập nhật theo dữ liệu thực tế, không cần cấu hình cố định.

### Quy tắc lọc chi tiết
Trong `EnergyFilter.is_valid()`:

1. **Kiểm tra năng lượng**:
   - Năng lượng phải tăng hoặc giữ nguyên so với baseline.
   - Lý do: Trong quá trình sạc, năng lượng tích lũy không thể giảm (trừ khi có lỗi sensor).

2. **Kiểm tra công suất**:
   - Công suất phải >= 0.
   - Lý do: Công suất âm có nghĩa là đang xả pin, không phải sạc.

### Ví dụ logic
Giả sử datapoint đầu tiên: Energy = 100 Wh, Power = 50 W → Hợp lệ, baseline = (100, 50)

Datapoint tiếp theo: Energy = 105 Wh, Power = 45 W → Hợp lệ (energy tăng, power >=0), baseline = (105, 45)

Datapoint tiếp theo: Energy = 103 Wh, Power = 40 W → Không hợp lệ (energy giảm), giữ baseline cũ.

Datapoint tiếp theo: Energy = 108 Wh, Power = -10 W → Không hợp lệ (power âm), giữ baseline cũ.

### Ưu điểm
- **Chống nhiễu**: Lọc bỏ datapoint bất thường mà không ảnh hưởng baseline.
- **Tự phục hồi**: Khi có datapoint hợp lệ mới, baseline cập nhật.
- **Dễ debug**: Logic rõ ràng, dễ theo dõi qua log.

### Nhược điểm và mở rộng
- **Không phát hiện lỗi tích lũy**: Nếu nhiều điểm lỗi liên tiếp, baseline cũ có thể không còn hợp lệ.
- **Mở rộng tương lai**: Có thể thêm kiểm tra tốc độ thay đổi, hoặc sử dụng moving average cho baseline.

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

Chỉ in ra thông tin, không làm gì khác vì đây là định nghĩa class.

## Yêu cầu
- Python 3.6+
- matplotlib (cho test)

## Ghi chú
- Hệ thống sử dụng baseline tuần tự: mỗi datapoint hợp lệ trở thành baseline mới.
- Chỉ chấp nhận datapoint nếu năng lượng tăng hoặc bằng, công suất >= 0.

- `energy` là đại lượng tích lũy, tăng theo thời gian.
- `power` là công suất tức thời.
- Giữa hai thời điểm liên tiếp, nếu năng lượng thay đổi quá ít so với công suất trung bình thì điểm đó có thể bị coi là không khớp.
- Bộ lọc dùng phép so sánh góc giữa độ dốc thực tế và độ dốc lý tưởng để xác định tính ổn định.

## Khi nào cần sửa

- Nếu dữ liệu `timestamp` không phải `ms`, cần đặt `is_timestamp_ms=False`.
- Nếu muốn chấp nhận nhiều điểm hơn, tăng `allowed_angle_deviation`.
- Nếu muốn thêm kiểm tra theo tag hoặc measurement, có thể bổ sung vào hàm `is_valid`.

## Ví dụ sử dụng

```python
from filter import EnergyFilter

filter = EnergyFilter(allowed_angle_deviation=10.0, is_timestamp_ms=True)
valid = filter.is_valid(energy_history, power_history, new_energy, new_power)
```

Trong đó `energy_history` và `power_history` là danh sách các dict có cấu trúc giống như:

```python
{
    'timestamp': 1680000000000,
    'value': 3141952372.8343577,
}
```
