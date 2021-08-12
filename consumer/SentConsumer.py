#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/12/10 17:37
# @File    : SentConsumer.py
from time import sleep
from queue import Queue
from api.api import send_text_msg, send_image_msg
from db.UserNoticeSet import UserNoticeSet
from message.SystemMessage import *

# 发送消息队列
sent_queue = Queue()


def build_queue_msg(to_user, msg, msg_type=1, msg_arg=''):
    # 处理管理员消息尾巴
    if system_tz_dict and isinstance(msg, str) and ('@chatroom' not in to_user):
        notice_id = system_tz_dict.get(NOTICE_ID)
        notice_str = system_tz_dict.get(NOTICE_STR)
        notices = UserNoticeSet().get_notices(to_user, notice_id)
        if not notices:
            msg += '\n\n' + notice_emoji + ' ' + notice_str
            UserNoticeSet().insert_notices(to_user, notice_id)
    if isinstance(msg, dict):
        msg_type = msg.get('msg_type')
        msg_arg = msg.get('msg_arg')
        msg = ''
    return {'to_user': to_user, 'msg': msg, 'msg_type': msg_type, 'msg_arg': msg_arg}


def sent_queue_msg(msg):
    sent_queue.put(msg)


# 发送消息消费者
# kam
def sent_msg_consumer():
    while True:
        try:
            msg = sent_queue.get()
            if msg is not None:
                to_user = str(msg["to_user"])
                send_msg = str(msg["msg"])
                msg_type = msg["msg_type"]
                msg_arg = str(msg["msg_arg"])
                print(str(msg))
                if msg_type == 1:
                    send_text_msg(to_user, send_msg)
                elif msg_type == 2:
                    send_image_msg(to_user, msg_arg)
                sleep(0.1)
            # time.sleep(random.randint(2,3))
        except Exception as e:
            sent_queue.task_done()
            print('sent_msg_consumer Error:', e)
