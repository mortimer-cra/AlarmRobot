#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/1/19 12:56
# @File    : ExtConsumer.py
from external.ExtJobParse import *

# ext消息队列
ext_queue = Queue()


def ext_consumer():
    while True:
        try:
            msg = ext_queue.get()
            if msg is not None:
                ExtJobParse(msg)
        except Exception as e:
            ext_queue.task_done()
            print('ext_consumer Error:', e)

