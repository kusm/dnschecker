#! /usr/bin/env python
# coding:utf-8


"""
This module provides Network class.

:copyright: (c) 2015 by the KUSM Admin Team
:license: MIT, see LICENSE for more details.
"""


import ipaddress
from record import DNSRecord, ARecord, PTRRecord, RecordInfo


class NetworkRangeError(Exception):
    pass


class Network:
    """
    192.168.0.0/24 のような一つのネットワークをあらわす
    """
    def __init__(
        self,
        network_address: str
    ):
        self.network_address = ipaddress.ip_network(network_address)

        # A レコード用のディクショナリで
        #    {"host1": {record1, record2}, "host2": {record3}, ...}
        # のように、ホスト名をキー、対応するレコードの集合を値とする
        self.a_record = {}

        # PTR レコード用のディクショナリで
        #    {"192.168.0.1": {record1, record2}, "192.168.0.2": {record3}, ...}
        # のように、IP アドレスをキー、対応するレコードの集合を値とする
        self.ptr_record = {}

        self.record_info = {}

    def add_record(
        self,
        record: DNSRecord
    ):
        """
        レコードを追加する

        >>> host1 = ARecord(
        ... ip_address='192.168.0.1',
        ...     hostname='host1'
        ... )
        ...
        >>> network.add_record(host1)
        """
        hostname = record.hostname
        ip_address = record.ip_address

        # レコードの IP アドレスがこのネットワークにはいっていない場合
        # NetworkRangeError をだす
        if ipaddress.ip_address(record.ip_address) not in self.network_address:
            raise NetworkRangeError("{} not in {}".format(
                ip_address, self.network_address
            ))

        # A レコードか PTR レコードかを調べて
        # self.a_record, self.ptr_record にいれる
        if isinstance(record, ARecord):
            if hostname in self.a_record:
                self.a_record[hostname].add(record)
            else:
                self.a_record[hostname] = {record}
        elif isinstance(record, PTRRecord):
            if ip_address in self.ptr_record:
                self.ptr_record[ip_address].add(record)
            else:
                self.ptr_record[ip_address] = {record}
        else:
            # どちらでもない場合は ValueError をだす
            raise ValueError("record type is {}".format(type(record)))

    def add_record_info(
        self,
        record_info: RecordInfo
    ):
        ip_address = record_info.ip_address
        # レコードの IP アドレスがこのネットワークにはいっていない場合
        # NetworkRangeError をだす
        if ipaddress.ip_address(record_info.ip_address) \
                not in self.network_address:
            raise NetworkRangeError("{} not in {}".format(
                ip_address, self.network_address
            ))

        if ip_address in self.record_info:
            self.record_info[ip_address].add(record_info)
        else:
            self.record_info[ip_address] = {record_info}

    def is_ipaddress(self, name: str):
        """
        name が IP アドレスかどうかチェックする
        """
        try:
            ipaddress.ip_address(name)
            return True
        except ValueError:
            return False

    def __getitem__(self, key: str):
        if self.is_ipaddress(key):
            return self.ptr_record[key]
        else:
            self.hostname_ip[key]

    def __contains__(self, key: str):
        if self.is_ipaddress(key):
            return key in self.ip_hostname
        else:
            return key in self.hostname_ip

    def _pop_record_info(
        self,
        record_infos: {RecordInfo},
        hostname: str,
    ):
        for record_info in record_infos:
            if record_info.hostname == hostname:
                return record_info, record_infos - {record_info}
        return None, record_infos

    def __iter__(self):
        """
        A レコードと PTR レコードとレコード情報から ip_address をキーとして

            (ip_address,
             a_hostname,
             ptr_hostname,
             reocrd_info.hostname,
             record_info.classname,
             reocrd_info.room,
             record_info.comment
             )

        のリストを生成する

        例えば

            A レコード           # PTR レコード
            hoge    192.168.0.1
                                 192.168.0.2  fuga
            syaro   192.168.0.3  192.168.0.3  syaro
            syaro   192.168.0.4  192.168.0.4  syaro
            rize    192.168.0.4  192.168.0.4  rize

        というレコードがこの network にはいっているとき、

        >>> list(network)
        [('192.168.0.1', 'hoge', None, None, None, None, None),
         ('192.168.0.2', None, 'fuga', None, None, None, None),
         ('192.168.0.3', 'syaro', 'syaro', None, None, None, None),
         ('192.168.0.4', 'syaro', 'syaro', None, None, None, None),
         ('192.168.0.4', 'rize', 'rize', None, None, None, None),
         ('192.168.0.5', None, None, None, None, None, None),
         ('192.168.0.6', None, None, None, None, None, None),
          ...
        ]

        となる。
        """
        a_ip_hostname = {
            str(ip_address): []
            for ip_address in self.network_address.hosts()
        }
        for hostname, records in self.a_record.items():
            for record in records:
                a_ip_hostname[record.ip_address].append(record)

        ip_a_ptr_hosts = []
        for ip_address in self.network_address.hosts():
            _ip_a_ptr_hosts = []
            ip = str(ip_address)
            a_set = set(record.hostname for record in a_ip_hostname[ip])
            ptr_set = set(
                record.hostname for record in self.ptr_record.get(ip, [])
            )
            a_and_ptr = a_set.intersection(ptr_set)
            only_a = a_set - ptr_set
            only_ptr = ptr_set - a_set

            record_infos = self.record_info.get(ip, [])

            for hostname in a_and_ptr:
                record_info, record_infos = self._pop_record_info(
                    record_infos, hostname
                )
                if record_info:
                    _ip_a_ptr_hosts.append(
                        (ip, hostname, hostname,
                         record_info.hostname,
                         record_info.classname,
                         record_info.room,
                         record_info.comment
                         )
                    )
                else:
                    _ip_a_ptr_hosts.append(
                        (ip, hostname, hostname,
                         None, None, None, None)
                    )
            for hostname in only_a:
                record_info, record_infos = self._pop_record_info(
                    record_infos, hostname
                )
                if record_info:
                    _ip_a_ptr_hosts.append(
                        (ip, hostname, None,
                         record_info.hostname,
                         record_info.classname,
                         record_info.room,
                         record_info.comment
                         )
                    )
                else:
                    _ip_a_ptr_hosts.append(
                        (ip, hostname, None,
                         None, None, None, None)
                    )
            for hostname in only_ptr:
                record_info, record_infos = self._pop_record_info(
                    record_infos, hostname
                )
                if record_info:
                    _ip_a_ptr_hosts.append(
                        (ip, None, hostname,
                         record_info.hostname,
                         record_info.classname,
                         record_info.room,
                         record_info.comment
                         )
                    )
                else:
                    _ip_a_ptr_hosts.append(
                        (ip, None, hostname,
                         None, None, None, None)
                    )

            for record_info in record_infos:
                _ip_a_ptr_hosts.append(
                    (ip, None, None,
                     record_info.hostname,
                     record_info.classname,
                     record_info.room,
                     record_info.comment
                     )
                )

            if _ip_a_ptr_hosts:
                ip_a_ptr_hosts.extend(_ip_a_ptr_hosts)
            else:
                ip_a_ptr_hosts.append(
                    (ip, None, None,
                     None, None, None, None)
                )
        return iter(ip_a_ptr_hosts)
