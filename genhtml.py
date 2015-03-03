#! /usr/bin/env python
# coding:utf-8

from network import Network
from checker import Checker
import jinja2
import os


def get_abs_path(path):
    return os.path.join(
        os.path.abspath(os.path.dirname(__file__)),
        path
    )


class HTMLBuilder:
    def __init__(self):
        # initializing jinja2
        self.env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(
                get_abs_path("templates")
            )
        )

    def index_render(
        self,
        ip_network: {str: Network}
    ):

        a_duplicated, a_not_found, a_cor_error = [], [], []
        ptr_duplicated, ptr_not_found, ptr_cor_error = [], [], []

        for network_address, network in ip_network.items():
            checker = Checker(network)

            _a_duplicated, _a_not_found, _a_cor_error = checker.check_a2ptr()
            a_duplicated.extend(list(_a_duplicated.items()))
            a_not_found.extend(_a_not_found)
            a_cor_error.extend(list(_a_cor_error.items()))

            _ptr_duplicated, _ptr_not_found, _ptr_cor_error = \
                checker.check_ptr2a()
            ptr_duplicated.extend(list(_ptr_duplicated.items()))
            ptr_not_found.extend(_ptr_not_found)
            ptr_cor_error.extend(list(_ptr_cor_error.items()))

        # index.html
        index_path = get_abs_path('build/index.html')
        with open(index_path, 'w') as f:
            template = self.env.get_template(
                'index_template.html'
            )
            html = template.render(
                a_only=a_not_found,
                ptr_only=ptr_not_found,
                a_overlaped=[
                    (hostname, [record.ip for record in records])
                    for (hostname, records) in a_duplicated
                ],
                ptr_overlaped=[
                    (ip_address, [record.hostname for record in records])
                    for (ip_address, records) in ptr_duplicated
                ],
                a_ptr_not_same=[
                    (a_record.hostname,
                     a_record.ip_address,
                     [ptr_record.hostname for ptr_record in ptr_records]
                     )
                    for a_record, ptr_records in a_cor_error
                ],
                ptr_a_not_same=[
                    (ptr_record.ip_address,
                     ptr_record.hostname,
                     [a_record.ip_address for a_record in a_records]
                     )
                    for ptr_record, a_records in ptr_cor_error
                ]
            )
            f.write(html)
            print("making {} ... done".format(index_path))

    def ip_host_render(
        self,
        ip_network: {str: Network}
    ):
        for network_address, network in ip_network.items():
            ip_address = network_address.split("/")[0]
            html_path = get_abs_path('build/{}.html'.format(ip_address))

            with open(html_path, 'w') as f:
                template = self.env.get_template(
                    'a_ptr_template.html'
                )
                html = template.render(
                    records=list(network)
                )
                f.write(html)
                print("making {} ... done".format(html_path))

    def render(
        self,
        ip_network
    ):
        self.index_render(ip_network)
        self.ip_host_render(ip_network)
