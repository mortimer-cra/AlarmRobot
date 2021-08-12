#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @File  : SystemMessage.py
# @Author: Administrator
# @Date  : 2020/2/14
SYSTEM_NOTICE_MSG = 'tz'
SYSTEM_CANCEL_USER = 'xxxx'
SYSTEM_CANCEL_REMIND = 'xxxx'
SYSTEM_CACHE = 'xxxx'
SYSTEM_DZ_MSG = 'xxxx'

system_tz_dict = {}
NOTICE_ID = 'notice_id'
NOTICE_STR = 'notice_str'

notice_emoji = '[@emoji=\\uD83D\\uDCE2]'


def put_system_dict(*args):
    if not args:
        return
    system_tz_dict[NOTICE_ID] = args[0]
    system_tz_dict[NOTICE_STR] = args[1]


def clean_system_dict():
    system_tz_dict.clear()
