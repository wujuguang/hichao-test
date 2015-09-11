# !/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import os.path

logging.basicConfig()

log = logging.getLogger("hichao")
log.setLevel(logging.DEBUG)

login_api = ('/user/login/', '/user/join/',)
logout_api = ('/user/logout/',)

# 是否输出执行时间
exec_time_print = True

# 是否保存请求痕迹
post_data_saved = True

# 队列满多少条保存
save_rows_queue = 1  # 15

# 接口执行时间保存文件
time_report = os.path.join(os.path.expanduser('~'), 'report', r'report_time.md')

# 拦截生成curl保存文件
# noinspection PyUnresolvedReferences
curl_report = os.path.join(os.path.expanduser('~'), 'report', r'report_curl.md')

# 处理某些正则表达式, LazyBone实例化使用
lazy_bone_list = (
    # (r'(?P<user_id>\d+)', '624'),
    # (r'(?P<tip_id>\d+)', '26774'),
    # (r'(?P<place_id>\d+)', '1294')
)
