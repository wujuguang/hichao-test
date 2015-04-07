hichao-test

简介:
-----

pycharm自带个工具，在菜单Tools --> Test RESTful Web Service可以打开，可视化界面的操作，但不利于参数输入后保存以及后续的复用。

此工具基于以上缺点，直接借助linux工具，结合实际的个人需求与想法，以拦截请求、保存请求、复用的流程进行，为方便个人所用定制。

依赖:
-----
    ::

        $ sudo yum install curl
        $ sudo apt-get install curl

使用:
-----

    模块介绍：
    ::

        curl_reader.py:
            - 读取存放测试脚本的文件, 以命令行的形式执行(指定的行脚本, 指定范围的行脚本).
            - 利用 linux curl 构建测试脚本, 减少服务端开发过程中, 在测试上对客户端的依赖.


    在shell终端:
    $ hichao_curl -h
