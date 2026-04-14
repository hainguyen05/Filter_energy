from typing import Dict, Optional

class EnergyFilter:
    def __init__(self):
        self.last_energy: Optional[Dict] = None
        self.last_power: Optional[Dict] = None

    def set_baseline(self, energy_point: Dict, power_point: Dict) -> None:
        self.last_energy = energy_point
        self.last_power = power_point

    def has_baseline(self) -> bool:
        return self.last_energy is not None and self.last_power is not None

    def is_valid(self, new_energy: Dict, new_power: Dict) -> bool:
        """Validate new energy datapoint against current baseline."""
        if not self.has_baseline():
            return True

        e_start = self.last_energy['value']
        e_end = new_energy['value']

        return e_end >= e_start

    def accept(self, new_energy: Dict, new_power: Dict) -> bool:
        valid = self.is_valid(new_energy, new_power)
        if valid:
            self.set_baseline(new_energy, new_power)
        return valid
