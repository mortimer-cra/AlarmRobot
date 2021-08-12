#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/12/10 17:34
# @File    : ReceiveConsumer.py
from queue import Queue
from message.MessageParse import MessageParse

# 接受消息队列
receive_message_queue = Queue()


# 接受消息（生产者）
def on_message(message):
    message_str = str(message)
    print('on_message:' + message_str)
    receive_message_queue.put(message)


# 接收消息消费者
def message_queue_consumer():
    print('enter message_queue_consumer...')
    while True:
        try:
            msg = receive_message_queue.get()
            MessageParse(msg)
        except Exception as e:
            receive_message_queue.task_done()
            print('message_queue_consumer Error:', e)
