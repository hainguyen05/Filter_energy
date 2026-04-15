from typing import Dict, Optional, List, Tuple
import math

class EnergyFilter:
    def __init__(self, allowed_angle_deviation: float = 10.0, use_moving_average: bool = False, window_size: int = 5):
        self.allowed_angle_deviation = allowed_angle_deviation
        self.use_moving_average = use_moving_average
        self.window_size = window_size
        self.history: List[Tuple[Dict, Dict]] = [] 

    def set_baseline(self, energy_point: Dict, power_point: Dict) -> None:
        self.history.append((energy_point, power_point))
        if len(self.history) > self.window_size:
            self.history.pop(0)

    def has_baseline(self) -> bool:
        return len(self.history) > 0

    def get_baseline_energy(self) -> float:
        if not self.has_baseline():
            return 0.0
        if self.use_moving_average and len(self.history) >= 2:
            energies = [e['value'] for e, _ in self.history]
            return sum(energies) / len(energies)
        else:
            return self.history[-1][0]['value']

    def get_baseline_timestamp(self) -> int:
        if not self.has_baseline():
            return 0
        return self.history[-1][0]['timestamp']

    def is_valid(self, new_energy: Dict, new_power: Dict) -> bool:
        """Validate new energy datapoint against current baseline."""
        if not self.has_baseline():
            return True

        baseline_energy = self.get_baseline_energy()
        baseline_timestamp = self.get_baseline_timestamp()

        if new_energy['value'] < baseline_energy:
            return False
        if new_power['value'] < 0:
            return False

        if len(self.history) < 2:
            return True  

        delta_t_ms = new_energy['timestamp'] - baseline_timestamp
        if delta_t_ms <= 0:
            return False

        delta_t_hours = delta_t_ms / 3600000.0  

        recent_powers = [p['value'] for _, p in self.history[-min(5, len(self.history))::]]
        avg_power = sum(recent_powers) / len(recent_powers)

        expected_delta_energy = avg_power * delta_t_hours
        actual_delta_energy = new_energy['value'] - baseline_energy

        if expected_delta_energy <= 0:
            return actual_delta_energy >= 0  

        ideal_slope = expected_delta_energy / delta_t_ms
        actual_slope = actual_delta_energy / delta_t_ms

        if ideal_slope == 0:
            angle_deviation = 90.0 if actual_slope != 0 else 0.0
        else:
            angle_radians = math.atan2(actual_slope, ideal_slope)
            angle_deviation = abs(math.degrees(angle_radians))

        return angle_deviation <= self.allowed_angle_deviation

    def accept(self, new_energy: Dict, new_power: Dict) -> bool:
        valid = self.is_valid(new_energy, new_power)
        if valid:
            self.set_baseline(new_energy, new_power)
        return valid
