#! /usr/bin/env python
# coding:utf-8

import os

# A レコードの名前
a_record_filenames = [
    "math.kyoto-u.ac.jp.zone",
]
# PTR レコードの名前とそのネットワーク
ptr_record_filename_networks = [
    ('10.226.141.rev', '10.226.141.0/24'),
    ('10.226.142.rev', '10.226.142.0/24'),
    ('10.226.165.rev', '10.226.165.0/24')
]

# レコードファイルがあるディレクトリ
# デフォルトではこのスクリプトファイルが存在する
# ディレクトリにある zones/ 以下に配置する
basedir = os.path.join(
    os.path.abspath(os.path.dirname(__file__)),
    "zones"
)
