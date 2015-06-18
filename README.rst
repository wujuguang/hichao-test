hichao-test
-----------

hichao-test is a Tool that HTTP Test base on linux curl.

简介:
=====

pycharm自带个工具，在菜单Tools --> Test RESTful Web Service可以打开，可视化界面的操作，但不利于参数输入后保存以及后续的复用。此工具基于以上缺点，直接借助linux工具，结合实际的个人需求与想法，以拦截请求、保存请求、复用的流程进行，为方便个人所用定制。

使用:
=====

    依赖:
    
    linux系统需要安装curl
    ::

        $ sudo yum install curl
        $ sudo apt-get install curl

    模块介绍：
    ::

        curl_reader.py:
            - 读取存放测试脚本的文件, 以命令行的形式执行(指定的行脚本, 指定范围的行脚本).
            - 利用 linux curl 构建测试脚本, 减少服务端开发过程中, 在测试上对客户端的依赖.

        @django_request:
        用于Django项目

        @pyramid_request:
        用于Pyramid项目

        @tornado_request:
        用于Tornado项目

            - 测试时, 输出POST信息到控制台.
            - 拦截测试时请求数据, 保存并构建curl脚本保存到文件.

        curl_builder.py:
            - 构建生成curl测试请求数据, 以便于后续回归测试, 供curl_reader.py自动化.
            - 对之前生成报告文件做去重处理.


    在shell终端:
    ::
    
    $ hichao_curl -h
    $ hichao_distinct -h

