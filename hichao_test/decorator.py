# !/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals, print_function

import sys
import traceback
from functools import wraps
from hichao_test.conf import log, post_data_saved, save_rows_queue, curl_report
from hichao_test.curl_builder import RequireStore

cur_instance = RequireStore(report_file=curl_report, maxsize=save_rows_queue, cookie='~/report/cookie.txt')


def request_process(request, frame='django'):
    u"""输出并记录 request post(dict) 传入值.
        捕获和验证参数以供 curl 再使用, 验证从 curl 传来值.
    """

    if frame == 'django':
        is_secure = request.is_secure()
        post_dict = request.POST
        get_host = request.get_host()
        get_full_path = request.get_full_path()
    elif frame == 'tornado':
        is_secure = request.protocol == 'https'
        post_dict = request.arguments
        get_host = request.host
        get_full_path = request.path
    elif frame == 'pyramid':
        is_secure = request.scheme == 'https'
        post_dict = request.POST
        get_host = request.host
        get_full_path = request.path
    else:
        is_secure = False
        post_dict = {}
        get_host = ''
        get_full_path = ''

    str_post = ''
    protocol = 'http://' if not is_secure else 'https://'
    request_url = '%s%s%s' % (protocol, get_host, get_full_path)

    # 输出传入值开始
    log.debug('URL: %s' % request_url)

    if len(post_dict) > 0:
        log.debug(post_dict)
        for (key, value) in post_dict.items():
            str_post = '&'.join((str_post, '%s=%s' % (key, value)))
        str_post = str_post.strip('&')
        log.debug('Data String: %s' % str_post)
        log.debug('-*' * 50)

    if post_data_saved and str_post:
        # 记录传入值
        line = cur_instance.hold_data_require(
            request, request_url=request_url, data=str_post, frame=frame)
        cur_instance.save_line_data(line)


def frame_request(frame, func=None):
    u"""测试request函数, 并输出信息.

        :param func: view 函数
    """

    @wraps(func)
    def returned_wrapper(request, *args, **kwargs):
        try:
            # 查看并控制台核实传入数据
            request_process(request, frame)
            response = func(request, *args, **kwargs)
            return response

        except Exception as e:
            # 异常时保存下数据
            cur_instance.save_file_data()

            log.exception(e)
            traceback.print_exc(file=sys.stdout)

    return returned_wrapper


def django_request(func=None):
    u"""测试request函数, 并输出信息.

        :param func: view 函数
    """

    return frame_request('django', func)


def tornado_request(func=None):
    """测试request函数, 打印出异常信息.
    """

    @wraps(func)
    def returned_wrapper(self, *args, **kwargs):
        try:
            # 查看并控制台核实传入数据
            request_process(self.request, 'tornado')
            response = func(self, *args, **kwargs)
            return response

        except Exception as e:
            # 异常时保存下数据
            cur_instance.save_file_data()

            log.exception(e)
            traceback.print_exc(file=sys.stdout)

    return returned_wrapper


def pyramid_request(func=None):
    """测试request函数, 打印出异常信息.
    """

    return frame_request('pyramid', func)
