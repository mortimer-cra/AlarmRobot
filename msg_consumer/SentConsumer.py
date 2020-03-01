#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/12/10 17:37
# @File    : SentConsumer.py
from queue import Queue
import time

# 发送消息队列
sent_queue = Queue()


def build_queue_msg(to_user, msg):
    return {'to_user': to_user, 'msg': msg}


def sent_queue_msg(msg):
    sent_queue.put(msg)


# 发送消息消费者
def sent_msg_consumer(wx_inst):
    while True:
        try:
            msg = sent_queue.get()
            if msg is not None:
                to_user = str(msg["to_user"])
                send_msg = str(msg["msg"])
                print(str(msg))
                wx_inst.send_text(to_user=to_user, msg=send_msg)
            # time.sleep(0.1)
            # time.sleep(random.randint(2,3))
        except Exception as e:
            sent_queue.task_done()
            print('sent_msg_consumer Error:', e)
