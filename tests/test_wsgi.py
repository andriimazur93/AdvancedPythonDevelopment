import pytest

from webtest import TestApp
# from tests import config_path
from apd.sensors.wsgi import sensor_values
from apd.sensors.sensors import PythonVersion

@pytest.fixture
def subject():
    return sensor_values

@pytest.fixture
def api_server(subject):
    return TestApp(subject)

@pytest.mark.functional
def test_sensor_values_returned_as_json(api_server):
    json_response = api_server.get("/sensors/").json
    python_version = PythonVersion().value()
    sensor_names = json_response.keys()
    assert "Python Version" in sensor_names
    assert json_response['Python Version'] == list(python_version)