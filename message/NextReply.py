#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @File  : NextReply.py
# @Author: Administrator
# @Date  : 2020/1/2
import random


def reply_ok(until, first_msg, sb):
    return random.choice((
        "好的，我将会在%s%s提醒%s%s" % (until, first_msg, "你" if sb else "ta", reply_ok_emojins()),
        "👌 %s%s我会提醒%s%s" % (until, first_msg, "你" if sb else "ta", reply_ok_emojins()),
        "记下了，我将会在%s%s提醒%s%s" % (until, first_msg, "你" if sb else "ta", reply_ok_emojins())
    ))


def reply_ok_emojins():
    return random.choice(('😉', '😙', '🙃', '☺'))
