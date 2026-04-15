import sys
import datetime
from typing import Dict, List
import matplotlib.pyplot as plt
from main import ChargingSession

# Test cases với dữ liệu giả để kiểm tra bộ lọc
def create_test_data():
    def make_case(minutes: int, energy: float, power: float, expected: bool, description: str):
        timestamp = minutes * 60000
        return {
            "energy": {"timestamp": timestamp, "value": energy},
            "power": {"timestamp": timestamp, "value": power},
            "expected": expected,
            "description": description,
        }

    test_cases = [
        make_case(0, 100.000, 50.0, True, "Baseline point"),
        make_case(10, 108.333, 50.0, True, "Valid constant power 50W"),
        make_case(20, 116.667, 50.0, True, "Valid constant power 50W"),
        make_case(30, 125.000, 50.0, True, "Valid constant power 50W"),
        make_case(40, 133.333, 50.0, True, "Valid constant power 50W"),
        make_case(50, 141.667, 50.0, True, "Valid constant power 50W"),

        make_case(60, 154.167, 100.0, True, "Valid step to 100W"),
        make_case(70, 170.833, 100.0, True, "Valid constant power 100W"),
        make_case(80, 187.500, 100.0, True, "Valid constant power 100W"),
        make_case(90, 204.167, 100.0, True, "Valid constant power 100W"),

        make_case(100, 200.000, 50.0, False, "Invalid: energy too low for 50W"),
        make_case(110, 237.500, 100.0, True, "Valid: jump back to 100W from last valid baseline"),
        make_case(120, 253.333, 100.0, True, "Valid: continue 100W"),
    ]

    # Thêm timestamp_dt cho plotting
    for case in test_cases:
        case["energy"]["timestamp_dt"] = datetime.datetime.fromtimestamp(case["energy"]["timestamp"] / 1000)
        case["power"]["timestamp_dt"] = datetime.datetime.fromtimestamp(case["power"]["timestamp"] / 1000)

    return test_cases

def plot_session(session, test_data):
    # Chuẩn bị dữ liệu cho đồ thị
    energy_times = [case["energy"]["timestamp_dt"] for case in test_data]
    energy_values = [case["energy"]["value"] for case in test_data]
    power_times = [case["power"]["timestamp_dt"] for case in test_data]
    power_values = [case["power"]["value"] for case in test_data]

    # Điểm hợp lệ
    valid_energy = [row['value'] for row, _ in session.valid_points]
    valid_power = [row['value'] for _, row in session.valid_points]
    valid_times = [datetime.datetime.fromtimestamp(row['timestamp'] / 1000) for row, _ in session.valid_points]

    # Điểm không hợp lệ
    invalid_energy = [row['value'] for row, _ in session.invalid_points]
    invalid_power = [row['value'] for _, row in session.invalid_points]
    invalid_times = [datetime.datetime.fromtimestamp(row['timestamp'] / 1000) for row, _ in session.invalid_points]

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

def run_tests():
    test_data = create_test_data()
    session = ChargingSession(allowed_energy_deviation_wh=1.0, window_size=5)

    passed = 0
    failed = 0

    print("Chạy test case cho bộ lọc năng lượng:")
    print("=" * 50)

    for i, case in enumerate(test_data, 1):
        energy = case["energy"]
        power = case["power"]
        expected = case["expected"]
        desc = case["description"]

        result = session.process_datapoint(energy, power)
        status = "PASS" if result == expected else "FAIL"

        if result == expected:
            passed += 1
        else:
            failed += 1

        print(f"Test {i}: {desc}")
        print(f"  Energy: {energy['value']} Wh at {energy['timestamp']}ms")
        print(f"  Power: {power['value']} W at {power['timestamp']}ms")
        print(f"  Expected: {'Valid' if expected else 'Invalid'}, Got: {'Valid' if result else 'Invalid'} -> {status}")
        print()

    summary = session.get_summary()
    print("Tóm tắt phiên test:")
    print(f"Tổng số điểm: {summary['total']}")
    print(f"Điểm hợp lệ: {summary['valid']}")
    print(f"Điểm không hợp lệ: {summary['invalid']}")
    print(f"Test passed: {passed}, Failed: {failed}")

    if failed == 0:
        print("Tất cả test case đều pass! Bộ lọc hoạt động hiệu quả.")
    else:
        print("Một số test case fail. Cần kiểm tra lại logic bộ lọc.")

    # Hiển thị đồ thị
    plot_session(session, test_data)

if __name__ == "__main__":
    run_tests()