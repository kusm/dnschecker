#! /usr/bin/env python
# coding:utf-8


class DNSRecord:
    """
    ひとつの DNS レコードをあらわすクラス

    >>> DNSRecord(
    ...  "host1",
    ...  "192.168.0.1",
    ...  "A"
    ... )
    """
    def __init__(
        self,
        hostname: str,
        ip_address: str,
        type,  # "A" もしくは "PTR"
        used: bool=True
    ):
        self.hostname = hostname
        self.ip_address = ip_address
        self.type = type
        self.used = used

    def __eq__(self, other):
        return self.hostname == other.hostname and \
            self.ip_address == other.ip_address and \
            self.type == other.type and \
            self.used == other.used

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.hostname, self.ip_address, self.type, self.used))

    def __str__(self):
        print("{} {} {}".format(self.type, self.hostname, self.type))


class ARecord(DNSRecord):
    """
    A レコードを表すクラス

    >>> ARecord(
    ...  "host1",
    ...  "192.168.0.1",
    ... )
    """
    def __init__(
        self,
        hostname: str,
        ip_address: str,
        used: bool=True
    ):
        DNSRecord.__init__(
            self,
            hostname,
            ip_address,
            "A",
            used
        )


class PTRRecord(DNSRecord):
    """
    PTR レコードを表すクラス

    >>> PTRRecord(
    ...  "host1",
    ...  "192.168.0.1",
    ... )
    """
    def __init__(
        self,
        hostname: str,
        ip_address: str,
        used: bool=True
    ):
        DNSRecord.__init__(
            self,
            hostname,
            ip_address,
            "PTR",
            used
        )
