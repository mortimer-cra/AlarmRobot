#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/12/18 15:33
# @File    : WorkDay.py
from chinese_calendar import is_holiday, is_workday
from datetime import timedelta

workday_dict = {'工作日': 1, '节假日': 2}


def next_workday(day):
    if not day:
        return None
    while not is_workday(day):
        day = day + timedelta(days=1)
    return day


def next_holiday(day):
    if not day:
        return None
    while not is_holiday(day):
        day = day + timedelta(days=1)
    return day
