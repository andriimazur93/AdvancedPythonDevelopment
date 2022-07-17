import socket
from unittest import mock

import pytest

from apd.sensors.sensors import IPAddresses


@pytest.fixture
def sensor():
    return IPAddresses()


class TestIPAddressFormatter:
    @pytest.fixture
    def subject(self, sensor):
        return sensor.format

    def test_format_single_ipv4(self, subject):
        ips = [("AF_INET", "192.0.2.1")]
        assert subject(ips) == "192.0.2.1 (IPv4)"

    def test_format_single_ipv6(self, subject):
        ips = [("AF_INET6", "2001:DB8::1")]
        assert subject(ips) == "2001:DB8::1 (IPv6)"

    def test_format_mixed_list(self, subject):
        ips = [("AF_INET", "192.0.2.1"), ("AF_INET6", "2001:DB8::1")]
        assert subject(ips) == "192.0.2.1 (IPv4)\n2001:DB8::1 (IPv6)"

    def test_unusual_protocols_are_marked_as_unknown(self, subject):
        ips = [("AF_IRDA", "ffff")]
        assert subject(ips) == "ffff (Unknown)"
