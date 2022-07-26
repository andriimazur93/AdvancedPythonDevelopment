import pytest
from click.testing import CliRunner

import apd.sensors.sensors
from apd.sensors.cli import show_sensors


def test_sensors():
    assert hasattr(apd.sensors.sensors, "PythonVersion")


@pytest.mark.functional
def test_python_version_is_first_two_lines_of_cli_output():
    runner = CliRunner()
    result = runner.invoke(show_sensors)
    python_version = str(apd.sensors.sensors.PythonVersion())
    assert ["Python Version", python_version] == result.stdout.split("\n")[:2]
