from typing import Optional

from apd.utils import Sensor


class Thermometer(Sensor[Optional[float]]):
    title = "Ambient Temperature"

    def value(self) -> Optional[float]:
        import random
        return random.randint(1, 100)

    @staticmethod
    def celsius_to_fahrenheit(value: float) -> float:
        return value * 9 / 5 + 32

    @classmethod
    def format(cls, value: Optional[float]) -> str:
        if value is None:
            return "Unknown"
        else:
            return "{:.1f}C ({:.1f}F)".format(value, cls.celsius_to_fahrenheit(value))

    def __str__(self) -> str:
        return self.format(self.value())
