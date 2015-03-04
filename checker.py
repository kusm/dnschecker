#! /usr/bin/env python
# coding:utf-8


"""
This module checks record consistency of a Network instance.

:copyright: (c) 2015 by the KUSM Admin Team
:license: MIT, see LICENSE for more details.
"""


from network import Network
from record import DNSRecord, ARecord, PTRRecord


class Checker:
    """
    Network のレコードの整合性をチェックするクラス
    """
    def __init__(self, network: Network):
        self.network = network

    def _check_records(
        self,
        source_attr: str,
        target_attr: str,
        source_record: {str: [DNSRecord]},
        target_record: {str: [DNSRecord]}
    ):
        # 重複するレコードの辞書
        #    {"host1": {host1, host2}}
        duplicated_record = {}
        # 対応するレコード (A ならば PTR) が見つからないレコードのリスト
        not_found_records = []
        # 正引き逆引き、もしくは逆引き正引きしたときに
        # 一致しないレコードの辞書
        #    {host1: {host1, host2},
        #     host2: {host1, host2}}
        # のようにレコードをキー, レコードの集合を値とする
        cor_error_records = {}

        for key, records in source_record.items():
            # 重複定義されているかチェックする
            if len(records) >= 2:
                duplicated_record[key] = records

            for record in records:
                target_key = getattr(record, target_attr)

                # 対応するレコード (A ならば PTR, PTR ならば A)
                # が存在するかチェックする
                if target_key not in target_record:
                    not_found_records.append(record)
                else:
                    cor_records = target_record[target_key]
                    if len(cor_records) != 1 or \
                            not all(
                                getattr(cor_record, source_attr) ==
                                getattr(record, source_attr)
                                for cor_record in cor_records
                            ):

                        cor_error_records[record] = cor_records
        return duplicated_record, not_found_records, cor_error_records

    def check_a2ptr(self):
        """
        正引きのあと逆引きをしてレコードをチェックする
        """
        return self._check_records(
            "hostname",
            "ip_address",
            self.network.a_record,
            self.network.ptr_record,
        )

    def check_ptr2a(self):
        """
        逆引きのあと正引きしてレコードをチェックする
        """
        return self._check_records(
            "ip_address",
            "hostname",
            self.network.ptr_record,
            self.network.a_record,
        )

    def _show_result(
        self,
        source_attr: str,
        target_attr: str,
        source_record: {"key": [DNSRecord]},
        target_record: {"key": [DNSRecord]},
        source_name: str,
        target_name: str
    ):
        """
        self._check_records の結果を表示する
        """
        duplicated, not_found, cor_error = self._check_records(
            source_attr,
            target_attr,
            source_record,
            target_record
        )
        for key, records in duplicated.items():
            print("duplicated definition:\n\t{} -> {}".format(
                key,
                ", ".join([getattr(_, target_attr) for _ in records])
            ))
        for record in not_found:
            print(
                "corresponded {} records not found\n\t{} -> {}".format(
                    target_name,
                    getattr(record, source_attr),
                    getattr(record, target_attr),
                )
            )
        for record, cor_records in cor_error.items():
            print("correspondence error\n\t{} -> {} -> {}".format(
                getattr(record, source_attr),
                getattr(record, target_attr),
                ", ".join(getattr(_, source_attr) for _ in cor_records)
            ))

    def show_a2ptr_checker_result(self):
        self._show_result(
            "hostname",
            "ip_address",
            self.network.a_record,
            self.network.ptr_record,
            "A",
            "PTR"
        )

    def show_ptr2a_checker_result(self):
        self._show_result(
            "ip_address",
            "hostname",
            self.network.ptr_record,
            self.network.a_record,
            "PTR",
            "A",
        )


def test_network():
    # テストレコード
    #
    # A レコード           # PTR レコード
    # chiya    192.168.0.1
    #                      192.168.0.2  chino
    # syaro   192.168.0.3  192.168.0.3  syaro
    # syaro   192.168.0.4  192.168.0.4  syaro
    # rize    192.168.0.4  192.168.0.4  rize

    a_chiya = ARecord("chiya", "192.168.0.1")
    a_syaro1 = ARecord("syaro", "192.168.0.3")
    a_syaro2 = ARecord("syaro", "192.168.0.4")
    a_rize = ARecord("rize", "192.168.0.4")
    ptr_chino = PTRRecord("chino", "192.168.0.2")
    ptr_syaro1 = PTRRecord("syaro", "192.168.0.3")
    ptr_syaro2 = PTRRecord("syaro", "192.168.0.4")
    ptr_rize = PTRRecord("rize", "192.168.0.4")

    hosts = [
        a_chiya, a_syaro1, a_syaro2, a_rize,
        ptr_chino, ptr_syaro1, ptr_syaro2, ptr_rize
    ]

    a2ptr_answer = (
        {"syaro": {a_syaro1, a_syaro2}},
        [a_chiya],
        {a_syaro2: {ptr_syaro2, ptr_rize},
         a_rize: {ptr_syaro2, ptr_rize}}
    )

    ptr2a_answer = (
        {"192.168.0.4": {ptr_syaro2, ptr_rize}},
        [ptr_chino],
        {ptr_syaro1: {a_syaro1, a_syaro2},
         ptr_syaro2: {a_syaro1, a_syaro2}}
    )

    nt = Network("192.168.0.0/24")
    for host in hosts:
        nt.add_record(host)

    checker = Checker(nt)
    assert checker.check_a2ptr() == a2ptr_answer
    assert checker.check_ptr2a() == ptr2a_answer
    return list(nt)
