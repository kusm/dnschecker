#! /usr/bin/env python
# coding:utf-8


"""
DNS Checker

:copyright: (c) 2015 by the KUSM Admin Team
:license: MIT, see LICENSE for more details.
"""

from network import Network, NetworkRangeError
from checker import Checker
from genhtml import HTMLBuilder
from parser import RecordParser, RecordInfoParser


def make_ip_network(
    a_record_filenames: [str],
    ptr_record_filename_networks: [str],
    record_info_filenames: [str]
) -> {str: Network}:
    """
    ゾーンファイルから Network インスタンスを生成する

    返り値は

        {"192.168.0.0/24": mynetwork1,
         "192.168.1.0/24": mynetwork2,
         }

    のような、ネットワークアドレスをキーとする辞書
    """
    network = {}
    for network_address in [network_address for _, network_address in
                            ptr_record_filename_networks]:
        network[network_address] = Network(network_address)

    # ゾーンファイルを解析する
    parser = RecordParser()
    for filename in a_record_filenames:
        for a_record in parser.parse_a_record_file(filename):
            for nt in network.values():
                try:
                    nt.add_record(a_record)
                except NetworkRangeError:
                    pass

    for filename, network_address in ptr_record_filename_networks:
        for ptr_record in parser.parse_ptr_record_file(
                filename, network_address
        ):
            try:
                network[network_address].add_record(ptr_record)
            except NetworkRangeError:
                pass

    # レコード情報を解析する
    record_info_parser = RecordInfoParser()
    for filename in record_info_filenames:
        for record_info in record_info_parser.parse_file(filename):
            for nt in network.values():
                try:
                    nt.add_record_info(record_info)
                except NetworkRangeError:
                    pass

    return network


def check_records(
    ip_network: {str: Network}
) -> None:
    """
    Network インスタンスの A レコードと PTR レコードが
    正しく対応しているかチェックする
    """
    for network_address, network in ip_network.items():
        print("cheking {} network".format(network_address))
        checker = Checker(network)
        checker.show_a2ptr_checker_result()
        checker.show_ptr2a_checker_result()


if __name__ == "__main__":
    from logging import getLogger, basicConfig, INFO, DEBUG
    import argparse
    import config
    import os
    # from genhtml import genhtml

    # parse arg
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="show DEBUG log"
    )
    parser.add_argument(
        "-z", "--zone-dir",
        type=str,
        nargs="?",
        default=os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            config.zone_dir
        ),
        help="zone directory"
    )
    parser.add_argument(
        "-d", "--html-dir",
        type=str,
        nargs="?",
        default=os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            config.html_dir
        ),
        help="html directory"
    )
    parser.add_argument(
        "-r", "--record-info-dir",
        type=str,
        nargs="?",
        default=os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            config.record_info_dir
        ),
        help="record info directory"
    )
    parser.add_argument(
        "--html",
        action="store_true",
        help="generate html"
    )
    args = parser.parse_args()
    # logger
    basicConfig(
        level=DEBUG if args.verbose else INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    )
    logger = getLogger(__file__)
    zone_dir = os.path.abspath(args.zone_dir)
    html_dir = os.path.abspath(args.html_dir)
    record_info_dir = os.path.abspath(args.record_info_dir)

    # ゾーンファイルのパスを求める
    a_record_filenames = [
        os.path.join(zone_dir, filename)
        for filename in config.a_record_filenames
    ]
    ptr_record_filename_networks = [
        (os.path.join(zone_dir, filename), ip_network)
        for filename, ip_network in config.ptr_record_filename_networks
    ]
    record_info_filenames = [
        os.path.join(record_info_dir, filename)
        for filename in config.record_info_filenames
    ]

    # ネットワークを定義する
    network = make_ip_network(
        a_record_filenames,
        ptr_record_filename_networks,
        record_info_filenames
    )

    if args.html:
        # --html オプションが有効のとき
        # HTML を生成する
        builder = HTMLBuilder()
        builder.render(network, html_dir)
    else:
        # --html オプションが無効のとき
        # ゾーンファイルをチェックして結果を標準出力にだす
        check_records(
            network
        )
