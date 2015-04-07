# !/usr/bin/env python
# -*- coding: utf-8 -*-

u"""读取存放测试脚本的文件, 以命令行的形式执行指定的行脚本, 指定范围的行脚本.

    利用 linux curl 构建测试脚本, 减少服务端开发过程中, 在测试上对客户端的依赖.
"""

from __future__ import print_function

import sys
import logging
import os.path
from optparse import OptionParser

if sys.version_info[0] == 3:
    range_ = range
else:
    range_ = xrange

log = logging.getLogger("hichao_test")
log.setLevel(logging.DEBUG)


class ScriptExecute(object):
    u"""读取测试脚本, 执行行脚本, 指定范围的行脚本
    """

    def __init__(self, script_file, report_bool=True, lazy_bone=None):
        """
            :param script_file:
            :param report_bool:
            :param lazy_bone:
        """

        super(ScriptExecute, self).__init__()
        self.script_file = script_file
        self.script_lines = self.__read_script_file()

        self.lazy_bone = lazy_bone
        self.report_bool = report_bool  # 是否生成报告文件
        self.log_file_name = None

    def __path_result_file(self):
        u"""生成日志的目录及文件形式.
        """

        # noinspection PyUnresolvedReferences
        result_logs = os.path.join(os.path.dirname(self.script_file), r'log')  # 默认报告目录

        if not os.path.exists(result_logs):
            os.makedirs(result_logs)

        if not self.log_file_name:
            # noinspection PyUnresolvedReferences
            log_file_name = os.path.join(result_logs, u'curl_%s.htm')

            self.log_file_name = log_file_name

        return self.log_file_name

    def __read_script_file(self):
        u"""读取测试脚本文件内容.
        """

        lines = None
        if os.path.exists(self.script_file):

            if os.path.ismount(self.script_file) or os.path.isdir(self.script_file):
                log.error(u'亲, 指定的存储路径错误！')
                return

            script_log_file = open(self.script_file, 'rb')
            lines = script_log_file.readlines()
        else:
            log.error(u'测试脚本, 指定的文件不存在.')

        if not lines:
            log.error(u'测试脚本, 指定的文件内容为空.')

        return lines

    def __loop_line(self, num):
        u"""运行行列表里指定的行.

            :param num: 行号
        """

        log_name = self.__path_result_file() % num
        if num > 0:
            num -= 1  # 文档行标, 实例索引起点不一

        line = self.script_lines[num].strip().replace("\n", "")

        log.debug(line)
        log.debug(line.startswith('curl'))

        if line.startswith('curl'):
            if self.lazy_bone:
                line = self.lazy_bone.process_regular(line)

            log.debug(90 * '=')
            log.debug(line.split()[-1])

            if self.report_bool:
                os.system('%s > %s' % (line, log_name))
            else:
                os.system('%s' % line)

    def run_script_lines(self, start=0, count=0):
        u"""运行指定行范围脚本.

            :param start: 起始行号 整数
            :param count: 后面行数 正整数
        """

        if self.script_lines:
            if len(self.script_lines) >= abs(start):
                if count == 0:
                    self.__loop_line(start)
                else:
                    for i in range_(start, start + count):
                        if i == len(self.script_lines):
                            break

                        self.__loop_line(i)


class LazyBone(object):
    u"""处理某些正则表达式, 懒人而已.
    """

    def __init__(self, regulars, exam_ids):
        """
            :param regulars: 要替换的表达式
            :param exam_ids: 被替换为的值
        """

        # [r'(?P<user_id>\d+)', r'(?P<tip_id>\d+)', r'(?P<place_id>\d+)']  # 三者不会同时存在
        # ['624', '26774', '1294']  # 待用于测试的实例依次ID

        self.regulars = regulars
        self.exam_ids = exam_ids

    def process_regular(self, line):
        u"""处理某些正则表达式.

            :param line: 行内容
        """

        for i in range_(len(self.regulars)):
            if line.find(self.regulars[i]) < 0:
                continue

            line = line.replace(self.regulars[i], self.exam_ids[i])
            break

        return line


def main():
    """提供外部 entry points 而用.
    """

    parser = OptionParser()
    parser.add_option("-f", "--file", type="string",
                      dest="file_name",
                      default=None,
                      help="data from script file")
    parser.add_option("-n", "--num", type="int",
                      dest="line_num",
                      default=-1,
                      help="line number in script file")

    parser.add_option("-c", "--count", type="int",
                      dest="line_count",
                      default=0,
                      help="next lines count ")

    (options, args) = parser.parse_args()
    if len(args) != 1:
        parser.error("incorrect number of arguments")

    if not options.file_name:
        return

    _curl_script = ScriptExecute(options.file_name)
    _curl_script.run_script_lines(options.line_num, options.line_count)


if __name__ == '__main__':
    main()
