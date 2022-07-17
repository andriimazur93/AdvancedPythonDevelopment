from apd.utils import Sensor
from typing import Optional


class HumiditySensor(Sensor[Optional[float]]):
    title = "Relative Humidity"

    def value(self) -> Optional[float]:
        import random
        return random.randint(1, 100)

    @classmethod
    def format(cls, value: Optional[float]) -> str:
        if value is None:
            return "Unknown"
        else:
            return "{:.1%}".format(value)
