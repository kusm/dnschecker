DNS Checker
==================

DNS レコードが正しく設定されているかをチェックするスクリプトです。
`/home/kusm/git_repos/dnschecker.git` においてあります。

必要なもの
-----------

Python3 が必要です。HTML を生成するには
テンプレートエンジンの `jinja2` が必要です。

はじめのテスト (動くか確かめる)
----------------------------------

    $ git clone /home/kusm/git_repos/dnschecker.git
    $ cd dnschecker

して `test.py` を実行してみましょう。`test.py` では

    # A レコード            # PTR レコード
    hoge    10.226.142.130
                            10.226.142.140  fuga
    syaro   10.226.142.248  10.226.142.248  syaro
    syaro   10.226.142.249  10.226.142.249  syaro
    rize    10.226.142.249  10.226.142.249  rize

というレコードがあると想定して、プログラムを実行します。

    $ python3 test.py
    warning: duplicated definition:
            syaro -> 10.226.142.248, 10.226.142.249
    corresponded PTR records not found
            A: hoge -> 10.226.142.130
    correspondence error
            syaro -> 10.226.142.249 -> rize, syaro
    correspondence error
            rize -> 10.226.142.249 -> rize, syaro
    warning: duplicated definition:
            10.226.142.249 -> rize, syaro
    corresponded A records not found
            PTR: 10.226.142.140 -> fuga
    correspondence error
            10.226.142.249 -> syaro -> 10.226.142.248, 10.226.142.249
    correspondence error
            10.226.142.248 -> syaro -> 10.226.142.248, 10.226.142.249

スクリプトの中身
-----------------

dnschecker.py は A レコードと PTR レコードが対応しているかをチェックします。
もしも対応が正しくない場合には、対応していないレコードを標準出力に出力します。

A レコードのチェックは

*   A レコードでホスト名が重複して定義されていないか
*   A レコードに対応する PTR レコードが存在するか
*   存在する場合には逆引きを行うと A レコードのホスト名に一致するか

を行います。PTR レコードのチェックはこの逆を行います。

このチェックでは、大文字小文字を区別します。
DNS レコードのホスト名としては大文字小文字は区別されませんが、
大文字小文字を一致させておく方がよいでしょう。


使い方
--------

1.  zones ディレクトリを(なければ) 作成し、その下にゾーンファイルを配置する。

        zones/
            math.kyoto-u.ac.jp.zone
            10.226.141.rev
            10.226.142.rev
            10.226.165.rev

2.  対応するゾーンファイルの名前を `config.py` にかく。


        ## config.py の中の対応する場所にゾーンファイルの名前を書く
        # A レコードの名前
        a_record_names = [
            "math.kyoto-u.ac.jp.zone",
        ]
        # PTR レコードの名前
        ptr_record_names = [
            '10.226.141.rev',
            '10.226.142.rev',
            '10.226.165.rev',
        ]

3.  レコードをチェックするには

        $ python3 dnschecker.py

    を実行する。

4.  レコードチェックの結果を HTML 出力をするには

        $ python3 dnschecker.py --html

    を実行する。すると `build/` 以下に HTML ファイルが生成される。

        build/
            index.html
            a-ptr.html
            static/
