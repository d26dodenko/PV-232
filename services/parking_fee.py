from math import ceil

class ParkingFeeService:
    def __init__(
        self,
        free_minutes=30,
        hourly_rate=100,
        daily_cap=1000,
        resident_coefficient=0.7,
        max_minutes=1440,
    ):
        self.free_minutes = free_minutes
        self.hourly_rate = hourly_rate
        self.daily_cap = daily_cap
        self.resident_coefficient = resident_coefficient
        self.max_minutes = max_minutes

    def _validate(self, minutes: int) -> None:
        if minutes < 0:
            raise ValueError("Minutes must be >= 0")
        if minutes > self.max_minutes:
            raise ValueError(f"Minutes must be <= {self.max_minutes}")

    def _billable_hours(self, minutes: int) -> int:
        return ceil(minutes / 60)

    def _apply_cap(self, cost: float) -> float:
        return min(cost, self.daily_cap)

    def _apply_discount(self, fee: float, is_resident: bool) -> float:
        if is_resident:
            return fee * self.resident_coefficient

        return fee

    def _is_free(self, minutes: int) -> bool:
        return minutes <= self.free_minutes

    def calculate_fee(self, minutes: int, is_resident: bool = False) -> float:
        self._validate(minutes)

        if self._is_free(minutes):
            return 0.0

        default_fee = self._apply_cap(self._billable_hours(minutes) * self.hourly_rate)
        result = self._apply_discount(default_fee, is_resident)

        return result
