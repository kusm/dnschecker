#! /usr/bin/env python
# coding:utf-8


"""
This module parses zones files which include A and PTR records.

:copyright: (c) 2015 by the KUSM Admin Team
:license: MIT, see LICENSE for more details.
"""

import re
from record import ARecord, PTRRecord, RecordInfo
try:
    import ipaddress
except ImportError:
    import ipaddr as ipaddress


class RecordParserError(Exception):
    """
    文字列がレコードの正規表現にマッチしないとき
    に発生させるための例外
    """
    pass


class RecordParser:
    """
    A, PTR レコードを解析するクラス
    """
    def __init__(self):
        # A レコードの正規表現
        self.a_regex = re.compile(
            # r'^(?:(?P<comment>;+)\s*)?'  # コメント
            r'^(?:(?P<hostname>[\w.-]+)\s+)?'  # ホスト名
            r'(?:IN\s+)?'
            r'(?:(?P<type>A)\s+)?'  # レコードタイプ
            r'(?:(?P<ip>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\s*)?$'  # IPv4
        )
        # PTR レコードの正規表現
        self.ptr_regex = re.compile(
            # r'^(?:(?P<comment>;+)\s*)?'  # コメント
            # r'(?:\d{1,3}\.\d{1,3}\.\d{1,3}\.)?'  # ネットワークアドレス /24
            r'^(?:(?P<ip>\d{1,3})\s+)?'  # IPv4 /24
            # r'(:?\.in-addr\.arpa\.\s+)?'
            r'(?:IN\s+)?'
            r'(?:(?P<type>PTR)\s+)?'
            r'(?:(?P<hostname>[\w.-]+)\s*)?$'
        )

    def _get_shortname(
        self,
        hostname: str
    ):
        """
        FQDN から先頭のホスト名をとりだす

        >>> parser._get_shortname("host1.example.com")
        "host1"
        """
        if "." in hostname:
            return hostname.split(".")[0]
        else:
            return hostname

    def parse_a_record(
        self,
        a_record: str,
    ):
        """
        PTR レコード文字列を解析する

        >>> parser.parse_ptr_record(
        ...     "host1 A 192.168.0.1"
        ... )
        """
        match = self.a_regex.search(a_record)
        if match:
            group = match.groupdict()
            if group["ip"] and group["hostname"] and group["type"]:
                return ARecord(
                    hostname=self._get_shortname(group["hostname"]),
                    ip_address=group["ip"],
                )
        raise RecordParserError()

    def parse_ptr_record(
        self,
        ptr_record: str,
        network_address: str
    ):
        """
        PTR レコード文字列を解析する

        >>> parser.parse_ptr_record(
        ...     "1 PTR host1.example.com.",
        ...     "192.168.0.0/24"
        ... )
        """
        match = self.ptr_regex.search(ptr_record)
        if match:
            group = match.groupdict()
            if group["ip"] and group["hostname"] and group["type"]:
                network = ipaddress.ip_network(network_address)
                return PTRRecord(
                    hostname=self._get_shortname(group["hostname"]),
                    ip_address=str(network[int(group["ip"])])
                )
        raise RecordParserError()

    def parse_a_record_file(
        self,
        filename: str
    ):
        """
        ゾーンファイルを解析して A レコードをとりだす

        >>> parser.parse_a_record_file(
        ...     "zones/example.com.zone",
        ... )
        """
        a_records = []
        with open(filename) as f:
            for record in f:
                try:
                    a_record = self.parse_a_record(record)
                    a_records.append(a_record)
                except RecordParserError:
                    pass
        return a_records

    def parse_ptr_record_file(
        self,
        filename: str,
        network_address: str
    ):
        """
        ゾーンファイルを解析して PTR レコードをとりだす

        >>> parser.parse_a_record_file(
        ...     "zones/192.168.0.rev",
        ...     "192.168.0.0/24"
        ... )
        """
        ptr_records = []
        with open(filename) as f:
            for record in f:
                try:
                    ptr_record = self.parse_ptr_record(record, network_address)
                    ptr_records.append(ptr_record)
                except RecordParserError:
                    pass
        return ptr_records


class RecordInfoParserError(Exception):
    """
    文字列がレコードの正規表現にマッチしないとき
    に発生させるための例外
    """
    pass


class RecordInfoParser:
    """
    A, PTR レコードを解析するクラス
    """
    def __init__(self):
        # A レコードの正規表現
        self.record_info_regex = re.compile(
            r'^\s*(?P<ip>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\s*\|'  # IP は必須
            r'\s*(?P<hostname>[^\s|]*)\s*\|'  # ホスト名
            r'(?P<classname>[^|]*)\|'  # クラス
            r'(?P<room>[^|]*)\|'  # 部屋
            r'(?P<comment>[^|]*)$'  # コメント
        )

        self.ignored_regexes = [
            re.compile(regex)
            for regex in [
                r'^\s*#',
                r'^\s*$'
            ]
        ]

    def parse(self, record_info: str):
        match = self.record_info_regex.search(record_info)
        if match:
            group = match.groupdict()
            ip = group["ip"].strip()
            hostname = group["hostname"].strip()
            classname = group["classname"].strip()
            room = group["room"].strip()
            comment = group["comment"].strip()
            return RecordInfo(
                ip if ip else None,
                hostname if hostname else None,
                classname if classname else None,
                room if room else None,
                comment if comment else None
            )
        else:
            raise RecordInfoParserError()

    def is_ignored_line(self, line: str):
        for ignored_regex in self.ignored_regexes:
            if ignored_regex.search(line):
                return True
        return False

    def parse_file(self, filename: str):
        record_infos = []
        with open(filename) as f:
            for line in [_.strip() for _ in f]:
                if self.is_ignored_line(line):
                    continue
                else:
                    try:
                        record_info = self.parse(line)
                        record_infos.append(record_info)
                    except RecordInfoParserError:
                        pass
        return record_infos


def test_a_record_parser():
    parser = RecordParser()
    valid_a_record_answers = [
        ("host1 A 192.168.0.2",
         ARecord(
             ip_address='192.168.0.2',
             hostname='host1'
         )),
        ("host2.example.com. IN A 192.168.0.3",
         ARecord(
             ip_address='192.168.0.3',
             hostname='host2',
         )),
    ]
    for record, answer in valid_a_record_answers:
        assert parser.parse_a_record(record) == answer

    invalid_a_records = [
        ";192.168.0.3 -- DISABLED",
        "example.com IN SOA host1.example.com. root.localhost. (",
        "$ORIGIN example.com",
        "   A 192.168.0.3",
        "A  192.168.0.3",
        ";host3 IN  A   192.168.0.4",
        "; host4    IN  A   192.168.0.5",
        "; 192.168.0.5",
    ]
    for record in invalid_a_records:
        try:
            parser.parse_a_record(record)
            assert False
        except RecordParserError:
            pass


def test_ptr_record_parser():
    parser = RecordParser()
    network_address = "192.168.0.0/24"

    valid_ptr_record_answers = [
        ("1 PTR host1.example.com.",
         PTRRecord(
             hostname='host1',
             ip_address='192.168.0.1'
         )),
    ]
    for record, answer in valid_ptr_record_answers:
        assert parser.parse_ptr_record(record, network_address) == answer
    invalid_ptr_records = [
        ";; 2",
        "$ORIGIn 0.168.192.in-addr.arpa."
    ]
    for record in invalid_ptr_records:
        try:
            parser.parse_ptr_record(record, network_address)
            assert False
        except RecordParserError:
            pass


def test_parse_file():
    valid_record_infos = [
        ("192.168.0.1|host1|HOST|100|テスト用",
         RecordInfo(
             "192.168.0.1",
             "host1",
             "HOST",
             "100",
             "テスト用"
         )),
        (" 192.168.0.1 | host1 | HOST | 100 | テスト用",
         RecordInfo(
             "192.168.0.1",
             "host1",
             "HOST",
             "100",
             "テスト用"
         )),
        ("192.168.0.1|||| だれかのPC  ",
         RecordInfo(
             "192.168.0.1",
             "",
             "",
             "",
             "だれかのPC"
         )),
        ("192.168.0.1||||",
         RecordInfo(
             "192.168.0.1",
             "",
             "",
             "",
             ""
         )),
    ]
    invalid_record_infos = [
        "|host1|HOST|100|テスト用",
        " 192.168.0.1 | host1 | HOST | テスト用",
    ]
    ignored_lines = [
        "#192.168.0.1 | | | |",
        " # 192.168.0.1 | | | |",
        "   ",
        "",
    ]

    parser = RecordInfoParser()

    for line, record_info in valid_record_infos:
        assert parser.parse(line) == record_info

    for line in invalid_record_infos:
        try:
            parser.parse(line)
            assert False
        except RecordInfoParserError:
            pass

    for line in ignored_lines:
        assert parser.is_ignored_line(line)
