# !/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals, print_function

import sys
import time
import traceback
from functools import wraps

from hichao_test.conf import log, exec_time_print, post_data_saved, save_rows_queue, time_report, curl_report
from hichao_test.curl_builder import DataStore, RequireStore

time_instance = DataStore(report_file=time_report, maxsize=save_rows_queue)
cur_instance = RequireStore(report_file=curl_report, maxsize=save_rows_queue, cookie='~/report/cookie.txt')


class Timer(object):
    u"""Computer program exec time."""

    def __init__(self, verbose=False):
        self.verbose = verbose

    def __enter__(self):
        self.start = time.time()
        return self

    def __exit__(self, *args, **kwargs):
        self.end = time.time()
        self.secs = self.end - self.start
        self.seconds = self.secs * 1000
        if self.verbose:
            print('elapsed time: %f ms' % self.seconds)


def request_process(request, frame='django'):
    u"""输出并记录 request post(dict) 传入值.
        捕获和验证参数以供 curl 再使用, 验证从 curl 传来值.
    """
    req_method = request.method
    if frame == 'django':
        is_secure = request.is_secure()
        req_dict = request.POST if req_method == "POST" else request.GET
        get_host = request.get_host()
        get_full_path = request.get_full_path()
    elif frame == 'tornado':
        is_secure = request.protocol == 'https'
        req_dict = request.arguments
        get_host = request.host
        get_full_path = request.path
    elif frame == 'pyramid':
        is_secure = request.scheme == 'https'
        req_dict = request.POST if req_method == "POST" else request.GET
        get_host = request.host
        get_full_path = request.path
    else:
        is_secure = False
        req_dict = {}
        get_host = ''
        get_full_path = ''

    str_post = ''
    protocol = 'http://' if not is_secure else 'https://'
    request_url = '%s%s%s' % (protocol, get_host, get_full_path)

    # 输出传入值开始
    log.debug('URL: %s' % request_url)

    if len(req_dict) > 0:
        log.debug(req_dict)
        for (key, value) in req_dict.items():
            str_post = '&'.join((str_post, '%s=%s' % (key, value)))
        str_post = str_post.strip('&')
        log.debug('Data String: %s' % str_post)
        log.debug('-*' * 50)

    if req_method == "POST" and post_data_saved and str_post:
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

            # 计算后端程序执行时间
            if exec_time_print:
                with Timer() as t:
                    response = func(request, *args, **kwargs)

                now_time = time.time()
                log.debug("%s => %s ms" % (func.__name__, t.seconds))
                line = "%-25s at %.2f %s => %s ms\n" % (func.__name__, now_time, 8 * ' ', t.seconds)
                time_instance.save_line_data(line)
            else:
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

            # 计算后端程序执行时间
            if exec_time_print:
                with Timer() as t:
                    response = func(self, *args, **kwargs)

                now_time = time.time()
                log.debug("%s => %s ms" % (func.__name__, t.seconds))
                line = "%-25s at %.2f %s => %s ms\n" % (func.__name__, now_time, 8 * ' ', t.seconds)
                time_instance.save_line_data(line)
            else:
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
