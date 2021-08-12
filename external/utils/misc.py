# coding: utf-8
import inspect
import logging
import random
import re
import threading
import weakref
from functools import wraps

import requests
from requests.adapters import HTTPAdapter

from external.utils import ResponseError


def check_response_body(response_body):
    """
    检查 response body: err_code 不为 0 时抛出 :class:`ResponseError` 异常

    :param response_body: response body
    """

    try:
        base_response = response_body['BaseResponse']
        err_code = base_response['Ret']
        err_msg = base_response['ErrMsg']
    except (KeyError, TypeError):
        pass
    else:
        if err_code != 0:
            if int(err_code) > 0:
                err_msg = err_msg
            raise ResponseError(err_code=err_code, err_msg=err_msg)


def ensure_list(x, except_false=True):
    """
    若传入的对象不为列表，则转化为列表

    :param x: 输入对象
    :param except_false: None, False 等例外，会直接返回原值
    :return: 列表，或 None, False 等
    :rtype: list
    """

    if isinstance(x, (list, tuple)) or (not x and except_false):
        return x
    return [x]


def prepare_keywords(keywords):
    """
    准备关键词
    """

    if not keywords:
        keywords = ''
    if isinstance(keywords, str):
        # noinspection PyTypeChecker
        keywords = re.split(r'\s+', keywords)
    return map(lambda x: x.lower(), keywords)


def match_text(text, keywords):
    """
    判断文本内容中是否包含了所有的关键词 (不区分大小写)

    :param text: 文本内容
    :param keywords: 关键词，可以是空白分割的 str，或是多个精准关键词组成的 list
    :return: 若包含了所有的关键词则为 True，否则为 False
    """

    if not text:
        text = ''
    else:
        text = text.lower()

    keywords = prepare_keywords(keywords)

    for kw in keywords:
        if kw not in text:
            return False
    return True


def match_attributes(obj, **attributes):
    """
    判断对象是否匹配输入的属性条件

    :param obj: 对象
    :param attributes: 属性键值对
    :return: 若匹配则为 True，否则为 False
    """

    has_raw = hasattr(obj, 'raw')

    for attr, value in attributes.items():
        if (getattr(obj, attr, None) or (obj.raw.get(attr) if has_raw else None)) != value:
            return False
    return True


def match_name(chat, keywords):
    """
    判断一个 Chat 对象的名称是否包含了所有的关键词 (不区分大小写)

    :param chat: Chat 对象
    :param keywords: 关键词，可以是空白分割的 str，或是多个精准关键词组成的 list
    :return: 若包含了所有的关键词则为 True，否则为 False
    """
    keywords = prepare_keywords(keywords)

    for kw in keywords:
        for attr in 'remark_name', 'display_name', 'nick_name', 'wxid':
            if kw in '{0}'.format(getattr(chat, attr, '')).lower():
                break
        else:
            return False
    return True


def smart_map(func, i, *args, **kwargs):
    """
    将单个对象或列表中的每个项传入给定的函数，并返回单个结果或列表结果，类似于 map 函数

    :param func: 传入到的函数
    :param i: 列表或单个对象
    :param args: func 函数所需的 args
    :param kwargs: func 函数所需的 kwargs
    :return: 若传入的为列表，则以列表返回每个结果，反之为单个结果
    """
    if isinstance(i, (list, tuple, set)):
        return list(map(lambda x: func(x, *args, **kwargs), i))
    else:
        return func(i, *args, **kwargs)


def enhance_connection(session, pool_connections=30, pool_maxsize=30, max_retries=2):
    """
    增强 requests.Session 对象的网络连接性能

    :param session: 需增强的 requests.Session 对象
    :param pool_connections: 最大的连接池缓存数量
    :param pool_maxsize: 连接池中的最大连接保存数量
    :param max_retries: 最大的连接重试次数 (仅处理 DNS 查询, socket 连接，以及连接超时)
    """

    for p in 'http', 'https':
        session.mount(
            '{}://'.format(p),
            HTTPAdapter(
                pool_connections=pool_connections,
                pool_maxsize=pool_maxsize,
                max_retries=max_retries,
                pool_block=False
            ))


def enhance_webwx_request(bot, sync_check_timeout=(10, 30), webwx_sync_timeout=(10, 20)):
    """
    针对 Web 微信增强机器人的网络请求

    :param bot: 需优化的机器人实例
    :param sync_check_timeout: 请求 "synccheck" 时的超时秒数
    :param webwx_sync_timeout: 请求 "webwxsync" 时的超时秒数
    """

    login_info = bot.core.loginInfo
    session = bot.core.s

    # get: 用于检查是否有新消息
    sync_check_url = '{}/synccheck'.format(login_info.get('syncUrl', login_info['url']))

    # post: 用于获取消息和更新联系人
    webwx_sync_url = '{li[url]}/webwxsync?sid={li[wxsid]}&skey={li[skey]}' \
                     '&pass_ticket={li[pass_ticket]}'.format(li=login_info)

    # noinspection PyProtectedMember
    def customized_request(method, url, **kwargs):
        """
        根据 请求方法 和 url 灵活调整各种参数
        """

        if method.upper() == 'GET':
            if url == sync_check_url:
                # 设置一个超时，避免无尽等待而停止发送心跳，导致出现 1101 错误
                kwargs['timeout'] = sync_check_timeout

                # deviceid 应每次都变化，否则会导致该连接断开不及时，接收消息变慢
                kwargs['params']['deviceid'] = 'e{}'.format(str(random.random())[2:17])

                bot._sync_check_iterations += 1
                kwargs['params']['_'] = bot._sync_check_iterations

        elif method.upper() == 'POST':
            if url == webwx_sync_url:
                # 同上方设置超时
                kwargs['timeout'] = webwx_sync_timeout

        return requests.Session.request(session, method, url, **kwargs)

    session.request = customized_request
