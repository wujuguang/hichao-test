# !/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals, print_function

u"""拦截request, 构建curl脚本, 并存储类.
    没使用middleware的形式, 拦截所需service, 使定义更灵活.
"""

import os
import datetime
from optparse import OptionParser
from hichao_test.conf import log, login_api, logout_api, save_rows_queue

try:
    from queue import Queue
except ImportError:
    from Queue import Queue


class DataStore(object):
    u"""数据行存储类.
    """

    def __init__(self, report_file, maxsize=5):
        super(DataStore, self).__init__()
        self._report_file = report_file
        self._lines_store = Queue(maxsize=maxsize)

        # 创建存放的路径
        dir_path = os.path.dirname(self._report_file)
        if dir_path and not os.path.exists(dir_path):
            os.makedirs(dir_path)

    def get_report_file(self):
        return self._report_file

    def open_file_data(self):
        u"""读取报告文件
        """

        if os.path.exists(self._report_file):
            read_file = open(self._report_file, 'rb')
            return read_file.readlines()

        return None

    def save_line_data(self, line):
        u"""保存行数据.

            :param line
        """

        # 存储到队列
        if not self._lines_store.full():
            self._lines_store.put(line)

        # 从队列中保存
        if self._lines_store.full():
            self.save_file_data()

    def save_file_data(self):
        u"""存储数据到文件.
        """

        with open(self._report_file, 'ab') as f:
            if not self._lines_store.empty():
                log_time = '#### %s\n' % str(datetime.datetime.now())
                f.write(log_time)

            while not self._lines_store.empty():
                one = self._lines_store.get()
                f.write('\t%s\n' % one)


class RequireStore(DataStore):
    u"""拦截request, 构建curl脚本, 并存储类.
    """

    _LOGIN_API = login_api
    _LOGOUT_API = logout_api

    def __init__(self, report_file, maxsize=0, cookie=None):
        super(RequireStore, self).__init__(report_file, maxsize)
        self.cookie = cookie

    def hold_data_require(self, request, request_url=None, data=None, frame='django'):
        """构建脚本, 生成curl 命令行.

            :param request:     请求对象.
            :param request_url: 请求地址.
            :param data:        请求数据.
            :param frame:       支持web框架.

            仅支持:
            method: GET/POST 其它如有需要待扩展.
            protocol: http/https 其它不考虑.
        """

        if frame == 'django':
            is_secure = request.is_secure()
            get_host = request.get_host()
            get_full_path = request.get_full_path()
        elif frame == 'tornado':
            is_secure = request.protocol == 'https'
            get_host = request.host
            get_full_path = request.path
        elif frame == 'pyramid':
            is_secure = request.scheme == 'https'
            get_host = request.host
            get_full_path = request.path
        else:
            is_secure = False
            get_host = ''
            get_full_path = ''

        line = 'curl '
        # 会话 cookies
        if self.cookie:
            # Fixed: -D and -b together error.
            if get_full_path in self._LOGIN_API + self._LOGOUT_API:
                line = ''.join((line, '-D %s ' % self.cookie))
            else:
                line = ''.join((line, '-b %s ' % self.cookie))

        # 构建方法和数据
        if request.method == 'POST' and data:
            line = ''.join((line, '-d \"%s\" ' % data))
        elif request.method == 'GET' and data:
            line = ''.join((line, '-G \"%s\" ' % data))
        else:
            pass

        # 构建请求地址
        if not request_url:
            protocol = 'http://' if not is_secure else 'https://'
            request_url = '%s%s%s' % (protocol, get_host, get_full_path)

        line = ''.join((line, request_url))
        return line


def sole_file_data(instance):
    u"""对拦截curl记录保存文件, 做处理去掉重复行.

        :param instance: DataStore实例.
    """

    lines = instance.open_file_data()
    if lines:
        sole_file = '%s_distinct%s' % os.path.splitext(instance.get_report_file())  # 去重后的记录文件
        if os.path.exists(sole_file):
            os.remove(sole_file)  # 删除之前生成文件

        log.debug('Original: %s' % len(lines))
        sole_data = set(lines)
        num_date = 0

        with open(sole_file, 'ab') as rf:
            log_time = '#### %s\n' % str(datetime.datetime.now())
            rf.write(log_time)

            for _line_ in sole_data:
                if _line_.startswith('####'):  # 取消原来日期分组
                    num_date += 1
                    continue
                rf.write(_line_)

        log.debug('Nowadays: %s' % (len(sole_data) - num_date))
        print('All is Ok')
    else:
        print('Data is None')


def main():
    """提供外部 entry points 而用.
    """

    parser = OptionParser()
    parser.add_option("-f", "--file", type="string",
                      dest="file",
                      default=None,
                      help="remove repeat lines in the script file.")

    (options, args) = parser.parse_args()
    if not options.file:
        parser.error("incorrect number of arguments")
        return

    _instance = RequireStore(report_file=options.file, maxsize=save_rows_queue, cookie='~/report/cookie.txt')
    sole_file_data(_instance)


if __name__ == '__main__':
    main()
