import configparser
import sys
from typing import Any, Iterable, Union, Dict, cast

import click
import pkg_resources

from apd.utils import ReturnCodes, Sensor


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


def parse_config_file(
        path: Union[str, Iterable[str]]
) -> Dict[str, Dict[str, str]]:
    parser = configparser.ConfigParser()
    parser.read(path, encoding='utf-8')
    try:
        plugin_names = [
            name for name in parser.get('config', 'plugins').split() if name
        ]
    except configparser.NoSectionError:
        raise RuntimeError("Could not find [config] section in file")
    except configparser.NoOptionError:
        raise RuntimeError("Could not find plugins line in [config] section")
    plugin_data = {}

    for plugin_name in plugin_names:
        try:
            plugin_data[plugin_name] = dict(parser.items(plugin_name))
        except configparser.NoSectionError:
            raise RuntimeError(f"Could not find [{plugin_name}] section in file")
    return plugin_data


def get_sensors_entry_points() -> Iterable[Sensor[Any]]:
    sensors = []
    for sensor_class in pkg_resources.iter_entry_points("apd.sensors.sensor"):
        class_ = sensor_class.load()
        sensors.append(cast(Sensor[Any], class_()))
    return sensors


def get_sensors(path: str) -> Iterable[Sensor[Any]]:
    sensors = []
    for plugin_name, sensor_data in parse_config_file(path).items():
        try:
            class_path = sensor_data.pop("plugin")
        except TypeError:
            raise RuntimeError(
                f"Could not find plugin= line in [{plugin_name}] section"
            )
        sensors.append(get_sensor_by_path(class_path, **sensor_data))
    return sensors


@click.command(help="Displays the values of the sensors")
@click.option(
    "--develop", required=False, metavar="path", help="Load a sensor by Python path"
)
@click.option(
    "--config",
    required=False,
    default="config.cfg",
    metavar="config_path",
    help="Load the specified configuration file",
)
def show_sensors(develop: str, config: str) -> None:
    sensors: Iterable[Sensor[Any]]
    if develop:
        try:
            sensors = [get_sensor_by_path(develop)]
        except RuntimeError as error:
            click.secho(str(error), fg="red", bold=True)
            sys.exit(ReturnCodes.BAD_SENSOR_PATH)
    else:
        try:
            sensors = get_sensors(config)
        except RuntimeError as error:
            click.secho(str(error), fg="red", bold=True)
            sys.exit(ReturnCodes.BAD_CONFIG)
    for sensor in sensors:
        click.secho(sensor.title, bold=True)
        click.echo(str(sensor))
        click.echo("")
    sys.exit(ReturnCodes.OK)


if __name__ == "__main__":
    show_sensors()
