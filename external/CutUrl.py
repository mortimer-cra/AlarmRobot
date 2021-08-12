#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @File  : CutUrl.py
# @Author: Administrator
# @Date  : 2020/2/17
import logging
import requests
from external.utils.misc import enhance_connection

logger = logging.getLogger(__name__)

url_dict = {}


class CutUrl(object):
    alapi_url = 'http://v1.alapi.cn/api/url'
    uomg_url = 'https://api.uomg.com/api/long2dwz'

    def __init__(self):
        self.session = requests.Session()
        enhance_connection(self.session)

    def get(self, url):
        re_url = self.get_alapi(url)
        if not re_url:
            re_url = self.get_uomg(url)
        return re_url

    def get_cache(self, url):
        # 先找下有没有缓存
        if url in url_dict:
            return url_dict.get(url)
        re_url = self.get_alapi(url)
        # 试一下别的
        if not re_url:
            re_url = self.get_uomg(url)
        # 缓存一下
        if re_url:
            url_dict[url] = re_url
        return re_url

    def get_uomg(self, url):
        payload = dict(
            url=url,
            dwzapi='tcn'
        )
        try:
            r = self.session.get(self.uomg_url, params=payload)
            answer = r.json()
            if answer:
                if answer.get('code') == 1:
                    return answer.get('ae_url')
            return None
        except Exception as e:
            logging.error(str(e))
            return None

    def get_alapi(self, url):
        payload = dict(
            url=url,
            type=1
        )
        try:
            r = self.session.get(self.alapi_url, params=payload)
            answer = r.json()
            if answer:
                if answer.get('code') == 200:
                    return answer.get('data').get('short_url')
            return None
        except Exception as e:
            logging.error(str(e))
            return None


if __name__ == '__main__':
    get = CutUrl().get('https://www.baidu.com/')
    print(get)
