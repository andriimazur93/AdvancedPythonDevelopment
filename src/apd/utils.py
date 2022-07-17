import enum
import functools
from typing import Callable
from typing import TypeVar, Generic, Any

from click.types import ParamType

T_value = TypeVar("T_value")


class ReturnCodes(enum.IntEnum):
    OK = 0
    BAD_SENSOR_PATH = 17
    BAD_CONFIG = 18


class Sensor(Generic[T_value]):
    title: str

    def value(self) -> T_value:
        raise NotImplementedError

    @classmethod
    def format(cls, value: T_value) -> str:
        raise NotImplementedError

    def __str__(self) -> str:
        return self.format(self.value())


class PythonClassParameterType(ParamType):
    name = "pythonclass"

    def __init__(self, superclass=type):
        self.superclass = superclass

    def get_sensor_by_path(self, sensor_path: str, fail: Callable[[str], None]) -> Any:
        try:
            module_name, sensor_name = sensor_path.split(":")
        except ValueError:
            return fail(
                "Class path must be in the format dotted.path.to.module:ClassName"
            )

        try:
            import importlib
            module = importlib.import_module(module_name)
        except ImportError:
            return fail(f"Could not import module {module_name}")

        try:
            sensor_class = getattr(module, sensor_name)
        except AttributeError:
            raise RuntimeError(f"Could not find attribute {sensor_name} in {module_name}")

        if (
                isinstance(sensor_class, type)
                and issubclass(sensor_class, self.superclass)
                and sensor_class != self.superclass
        ):
            return sensor_class()
        else:
            raise RuntimeError(f"Detected object {sensor_class!r} is not recognized as a {self.superclass} type")

    def convert(self, value, param, ctx):
        fail = functools.partial(self.fail, param=param, ctx=ctx)
        return self.get_sensor_by_path(value, fail)

    def __repr__(self):
        return "PythonClass"


SensorClassParameter = PythonClassParameterType(Sensor)
