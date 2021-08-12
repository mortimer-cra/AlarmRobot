#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @File  : DoubanSpider.py
# @Author: Administrator
# @Date  : 2020/3/2
import requests
import random
from db.DoubanSet import DoubanSet

# 浏览器请求头
agents = [
    # Firefox
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:34.0) Gecko/20100101 Firefox/34.0",
    "Mozilla/5.0 (X11; U; Linux x86_64; zh-CN; rv:1.9.2.10) Gecko/20100922 Ubuntu/10.10 (maverick) Firefox/3.6.10",
    # chrome
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11",
    "Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/534.16 (KHTML, like Gecko) Chrome/10.0.648.133 Safari/534.16",
    # UC浏览器
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.122 UBrowser/4.0.3214.0 Safari/537.36",
    # IPhone
    "Mozilla/5.0 (iPhone; U; CPU iPhone OS 4_3_3 like Mac OS X; en-us) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8J2 Safari/6533.18.5",
    # IPod
    "Mozilla/5.0 (iPod; U; CPU iPhone OS 4_3_3 like Mac OS X; en-us) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8J2 Safari/6533.18.5",
    # IPAD
    "Mozilla/5.0 (iPad; U; CPU OS 4_2_1 like Mac OS X; zh-cn) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8C148 Safari/6533.18.5",
    "Mozilla/5.0 (iPad; U; CPU OS 4_3_3 like Mac OS X; en-us) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8J2 Safari/6533.18.5",
    # Android
    "Mozilla/5.0 (Linux; U; Android 2.2.1; zh-cn; HTC_Wildfire_A3333 Build/FRG83D) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1",
    "Mozilla/5.0 (Linux; U; Android 2.3.7; en-us; Nexus One Build/FRF91) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1"
]

headers = {
    # 随机取请求头
    "User-Agent": random.choice(agents),
    "Origin": "https://movie.douban.com",
    "Referer": "https://movie.douban.com"
}


# 登录返回cookie
def login(url, user, password):
    # 登录
    req_headers = {
        'User-Agent': "Mozilla/5.0 (X11; U; Linux x86_64; zh-CN; rv:1.9.2.10) Gecko/"
                      "20100922 Ubuntu/10.10 (maverick) Firefox/3.6.10"
    }

    req_data = {
        'ck': '',
        'ticket': '',
        'name': user,
        'password': password,
        'remember': False
    }

    # 使用Session post数据
    session = requests.Session()
    resp = session.post(url, data=req_data, headers=req_headers)
    print(resp.cookies.get_dict())  # cookies内容
    temp = session.cookies;
    session.close();  # 避免没必要的开销
    return temp;


def getNewList(soup_nowplayings):
    infoc_ = []

    hots = soup_nowplayings['subjects']
    for num in range(len(hots)):
        info = {}
        temp = hots[num]
        info['id'] = temp['id']
        info['title'] = temp['title']
        info['rate'] = temp['rate']
        info['url'] = temp['url']
        info['cover'] = temp['cover']
        info['is_new'] = temp['is_new']
        infoc_.append(info)
    return infoc_


def douban_spider():
    try:
        print('开始豆瓣爬取...')
        # login to douban 报错会等待,然后重新登录获取
        # news = "https://movie.douban.com/explore#!type=movie&tag=%E6%9C%80%E6%96%B0&page_limit=20&page_start=0"
        news = "https://movie.douban.com/j/search_subjects?type=movie&tag=%E6%9C%80%E6%96%B0&page_limit=20&page_start=0"

        # soup_news = requests.get(url=news, headers=headers, cookies=cookie).json()
        soup_news = requests.get(url=news, headers=headers).json()
        data_news = getNewList(soup_news)
        for data in data_news:
            rate = data.get('rate')
            if float(rate) >= 7.5:
                movie_id = data.get('id')
                title = data.get('title')
                url = data.get('url')
                movie = DoubanSet().get_movie(movie_id)
                if movie:
                    continue
                DoubanSet().insert_douban(movie_id, title, rate, url)
        print('豆瓣爬取结束...')
    except Exception as e:
        print('豆瓣爬取执行出现异常:' + str(e))


if __name__ == '__main__':
    douban_spider()
