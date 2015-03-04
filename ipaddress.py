#! /usr/bin/env python
# coding:utf-8


def convert_ip_str2int(
    ip_address: str
) -> int:
    a, b, c, d = [int(_) for _ in ip_address.split(".")]
    return (a << 24) + (b << 16) + (c << 8) + d


def convert_ip_int2str(
    int_ip_address: int
) -> str:
    a = int_ip_address >> 24
    b = (int_ip_address >> 16) & 255
    c = (int_ip_address >> 8) & 255
    d = int_ip_address & 255
    return "{}.{}.{}.{}".format(a, b, c, d)


def test_convert_ip():
    ip_addresses = [
        "192.168.0.1",
        "192.168.1.1",
        "192.168.3.1",
        "10.226.140.1",
        "10.226.140.2",
        "10.226.140.3"
    ]

    for ip_address in ip_addresses:
        assert ip_address == convert_ip_int2str(
            convert_ip_str2int(ip_address)
        )


class IPAddress:
    def __init__(self, ip_address: str):
        self.ip_address = ip_address
        self.int_ip_address = convert_ip_str2int(ip_address)

    def __str__(self):
        return "{}".format(self.ip_address)


class IPNetwork:
    def __init__(self, network_address: str):
        _ip_address, _cidr = network_address.split("/")
        self.cidr = int(_cidr)
        self.shift_val = 32 - self.cidr
        self._ip_address = _ip_address
        self._int_ip_address = convert_ip_str2int(_ip_address)
        self.int_network_address = \
            (self._int_ip_address >> self.shift_val) << self.shift_val
        self.network_address = convert_ip_int2str(self.int_network_address)

    def __contains__(self, item: IPAddress):
        if isinstance(item, IPAddress):
            if item.int_ip_address >> self.shift_val == \
                    self.int_network_address >> self.shift_val:
                return True
            else:
                return False
        else:
            raise ValueError("{} is not IPAddress instance".format(item))

    def __str__(self):
        return "{}/{}".format(
            self.network_address,
            self.cidr
        )

    def __getitem__(self, int_host: int):
        return IPAddress(
            convert_ip_int2str(self.int_network_address + int_host)
        )

    def get_number_of_hosts(self):
        return sum(1 << i for i in range(self.shift_val))

    def hosts(self):
        return [
            convert_ip_int2str(int_host + self.int_network_address)
            for int_host in range(self.get_number_of_hosts())
        ][1:]


def ip_network(
    network_address: str
):
    return IPNetwork(network_address)


def ip_address(
    ip_address: str
):
    return IPAddress(ip_address)


if __name__ == '__main__':
    pass
