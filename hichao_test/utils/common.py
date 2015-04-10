#!usr/bin/env python
# coding: utf-8

from __future__ import unicode_literals, print_function

import sys
import inspect


def get_subclass_iter(_name, _base_class):
    """获取指定模块下, 指定类的所有子类.

        :param _name:       指定模块.
        :param _base_class: 指定(父)类.
    """

    for name, obj in inspect.getmembers(sys.modules[_name]):
        if inspect.isclass(obj) and issubclass(obj, _base_class) and obj != _base_class:
            yield obj


def get_method_iter(_sub_class):
    """获取指定子类的方法.

        :param _sub_class: 指定子类.
    """

    print(_sub_class)

    pass


def get_method_type(_method):
    """获取指定方法Get/Post类型.

        :param _method: 指定子类.
    """

    print(_method)

    pass
