#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @File  : RmImgDir.py
# @Author: Administrator
# @Date  : 2020/2/27
import shutil
import os

OS_PATH = 'C:\\stock_image'


def clean_dir():
    try:
        shutil.rmtree(OS_PATH)
        os.mkdir(OS_PATH)
    except Exception as e:
        print('clean_dir error ...')
