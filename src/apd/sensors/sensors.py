#!/usr/bin/env python
# coding: utf-8

import math
import sys
from typing import Any, Optional, List, Tuple, Iterable

import psutil

from apd.utils import Sensor


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
