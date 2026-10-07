#!/usr/bin/env python

"""读取存放测试脚本的文件, 以命令行的形式执行指定的行脚本, 指定范围的行脚本.

    利用 linux curl 构建测试脚本, 减少服务端开发过程中, 在测试上对客户端的依赖.
"""

import argparse
import re
import shlex
import subprocess

import os.path
from hichao_test.conf import log, lazy_bone_list


def _mask_sensitive(line):
    """脱敏 curl 命令中的 -d/-G 数据, 避免日志泄露密码等."""

    return re.sub(r'(-[dG]\s+")[^"]*(")', r'\1***\2', line)


class ScriptExecute:
    """读取测试脚本, 执行行脚本, 指定范围的行脚本
    """

    def __init__(self, script_file, report_bool=True, lazy_bone=None):
        """
            :param script_file: CURL脚本存储文件.
            :param report_bool: 是否生成报告文件.
            :param lazy_bone:   替换URL正则表达式中(GET)参数值.
        """

        super().__init__()
        self.script_file = script_file
        self.script_lines = self.__read_script_file()

        self.lazy_bone = lazy_bone
        self.report_bool = report_bool  # 是否生成报告文件
        self.log_file_name = None

    def __path_result_file(self):
        """生成日志的目录及文件形式.
        """

        # noinspection PyUnresolvedReferences
        result_logs = os.path.join(os.path.dirname(self.script_file),
                                   r'log')  # 默认报告目录

        if not os.path.exists(result_logs):
            os.makedirs(result_logs)

        if not self.log_file_name:
            # noinspection PyUnresolvedReferences
            log_file_name = os.path.join(result_logs, 'curl_%s.htm')

            self.log_file_name = log_file_name

        return self.log_file_name

    def __read_script_file(self):
        """读取测试脚本文件内容.
        """

        if os.path.exists(self.script_file):
            if os.path.ismount(self.script_file) or os.path.isdir(
                    self.script_file):
                raise ValueError(
                    "specified path is a directory or mount point: %s"
                    % self.script_file)

            with open(self.script_file, 'r', encoding='utf-8') as script_log_file:
                lines = script_log_file.readlines()
        else:
            raise FileNotFoundError(
                "specified script file does not exist: %s" % self.script_file)

        if not lines:
            log.error("specified script file content is empty.")

        return lines

    def __loop_line(self, num):
        """运行行列表里指定的行.

            :param num: 行编号, 正整数.
        """

        if num < 1:
            raise ValueError("num参数必须是正整数.")
        if num > len(self.script_lines):
            raise IndexError("num参数超出脚本总行数 %d." % len(
                self.script_lines))
        num -= 1  # 文档行标, 实例索引起点不一

        line = self.script_lines[num].strip()
        # log.debug(line.startswith('curl'))

        if line.startswith('curl'):
            if self.lazy_bone:
                line = self.lazy_bone.process_regular(line)

            log.debug(_mask_sensitive(line))
            parts = line.split()
            if parts:
                log.debug(parts[-1])

            try:
                if self.report_bool:
                    log_name = self.__path_result_file() % (num + 1)
                    with open(log_name, 'w', encoding='utf-8') as out:
                        subprocess.run(shlex.split(line), stdout=out,
                                       timeout=60, check=False)
                else:
                    subprocess.run(shlex.split(line), timeout=60, check=False)
            except (ValueError, subprocess.TimeoutExpired) as e:
                # 单行失败(引号不配对/超时等)不影响后续行执行
                log.error("line %d execute failed: %s", num + 1, e)

            log.debug('-*' * 50)

    def run_script_lines(self, start=1, count=0):
        """运行指定行范围脚本.

            :param start: 起始行编号, 正整数.
            :param count: 后面行数, 正负整数.
        """

        if start < 1:
            raise ValueError("start参数必须是正整数.")

        if self.script_lines:
            total = len(self.script_lines)
            if total < start:
                raise ValueError("start参数超出脚本总行数 %d." % total)

            if count == 0:
                self.__loop_line(start)
            else:
                step = 1 if count > 0 else -1
                # 末端行号预校验, 避免半途崩溃导致部分执行
                end = start + count - step
                if end < 1 or end > total:
                    raise ValueError(
                        "count参数导致行号 %d 超出有效范围 [1, %d]."
                        % (end, total))

                data_range = range(start, start + count, step)
                for i in data_range:
                    self.__loop_line(i)

    def run_script_total(self):
        """运行所有记录.
        """

        if self.script_lines:
            data_range = range(1, len(self.script_lines) + 1)
            for i in data_range:
                self.__loop_line(i)


class LazyBone:
    r"""替换脚本行中的占位文本, 懒人而已.

        注意: 做的是字面替换而非正则匹配. 典型场景是脚本中保存了
        Django URLconf 形式的占位符(如 /user/(?P<user_id>\d+)/),
        执行前将其字面替换为实际的 id.
    """

    def __init__(self, _lazy_bone_list=None):
        """
            :param _lazy_bone_list: (要替换的字面文本, 被替换为的值).
        """

        self._lazy_bone_list = _lazy_bone_list or []

    def process_regular(self, line):
        """字面替换行内容中的占位文本, 命中第一条规则即返回.

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

    parser = argparse.ArgumentParser(
        description='execute curl script lines from the stored file.')
    parser.add_argument('-f', '--file', dest='file', default=None,
                        help='store the curl script data file.')
    parser.add_argument('-n', '--num', type=int, dest='num', default=None,
                        help='execute the script line number specified.')
    parser.add_argument('-c', '--count', type=int, dest='count', default=0,
                        help='perform the following line count.')

    options = parser.parse_args()
    log.debug("options:%s\n" % options)

    if not options.file:
        parser.error("specified file required parameters are missing.")

    file_name = options.file
    lazy_bone = LazyBone(lazy_bone_list) if lazy_bone_list else None
    _curl_script = ScriptExecute(file_name, report_bool=True,
                                 lazy_bone=lazy_bone)

    if options.num is None:
        _curl_script.run_script_total()
    else:
        line_num = options.num
        line_count = options.count
        _curl_script.run_script_lines(line_num, line_count)


if __name__ == '__main__':
    main()
