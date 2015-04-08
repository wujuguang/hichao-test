# !/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import os.path

log = logging.getLogger("ky_hichao")
log.setLevel(logging.DEBUG)

login_api = ('/user/login/', '/user/join/',)
logout_api = ('/user/logout/',)

# 是否保存请求痕迹
post_data_saved = True

# 队列满多少条保存
save_rows_queue = 15

# 拦截生成curl保存文件
# noinspection PyUnresolvedReferences
curl_report = os.path.join('~', 'report', r'report_curl.md')
