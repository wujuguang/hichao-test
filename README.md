hichao-test
===========

hichao-test is a Tool that HTTP Test base on linux curl.

简介:
-----

pycharm自带个工具，在菜单Tools --> Test RESTful Web Service可以打开，可视化界面的操作，但不利于参数输入后保存以及后续的复用。此工具基于以上缺点，直接借助linux工具，结合实际的个人需求与想法，以拦截请求、保存请求、复用的流程进行，为方便个人所用定制。

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
        pyramid_request:   用于Pyramid项目
        tornado_request:   用于Tornado项目

        - 测试时, 输出执行时间到控制台.
        - 测试时, 输出POST信息到控制台.
        - 计算测试时程序执行时间, 并保存数据到文件.
        - 拦截测试时请求数据, 并构建curl脚本保存到文件.        

    curl_builder.py:
        - 构建生成curl测试请求数据, 以便于后续回归测试, 供curl_reader.py自动化.
        - 对之前生成报告文件做去重处理.

使用:
-----
    在shell终端:
    $ hichao_curl -h     # 执行脚本文件中的curl脚本命令.
    $ hichao_distinct -h # 对之前生成报告文件做去重处理.
    
    ＠django_request:    添入你的Django项目views函数前.
    ＠pyramid_request:   添入你的pyramid项目views函数前.
    ＠tornado_request:   添入你的Tornado项目tornado.web.RequestHandler子类函数(如:POST)前.
    
事项:
------
    在使用*_request时, 有可能因为某些原因, 其下的request.host不为实际的域名.
    比如: 使用nginx的负载均衡, headers下的Host会被改变为upstream的名称. 在其节点下添加如下即可:

    proxy_set_header Host $http_host;
    
安装:
-----
    pip install -e git+git@github.com:wujuguang/hichao-test.git

    or

    pip install -e git+https://github.com/wujuguang/hichao-test.git
