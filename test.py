import csv
import datetime
from pathlib import Path
import matplotlib.pyplot as plt
import argparse
from main import ChargingSession


def parse_csv(file_path: str):
    rows = []
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = [line for line in f if not line.startswith('#')]
        reader = csv.DictReader(lines)
        for row in reader:
            timestamp = datetime.datetime.fromisoformat(row['_time'].replace('Z', '+00:00'))
            timestamp_ms = int(timestamp.timestamp() * 1000)
            rows.append({
                'timestamp': timestamp_ms,
                'timestamp_dt': timestamp,
                'value': float(row['_value']),
            })
    return rows


def pair_energy_power(energy_data, power_data):
    energy_by_ts = {row['timestamp']: row for row in energy_data}
    power_by_ts = {row['timestamp']: row for row in power_data}
    common_timestamps = sorted(set(energy_by_ts) & set(power_by_ts))
    return [(energy_by_ts[ts], power_by_ts[ts]) for ts in common_timestamps]


def plot_session(session, paired_data):
    # Chuẩn bị dữ liệu cho đồ thị
    energy_times = [row['timestamp_dt'] for row, _ in paired_data]
    energy_values = [row['value'] for row, _ in paired_data]
    power_times = [row['timestamp_dt'] for _, row in paired_data]
    power_values = [row['value'] for _, row in paired_data]

    # Điểm hợp lệ
    valid_times = [row['timestamp_dt'] for row, _ in session.valid_points]
    valid_energy = [row['value'] for row, _ in session.valid_points]
    valid_power = [row['value'] for _, row in session.valid_points]

    # Điểm không hợp lệ
    invalid_times = [row['timestamp_dt'] for row, _ in session.invalid_points]
    invalid_energy = [row['value'] for row, _ in session.invalid_points]
    invalid_power = [row['value'] for _, row in session.invalid_points]

    # Tạo subplot
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 9), sharex=True)

    # Đồ thị năng lượng
    ax1.plot(energy_times, energy_values, label='Năng lượng', color='blue', linewidth=1)
    ax1.scatter(valid_times, valid_energy, color='green', label='Điểm hợp lệ', s=30, zorder=3)
    ax1.scatter(invalid_times, invalid_energy, color='red', label='Điểm không hợp lệ', s=60, marker='x', zorder=4)
    ax1.set_ylabel('Năng lượng (Wh)')
    ax1.set_title('Dữ liệu năng lượng với điểm hợp lệ/không hợp lệ')
    ax1.legend(loc='upper left')
    ax1.grid(True, alpha=0.3)

    # Đồ thị công suất
    ax2.plot(power_times, power_values, label='Công suất', color='orange', linewidth=1)
    ax2.scatter(valid_times, valid_power, color='green', label='Điểm hợp lệ', s=30, zorder=3)
    ax2.scatter(invalid_times, invalid_power, color='red', label='Điểm không hợp lệ', s=60, marker='x', zorder=4)
    ax2.set_ylabel('Công suất (W)')
    ax2.set_title('Dữ liệu công suất với điểm hợp lệ/không hợp lệ')
    ax2.legend(loc='upper left')
    ax2.grid(True, alpha=0.3)

    ax2.set_xlabel('Thời gian')
    fig.autofmt_xdate(rotation=25)
    plt.tight_layout()
    plt.show()


def main():
    parser = argparse.ArgumentParser(description='Test Energy Filter System')
    parser.add_argument('--angle-deviation', type=float, default=10.0, help='Allowed angle deviation in degrees (default: 10.0)')
    parser.add_argument('--moving-average', action='store_true', help='Use moving average for baseline')
    parser.add_argument('--window-size', type=int, default=5, help='Window size for moving average (default: 5)')

    args = parser.parse_args()

    energy_file = Path('query_energy.csv')
    power_file = Path('query_power.csv')
    if not energy_file.exists() or not power_file.exists():
        print('Thiếu file query_energy.csv hoặc query_power.csv trong thư mục hiện tại.')
        return

    energy_data = parse_csv(energy_file)
    power_data = parse_csv(power_file)
    paired_data = pair_energy_power(energy_data, power_data)

    if not paired_data:
        print('Không tìm thấy timestamp chung giữa file năng lượng và công suất.')
        return

    session = ChargingSession(allowed_angle_deviation=args.angle_deviation, use_moving_average=args.moving_average, window_size=args.window_size)
    for energy_point, power_point in paired_data:
        session.process_datapoint(energy_point, power_point)

    summary = session.get_summary()
    print('Tóm tắt phiên sạc:')
    print(f"Tổng số điểm: {summary['total']}")
    print(f"Điểm hợp lệ: {summary['valid']}")
    print(f"Điểm không hợp lệ: {summary['invalid']}")
    print(f"Settings: angle_deviation={args.angle_deviation}, moving_average={args.moving_average}, window_size={args.window_size}")

    plot_session(session, paired_data)


if __name__ == '__main__':
    main()


if __name__ == '__main__':
    main()
