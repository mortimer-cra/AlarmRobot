#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @File  : NextReply.py
# @Author: Administrator
# @Date  : 2020/1/2
import random


def reply_ok(until, first_msg, first_add, sb, tail):
    return random.choice((
        "好的，我将会在%s%s提醒%s[@emoji=\\uE405]%s%s" % (until, first_msg, sb, first_add, tail),
        "[@emoji=\\uE420]好的，%s我将会%s提醒%s%s%s" % (until, first_msg, sb, first_add, tail)
    ))


def reply_ok_emojins():
    return random.choice(('[@emoji=\\uD83D\\uDE09]', '[@emoji=\\uD83D\\uDE0A]', '[@emoji=\\uD83D\\uDE03]',
                          '[@emoji=\\uD83D\\uDE01]', '[@emoji=\\u263A]', '[@emoji=\\uD83D\\uDE1A]', '[嘿哈]',
                          '[@emoji=\\uD83D\\uDE43]', '[@emoji=\\uD83D\\uDE0B]', '[@emoji=\\uD83E\\uDD13]'))


if __name__ == '__main__':
    emojins = reply_ok_emojins()
    print(emojins)
    ok = reply_ok('一分钟后', '第一次', "你")
    print(ok)
