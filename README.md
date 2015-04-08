hichao-test
===========

hichao-test is a Tool that HTTP Test base on linux curl.

依赖:
-----

    $ sudo yum install curl
    $ sudo apt-get install curl
    
模块介绍:
---------

    conf.py:
        - 默认的配置项, 一般无需改动.

    curl_reader.py:
        - 读取存放测试脚本的文件, 以命令行的形式执行(指定的行脚本, 指定范围的行脚本).
        - 利用 linux curl 构建测试脚本, 减少服务端开发过程中, 在测试上对客户端的依赖.

    decorator.py:
        django_request:    用于Django项目
        tornado_request:   用于Tornado项目

        - 测试时, 输出POST信息到控制台.
        - 拦截测试时请求数据, 保存并构建curl脚本保存到文件.

    curl_builder.py:
        - 构建生成curl测试请求数据, 以便于后续回归测试, 供curl_reader.py自动化.
        - 对之前生成报告文件做去重处理.

使用:
-----
    在shell终端:
    $ hichao_curl -h     # 执行脚本文件中的curl脚本命令.
    $ hichao_distinct -h # 对之前生成报告文件做去重处理.
    
    ＠django_request:    添入你的Django项目views函数前.
    ＠tornado_request:   添入你的Tornado项目tornado.web.RequestHandler子类函数(如:POST)前.
