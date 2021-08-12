#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/12/18 13:00
# @File    : TestWorkDay.py
from chinese_calendar import *
from remind.WorkDay import *
from remind.RemindUtil import *

if __name__ == '__main__':
    # remark = '工作日'
    # day = datetime.fromtimestamp(1569915520)
    # for key in workday_dict:
    #     if key in remark:
    #         if workday_dict[key] == 1:
    #             day = next_workday(day)
    #         elif workday_dict[key] == 2:
    #             day = next_holiday(day)
    #
    # time = nature_time(day.strftime("%Y-%m-%d %H:%M:%S"))
    # print(time)

    day = datetime.strptime('2020-01-19 16:15:00', '%Y-%m-%d %H:%M:%S')

    print(is_holiday(day))
    print(is_workday(day))
    print(is_in_lieu(day))
