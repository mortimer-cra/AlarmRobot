#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @File  : StockImgK.py
# @Author: Administrator
# @Date  : 2020/2/26
import os

OS_PATH = 'C:\\stock_image'
os.makedirs(OS_PATH, exist_ok=True)
FUND_URL = 'http://j4.dfcfw.com/charts/pic6/'


def get_fund_img(code):
    from urllib.request import urlretrieve
    pic_path = FUND_URL + code + '.png'
    file_path = OS_PATH + '\\' + code + '.png'
    try:
        urlretrieve(pic_path, file_path)
    except Exception as e:
        return None
    return file_path


if __name__ == '__main__':
    pass
