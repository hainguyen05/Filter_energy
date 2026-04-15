from typing import Dict, Optional, List, Tuple

class EnergyFilter:
    def __init__(self, allowed_energy_deviation_wh: float = 1.0, allowed_energy_deviation_ratio: float = 0.3, window_size: int = 5):
        self.allowed_energy_deviation_wh = allowed_energy_deviation_wh
        self.allowed_energy_deviation_ratio = allowed_energy_deviation_ratio
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
        return self.history[-1][0]['value']

    def get_baseline_power(self) -> float:
        if not self.has_baseline():
            return 0.0
        return self.history[-1][1]['value']

    def estimate_efficiency(self) -> float:
        if len(self.history) < 2:
            return 1.0

        prev_energy, prev_power = self.history[-2]
        last_energy, last_power = self.history[-1]
        delta_t_ms = last_energy['timestamp'] - prev_energy['timestamp']
        if delta_t_ms <= 0:
            return 1.0

        delta_t_hours = delta_t_ms / 3600000.0
        avg_power = (prev_power['value'] + last_power['value']) / 2.0
        if avg_power <= 0 or delta_t_hours <= 0:
            return 1.0

        energy_delta = last_energy['value'] - prev_energy['value']
        if energy_delta <= 0:
            return 1.0

        return energy_delta / (avg_power * delta_t_hours)

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
        baseline_power = self.get_baseline_power()

        if new_energy['value'] < baseline_energy:
            return False
        if new_power['value'] < 0:
            return False

        delta_t_ms = new_energy['timestamp'] - baseline_timestamp
        if delta_t_ms <= 0:
            return False

        delta_t_hours = delta_t_ms / 3600000.0
        avg_power = (baseline_power + new_power['value']) / 2.0
        actual_delta_energy = new_energy['value'] - baseline_energy

        if len(self.history) < 2:
            return actual_delta_energy >= 0

        if actual_delta_energy < 0:
            return False

        efficiency = self.estimate_efficiency()
        expected_delta_energy = efficiency * avg_power * delta_t_hours
        tolerance = max(
            self.allowed_energy_deviation_wh,
            abs(expected_delta_energy) * self.allowed_energy_deviation_ratio,
        )

        if actual_delta_energy > expected_delta_energy + tolerance:
            return False

        return True

    def accept(self, new_energy: Dict, new_power: Dict) -> bool:
        valid = self.is_valid(new_energy, new_power)
        if valid:
            self.set_baseline(new_energy, new_power)
        return valid
