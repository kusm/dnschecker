#! /usr/bin/env python
# coding:utf-8

# レコードファイルがあるディレクトリ
# デフォルトではこのスクリプトファイルが存在する
# ディレクトリにある zones/ 以下に配置する
zone_dir = "testzones"

# 生成した HTML をおくディレクトリ
html_dir = "build"

# レコードに関する情報をおいているディレクトリ
record_info_dir = "testzones"

# A レコードのゾーンファイル名
a_record_filenames = [
    "example.jp.zone",
]
# PTR レコードのゾーンファイル名そのネットワーク
ptr_record_filename_networks = [
    ('192.168.0.rev', '192.168.0.0/24'),
]

# レコード情報を納めたファイル
record_info_filenames = [
    '192.168.0.info',
]
