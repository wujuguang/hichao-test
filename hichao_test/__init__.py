#!/usr/bin/env python

import importlib

__all__ = ("django_request", 'tornado_request', "pyramid_request",
           "ScriptExecute", "LazyBone", "DataStore", "RequireStore")

_LAZY_IMPORTS = {
    "django_request": "hichao_test.decorator",
    "tornado_request": "hichao_test.decorator",
    "pyramid_request": "hichao_test.decorator",
    "ScriptExecute": "hichao_test.curl_reader",
    "LazyBone": "hichao_test.curl_reader",
    "DataStore": "hichao_test.curl_builder",
    "RequireStore": "hichao_test.curl_builder",
}


def __getattr__(name):
    """PEP 562 lazy import: 首次访问时才加载子模块.
    """

    module_name = _LAZY_IMPORTS.get(name)
    if module_name is None:
        raise AttributeError(
            "module %r has no attribute %r" % (__name__, name))

    value = getattr(importlib.import_module(module_name), name)
    globals()[name] = value  # 缓存, 后续访问走模块正常属性
    return value


def __dir__():
    return sorted(__all__)
