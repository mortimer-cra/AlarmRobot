#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @File  : SentConsumerChatRoom.py
# @Author: Administrator
# @Date  : 2020/2/1
from queue import Queue
import time
from api.api import get_robot_wxid,send_group_at_msg

# 发送消息队列(chatroom)
sent_queue_chatroom = Queue()


def build_queue_msg_chatroom(to_wxid, at_wxid, at_name, msg):
    return {'to_wxid': to_wxid, 'at_wxid': at_wxid, 'at_name': at_name, 'msg': msg}


def sent_queue_msg_chatroom(msg):
    sent_queue_chatroom.put(msg)


# 发送消息消费者
def sent_msg_consumer_chatroom():
    while True:
        try:
            msg = sent_queue_chatroom.get()
            if msg is not None:
                to_wxid = str(msg["to_wxid"])
                at_wxid = str(msg["at_wxid"])
                at_name = str(msg["at_name"])
                msg = str(msg["msg"])
                send_group_at_msg(to_wxid, at_wxid, at_name, msg)
            # time.sleep(0.1)
            # time.sleep(random.randint(2,3))
        except Exception as e:
            sent_queue_chatroom.task_done()
            print('sent_msg_consumer_chatroom Error:', e)
