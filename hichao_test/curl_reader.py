# !/usr/bin/env python
# -*- coding: utf-8 -*-

u"""读取存放测试脚本的文件, 以命令行的形式执行指定的行脚本, 指定范围的行脚本.

    利用 linux curl 构建测试脚本, 减少服务端开发过程中, 在测试上对客户端的依赖.
"""

from __future__ import unicode_literals, print_function

import sys
import os.path
from optparse import OptionParser
from hichao_test.conf import log

if sys.version_info[0] == 3:
    range_ = range
else:
    range_ = xrange


class ScriptExecute(object):
    u"""读取测试脚本, 执行行脚本, 指定范围的行脚本
    """

    def __init__(self, script_file, report_bool=True, lazy_bone=None):
        """
            :param script_file: CURL脚本存储文件.
            :param report_bool: 是否生成报告文件.
            :param lazy_bone:   替换URL正则表达式中(GET)参数值.
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

        if os.path.exists(self.script_file):
            if os.path.ismount(self.script_file) or os.path.isdir(self.script_file):
                log.error("oh, specify the path error.")  # u'亲, 指定的存储路径错误！'
                return

            script_log_file = open(self.script_file, 'rb')
            lines = script_log_file.readlines()
        else:
            log.error("specified script file does not exist.")  # u'测试脚本, 指定的文件不存在.'
            return

        if not lines:
            log.error("specified script file content is empty.")  # u'测试脚本, 指定的文件内容为空.'

        return lines

    def __loop_line(self, num):
        u"""运行行列表里指定的行.

            :param num: 行编号, 正整数.
        """

        log_name = self.__path_result_file() % num
        if num > 0:
            num -= 1  # 文档行标, 实例索引起点不一
        else:
            raise Exception("num参数必须是正整数.")

        line = self.script_lines[num].strip().replace("\n", "")
        # log.debug(line.startswith('curl'))

        if line.startswith('curl'):
            if self.lazy_bone:
                line = self.lazy_bone.process_regular(line)

            log.debug(line)
            log.debug(line.split()[-1])

            if self.report_bool:
                os.system('%s > %s' % (line, log_name))
            else:
                os.system('%s' % line)

            log.debug('-*' * 50)

    def run_script_lines(self, start=1, count=0):
        u"""运行指定行范围脚本.

            :param start: 起始行编号, 正整数.
            :param count: 后面行数, 正负整数.
        """

        if self.script_lines:
            if len(self.script_lines) >= abs(start):
                if count == 0:
                    self.__loop_line(start)
                else:
                    data_range = range_(start, start + count) if count > 0 else range_(start, start + count, -1)
                    for i in data_range:
                        self.__loop_line(i)

    def run_script_total(self):
        """运行所有记录.
        """

        if self.script_lines:
            data_range = range_(1, len(self.script_lines) + 1)
            for i in data_range:
                self.__loop_line(i)


class LazyBone(object):
    u"""处理某些正则表达式, 懒人而已.
    """

    def __init__(self, _lazy_bone_list=None):
        """
            :param _lazy_bone_list: (要替换的表达式, 被替换为的值).
        """

        self._lazy_bone_list = _lazy_bone_list

    def process_regular(self, line):
        u"""处理某些正则表达式.

            :param line: 行内容
        """

        for (regular, exam_id) in self._lazy_bone_list:
            if line.find(regular) < 0:
                continue

            line = line.replace(regular, exam_id)
            break

        return line


def main():
    """提供外部 entry points 而用.
    """

    parser = OptionParser()
    parser.add_option("-f", "--file",
                      type="string",
                      dest="file",
                      help="store the curl script data file.")

    parser.add_option("-n", "--num",
                      type="int",
                      dest="num",
                      default=None,
                      help="execute the script line number specified.")

    parser.add_option("-c", "--count",
                      type="int",
                      dest="count",
                      default=0,
                      help="perform the following line count.")

    (options, args) = parser.parse_args()
    log.debug("options:%s\n" % options)

    if not options.file:
        log.error("specified file required parameters are missing.")
        return

    file_name = options.file
    _curl_script = ScriptExecute(file_name, report_bool=True, lazy_bone=None)

    if options.num is None:
        _curl_script.run_script_total()
    else:
        line_num = options.num
        line_count = options.count
        _curl_script.run_script_lines(line_num, line_count)


if __name__ == '__main__':
    main()
