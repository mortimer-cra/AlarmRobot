# -*- coding: utf-8 -*-
# @Time    : 2019/11/27 23:00
# @Author  : liu
# @File    : WxRobot.py
# @Desc    :
# @Software: PyCharm
from WechatPCAPI import WechatPCAPI
import logging
import time
import threading
from message.FriendDict import friend_dict
from msg_consumer.ReceiveConsumer import *
from msg_consumer.SentConsumer import sent_msg_consumer
from schedule.Scheduler import scheduler

logging.basicConfig(level=logging.INFO)


def main():
    wx_inst = WechatPCAPI(on_message=on_message, log=logging)
    wx_inst.start_wechat(block=True)
    while not wx_inst.get_myself():
        time.sleep(5)
    time.sleep(5)
    threading.Thread(target=message_queue_consumer).start()
    threading.Thread(target=sent_msg_consumer, args=(wx_inst,)).start()
    scheduler.start()
    # 都初始化完后等待3秒 初始化结巴好友昵称分词
    time.sleep(2)


if __name__ == '__main__':
    main()
