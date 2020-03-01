#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/12/10 17:34
# @File    : ReceiveConsumer.py
from queue import Queue
from message.MessageProcessing import MessageProcessing

# 接受消息队列
receive_message_queue = Queue()

# 限制重复 1s
message_exclude_repeat = ''


# 接受消息（生产者）
def on_message(message):
    global message_exclude_repeat
    message_str = str(message)
    if message_exclude_repeat:
        if message_str == message_exclude_repeat:
            return
    message_exclude_repeat = message_str
    print('on_message:' + message_str)
    receive_message_queue.put(message)


# 接收消息消费者
def message_queue_consumer():
    print('enter message_queue_consumer...')
    while True:
        try:
            msg = receive_message_queue.get()
            MessageProcessing(msg).message_process()
        except Exception as e:
            receive_message_queue.task_done()
            print('message_queue_consumer Error:', e)
