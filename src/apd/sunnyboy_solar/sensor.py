import typing as t

from apd.sensors.sensors import Sensor

bt_addr = "00:80:25:00:00:00"


class SolarCumulativeOutput(Sensor[t.Optional[float]]):
    title = "Solar panel cumulative output"

    def value(self) -> t.Optional[float]:
        import random
        return random.randint(1, 10000)

    @classmethod
    def format(cls, value: t.Optional[float]) -> str:
        if value is None:
            return "Unknown"
        return "{} kWh".format(value / 1000)
