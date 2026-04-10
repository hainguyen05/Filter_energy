import math
from typing import List, Dict

class EnergyFilter:
    def __init__(self, allowed_angle_deviation: float = 10.0, is_timestamp_ms: bool = True):   # sai số góc là 10 độ
        self.allowed_angle_deviation = allowed_angle_deviation
        self.is_timestamp_ms = is_timestamp_ms

    def is_valid(self, energy_history: List[Dict], power_history: List[Dict], new_energy: Dict, new_power: Dict) -> bool:
        if not energy_history or not power_history:
            return True
        
        # Lấy điểm cuối cùng của list để so sánh với datapoint mới
        last_energy = energy_history[-1]
        last_power = power_history[-1]

        t_start = last_energy['timestamp']
        e_start = last_energy['value']
        p_start = last_power['value']

        t_end = new_energy['timestamp']
        e_end = new_energy['value']
        p_end = new_power['value']

        dt_raw = t_end - t_start

        if self.is_timestamp_ms:
            dt_min = dt_raw / 1000.0 / 60.0 
        else:
            dt_min = dt_raw / 60.0           

        if dt_min <= 0:
            return False

        de_actual = e_end - e_start

        avg_power = (p_start + p_end) / 2.0
        ideal_slope = avg_power / 60.0 

        scale_y = ideal_slope if ideal_slope > 0 else 1.0

        actual_slope_scaled = (de_actual / dt_min) / scale_y
        actual_angle = math.degrees(math.atan(actual_slope_scaled))

        ideal_angle = 45.0 if ideal_slope > 0 else 0.0

        angle_diff = abs(actual_angle - ideal_angle)
        
        return angle_diff <= self.allowed_angle_deviation