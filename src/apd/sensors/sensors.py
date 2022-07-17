#!/usr/bin/env python
# coding: utf-8
import math
import sys
from typing import Any, Optional, List, Tuple, Iterable

import click
import psutil

from apd.humidity_sensor.sensor import HumiditySensor
from apd.thermometer.sensor import Thermometer
from apd.utils import ReturnCodes, Sensor, SensorClassParameter


class PythonVersion(Sensor[Any]):
    title = "Python Version"

    def value(self) -> Any:
        return sys.version_info

    @classmethod
    def format(cls, value: Any) -> str:
        if value.micro == 0 and value.releaselevel == "alpha":
            return "{0.major}.{0.minor}.{0.micro}a{0.serial}".format(value)
        return "{0.major}.{0.minor}".format(value)


class IPAddresses(Sensor[Iterable[Tuple[str, str]]]):
    title = "IP Addresses"
    FAMILIES = {"AF_INET": "IPv4", "AF_INET6": "IPv6"}

    def value(self) -> List[Tuple[str, str]]:
        address_info = [('AF_INET', '192.0.2.1')]
        return address_info

    @classmethod
    def format(cls, value: Iterable[Tuple[str, str]]) -> str:
        return "\n".join(
            "{0} ({1})".format(address[1], cls.FAMILIES.get(address[0], "Unknown"))
            for address in value
        )


class CPULoad(Sensor[float]):
    title = "CPU Usage"

    def value(self) -> float:
        return psutil.cpu_percent(interval=3) / 100.0

    @classmethod
    def format(cls, value: float) -> str:
        return "{:.1%}".format(value)


class RAMAvailable(Sensor[int]):
    title = "RAM Available"
    UNITS = ("B", "KiB", "MiB", "GiB", "TiB", "PiB", "EiB")
    UNIT_SIZE = 2 ** 10

    def value(self) -> int:
        return psutil.virtual_memory().available

    @classmethod
    def format(cls, value: int) -> str:
        magnitude = math.floor(math.log(value, cls.UNIT_SIZE))
        max_magnitude = len(cls.UNITS) - 1
        magnitude = min(magnitude, max_magnitude)
        scaled_value = value / (cls.UNIT_SIZE ** magnitude)
        return "{:.1f} {}".format(scaled_value, cls.UNITS[magnitude])


class ACStatus(Sensor[Optional[bool]]):
    title = "AC Connected"

    def value(self) -> Optional[bool]:
        battery = psutil.sensors_battery()
        if battery is not None:
            return battery.power_plugged
        else:
            return None

    @classmethod
    def format(cls, value: Optional[bool]) -> str:
        if value is None:
            return "Unknown"
        elif value:
            return "Connected"
        else:
            return "Not connected"


def get_sensors() -> Iterable[Sensor[Any]]:
    return [
        PythonVersion(),
        IPAddresses(),
        CPULoad(),
        RAMAvailable(),
        ACStatus(),
        HumiditySensor(),
        Thermometer(),
    ]


def get_sensor_by_path(sensor_path: str) -> Any:
    import importlib
    try:
        module_name, sensor_name = sensor_path.split(":")
    except ValueError:
        raise RuntimeError("Sensor path must be in the format 'dotted.path.to.module:ClassName'")
    try:
        module = importlib.import_module(module_name)
    except ImportError:
        raise RuntimeError(f"Could not import module {module_name}")

    try:
        sensor_class = getattr(module, sensor_name)
    except AttributeError:
        raise RuntimeError(f"Cound not find attribute {sensor_name} in {module_name}")

    if (isinstance(sensor_class, type) and issubclass(sensor_class, Sensor) and sensor_class != Sensor):
        return sensor_class()
    else:
        raise RuntimeError(f"Detected object {sensor_class!r} is not recognized as a Sensor type")


@click.command(help="Displays the values of the sensors")
@click.option(
    "--develop", required=False, metavar="path",
    help="Load a sensor by Python path", type=SensorClassParameter,
)
def show_sensors(develop: str) -> None:
    sensors: Iterable[Sensor[Any]]
    if develop:
        try:
            sensors = [develop]
        except RuntimeError as error:
            click.secho(str(error), fg='red', bold=True, err=True)
            sys.exit(ReturnCodes.BAD_SENSOR_PATH)
    else:
        sensors = get_sensors()
    for sensor in sensors:
        click.secho(sensor.title, bold=True)
        click.echo(str(sensor))
        click.echo("")


if __name__ == "__main__":
    show_sensors()
