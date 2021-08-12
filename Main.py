#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @File  : Main.py
# @Author: Administrator
# @Date  : 2020/1/4
import logging
import threading
from consumer.ReceiveConsumer import *
from consumer.SentConsumer import sent_msg_consumer
from consumer.SentConsumerChatRoom import sent_msg_consumer_chatroom
from consumer.ExtConsumer import *
from remind.InitJieba import *
from schedule.Scheduler import scheduler
from external.weather.AreaDict import CITY_SET
from api.api import get_friend_list
from controller.Controller import app

logging.basicConfig(level=logging.INFO)


def main():
    # 两个消息消费线程
    for i in range(0, 2):
        threading.Thread(target=message_queue_consumer).start()
    threading.Thread(target=sent_msg_consumer).start()
    threading.Thread(target=sent_msg_consumer_chatroom).start()
    # 外部应用提醒消费者
    for i in range(0, 3):
        threading.Thread(target=ext_consumer).start()
    # 都初始化完后等待3秒 初始化结巴好友昵称分词
    friend_list = get_friend_list(is_refresh=1)
    if friend_list:
        for item in friend_list:
            nickname = item.get("Name", "")
            wx_id = item.get("wxid", "")
            friend_dict[nickname] = {'id_': wx_id}
    time.sleep(1)
    init_friend_jieba()
    app.run(host="0.0.0.0", port=8074, debug=False)


if __name__ == '__main__':
    main()
