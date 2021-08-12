#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @File  : RemindUtil.py
# @Author: Administrator
# @Date  : 2019/12/11
from datetime import timedelta, datetime


def delta2dict(delta):
    """Accepts a delta, returns a dictionary of units"""
    delta = abs(delta)
    return {
        '年': int(delta.days / 365),
        '天': int(delta.days % 365),
        '小时': int(delta.seconds / 3600),
        '分钟': int(delta.seconds / 60) % 60,
        '秒': delta.seconds % 60,
        '毫秒': delta.microseconds
    }


def nature_time(dt, precision=2, past_tense='{}前', future_tense='{}后'):
    """Accept a datetime or timedelta, return a human readable delta string,
    Steal from ago.human
    """
    now = datetime.now().replace(microsecond=0)
    delta = dt
    if type(dt) is not type(timedelta()):
        delta = datetime.strptime(dt, '%Y-%m-%d %H:%M:%S') - now

    the_tense = future_tense
    if delta < timedelta(0):
        the_tense = past_tense

    d = delta2dict(delta)
    hlist = []
    count = 0
    units = ('年', '天', '小时', '分钟', '秒', '毫秒')
    for unit in units:
        if count >= precision:
            break  # met precision
        if d[unit] == 0:
            continue  # skip 0's
        if hlist and unit == units[-1]:  # skip X秒XX毫秒
            break
        hlist.append('%s%s' % (d[unit], unit))
        count += 1
    human_delta = ''.join(hlist)
    return the_tense.format(human_delta)

if __name__ == '__main__':
    time = nature_time(timedelta(years=1))
    print(time)
