from typing import Dict, List, Optional
from filter import EnergyFilter

DataPoint = Dict[str, float]

class ChargingSession:
    def __init__(self, energy_filter: Optional[EnergyFilter] = None, allowed_energy_deviation_wh: float = 1.0, allowed_energy_deviation_ratio: float = 0.3, window_size: int = 5):
        if energy_filter is None:
            energy_filter = EnergyFilter(
                allowed_energy_deviation_wh=allowed_energy_deviation_wh,
                allowed_energy_deviation_ratio=allowed_energy_deviation_ratio,
                window_size=window_size,
            )
        self.filter = energy_filter
        self.valid_points: List[tuple] = []
        self.invalid_points: List[tuple] = []
        self.started = False

    def process_datapoint(self, energy_point: DataPoint, power_point: DataPoint) -> bool:
        if not self.started:
            self.filter.set_baseline(energy_point, power_point)
            self.valid_points.append((energy_point, power_point))
            self.started = True
            return True
        
        valid = self.filter.accept(energy_point, power_point)
        if valid:
            self.valid_points.append((energy_point, power_point))
        else:
            self.invalid_points.append((energy_point, power_point))
        return valid

    def get_summary(self) -> Dict[str, int]:
        return {
            'total': len(self.valid_points) + len(self.invalid_points),
            'valid': len(self.valid_points),
            'invalid': len(self.invalid_points),
        }


if __name__ == '__main__':
    pass
