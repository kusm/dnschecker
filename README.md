DNS Checker
==================

DNS レコードが正しく設定されているかをチェックするスクリプトです。
`/home/kusm/git_repos/dnschecker.git` においてあります。

必要なもの
-----------

Python3 が必要です。HTML を生成するには
テンプレートエンジンの `jinja2` が必要です。

これらをいれるには
`python3`, `python3-jinja2`
パッケージをインストールしましょう。

    $ sudo aptitude install python3 python3-jinja2

スクリプトの説明
-----------------

dnschecker.py は A レコードと PTR レコードが対応しているかをチェックします。
もしも対応が正しくない場合には、対応していないレコード情報を標準出力
にだします。

A レコードのチェックは

*   A レコードでホスト名が重複して定義されていないか
*   A レコードに対応する PTR レコードが存在するか
*   対応する PTR レコードが存在する場合には、逆引きを行うと A レコードのホスト名に一致するか

を行います。PTR レコードのチェックは A レコードの場合の逆を行い、

*   PTR レコードでホスト名が重複して定義されていないか
*   PTR レコードに対応する A レコードが存在するか
*   存在する場合には正引きを行うと PTR レコードのホスト名に一致するか

をチェックします。

例
----

例として

    # A レコード           # PTR レコード
    # chiya    192.168.0.1
    #                      192.168.0.2  chino
    # syaro   192.168.0.3  192.168.0.3  syaro
    # syaro   192.168.0.4  192.168.0.4  syaro
    # rize    192.168.0.4  192.168.0.4  rize

というレコードがあったとしましょう。
この例の正引きのゾーンファイルは `testzones/example.jp.zone`
逆引きのゾーンファイルは `testzones/192.168.0.info`
レコード情報のファイルは `testzones/192.168.0.info`
にあります。

dnschecker を実行するには、はじめに `config.py` を編集し
どのディレクトリの何という名前のゾーンファイルをチェックするか
指定します。

このテストでは以下のように設定しましょう。

    # レコードファイルがあるディレクトリ
    zone_dir = "testzones"

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

この設定ができたら dnschecker を実行してレコードの整合性をチェックします。

    $ python3 dnschecker.py
    cheking 192.168.0.0/24 network
    duplicated definition:
            syaro -> 192.168.0.3, 192.168.0.4
    corresponded PTR records not found
            chiya -> 192.168.0.1
    correspondence error
            syaro -> 192.168.0.4 -> rize, syaro
    correspondence error
            rize -> 192.168.0.4 -> rize, syaro
    duplicated definition:
            192.168.0.4 -> rize, syaro
    corresponded A records not found
            192.168.0.2 -> chino
    correspondence error
            192.168.0.3 -> syaro -> 192.168.0.3, 192.168.0.4
    correspondence error
            192.168.0.4 -> syaro -> 192.168.0.3, 192.168.0.4

出力の意味は

    duplicated definition:
            syaro -> 192.168.0.3, 192.168.0.4

は `syaro` というホスト名が A レコードで二重に定義されていることを示しています。

    corresponded PTR records not found
            chiya -> 192.168.0.1

は A レコード `chiya 192.168.0.1` に対応する PTR レコードが存在しないことを
示しています。

      correspondence error
              syaro -> 192.168.0.4 -> rize, syaro

は正引き逆引きをするとホスト名が一致しないことを示しています。

このチェックでは、大文字小文字を区別します。
DNS レコードのホスト名としては大文字小文字は区別されませんが、
大文字小文字を一致させておく方がよいでしょう。

この結果とレコード表を HTML に出力することもできます。
はじめに config.py の `html_dir` を設定して
HTML を出力するディレクトリを設定します。

    # 生成した HTML をおくディレクトリ
    html_dir = "build"

次に dnschecker.py を `--html` オプション付きで実行します。

    $ python3 dnschecker.py --html

すると build ディレクトリ以下に index.html と 192.168.0.0.html という
HTML が生成されます。

dnschecker の使い方
------------------------

`dnschecker.py` は次のように使用します。


1.  config.py を設定する

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

    `zone_dir`, `record_info_dir`, `html_dir` はコマンドラインオプション
    `-z`, `-r`, `-d` を使っても変更できる。詳しくは `python3 dnschecker.py -h` を見ること。

2.  対応するディレクトリにファイルがあることを確認する。

        testzones/
            example.jp.zone
            192.168.0.rev
            192.168.0.info

3.  レコードをチェックするには

        $ python3 dnschecker.py

    を実行する。

    HTML を生成するには

        $ python3 dnschecker.py --html

    を実行する。この場合 `config.html_dir` 以下に HTML ファイルが生成される

4.  レコードチェックの結果を HTML 出力をするには

        $ python3 dnschecker.py --html

    を実行する。すると `build/` 以下に HTML ファイルが生成される。

        build/
            192.168.0.0.html
            a_ptr.css
            index.css
            index.html
