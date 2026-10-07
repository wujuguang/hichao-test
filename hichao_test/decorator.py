#!/usr/bin/env python

import sys
import time
import traceback
from functools import wraps
from urllib.parse import quote_plus

from hichao_test.conf import (log, exec_time_print, post_data_saved,
                              save_rows_queue, time_report, curl_report)
from hichao_test.curl_builder import DataStore, RequireStore

_time_instance = None
_cur_instance = None


def get_time_instance():
    """延迟创建, 避免 import 时创建目录等副作用.
    """

    global _time_instance
    if _time_instance is None:
        _time_instance = DataStore(report_file=time_report,
                                   maxsize=save_rows_queue)
    return _time_instance


def get_cur_instance():
    """延迟创建, 避免 import 时创建目录等副作用.
    """

    global _cur_instance
    if _cur_instance is None:
        _cur_instance = RequireStore(report_file=curl_report,
                                     maxsize=save_rows_queue,
                                     cookie='~/report/cookie.txt')
    return _cur_instance


class Timer:
    """Computer program exec time."""

    def __init__(self, verbose=False):
        self.verbose = verbose

    def __enter__(self):
        self.start = time.time()
        return self

    def __exit__(self, *args, **kwargs):
        self.end = time.time()
        self.seconds = self.end - self.start
        self.millisecond = self.seconds * 1000
        if self.verbose:
            print('elapsed time: %f ms' % self.millisecond)


def request_process(request, frame='django'):
    """输出并记录 request post(dict) 传入值.
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
        pairs = []
        for (key, value) in req_dict.items():
            pairs.append('%s=%s' % (quote_plus(str(key)),
                                    quote_plus(str(value))))
        str_post = '&'.join(pairs)
        log.debug('Data String: %s' % str_post)
        log.debug('-*' * 50)

    if req_method == "POST" and post_data_saved and str_post:
        # 记录传入值
        cur_instance = get_cur_instance()
        line = cur_instance.hold_data_require(
            request, request_url=request_url, data=str_post, frame=frame)
        cur_instance.save_line_data(line)

    return get_full_path


def frame_request(frame, func=None):
    """测试request函数, 并输出信息.

        :param frame: 框架 名称
        :param func: view 函数
    """

    if func is None:
        return lambda f: frame_request(frame, f)

    @wraps(func)
    def returned_wrapper(request, *args, **kwargs):
        try:
            # 查看并控制台核实传入数据
            full_path = request_process(request, frame)

            # 计算后端程序执行时间
            if exec_time_print:
                with Timer() as t:
                    response = func(request, *args, **kwargs)

                log.debug("%s => %s ms" % (full_path, t.millisecond))
                line = "%-25s %s => %s ms\n" % (
                    full_path, 8 * ' ', t.millisecond)
                get_time_instance().save_line_data(line)
            else:
                response = func(request, *args, **kwargs)
            return response

        except Exception as e:
            # 异常时保存下数据
            get_cur_instance().save_file_data()

            log.exception(e)
            traceback.print_exc(file=sys.stdout)
            raise

    return returned_wrapper


def django_request(func=None):
    """测试request函数, 并输出信息.

        :param func: view 函数
    """

    return frame_request('django', func)


def tornado_request(func=None):
    """测试request函数, 打印出异常信息.
    """

    if func is None:
        return tornado_request

    @wraps(func)
    def returned_wrapper(self, *args, **kwargs):
        try:
            # 查看并控制台核实传入数据
            full_path = request_process(self.request, 'tornado')

            # 计算后端程序执行时间
            if exec_time_print:
                with Timer() as t:
                    response = func(self, *args, **kwargs)

                log.debug("%s => %s ms" % (full_path, t.millisecond))
                line = "%-25s %s => %s ms\n" % (
                    full_path, 8 * ' ', t.millisecond)
                get_time_instance().save_line_data(line)
            else:
                response = func(self, *args, **kwargs)
            return response

        except Exception as e:
            # 异常时保存下数据
            get_cur_instance().save_file_data()

            log.exception(e)
            traceback.print_exc(file=sys.stdout)
            raise

    return returned_wrapper


def pyramid_request(func=None):
    """测试request函数, 打印出异常信息.
    """

    return frame_request('pyramid', func)
