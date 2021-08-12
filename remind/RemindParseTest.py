#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/12/10 16:42
# @File    : RemindParseTest.py
from remind.Parser import Parser
import remind.InitJieba
from schedule.RemindScheduler import scheduler

if __name__ == '__main__':

    scheduler.start()
    parse = Parser().parse('每周1晚上八点', 'u1ryrkkr', 'guycg1tg')
    print(parse)
