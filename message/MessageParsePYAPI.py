#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @File  : MessageParsePYAPI.py
# @Author: Administrator
# @Date  : 2019/12/10
from message.FriendDict import friend_dict
from message.ReplyEnum import ReplyEnum
from message.SessionDict import *
from remind import ParseError
from remind.Parser import Parser, Reminder
import logging
from consumer.SentConsumer import build_queue_msg, sent_queue_msg

logging.basicConfig(level=logging.INFO)

CANCEL = '取消提醒'
QUERY = '我的提醒'
FUNCTION = '功能提醒'
FRIEND = '好友提醒'


# 消息解析
class MessageParsePYAPI:

    def __init__(self, message):
        if message is not None and 'type' in message:
            self.type = message.get('type', '')
            data = message.get('data', {})
            # single
            self.data_type = data.get('data_type', '')
            self.send_or_recv = data.get('send_or_recv', '')
            self.from_wxid = data.get('from_wxid', '')
            self.time = data.get('time', '')
            self.msg = data.get('msg', '')
            self.from_nickname = data.get('from_nickname', '')
            # chatRoom
            self.from_chatroom_wxid = data.get('from_chatroom_wxid', '')
            self.from_member_wxid = data.get('from_member_wxid', '')
            self.from_chatroom_nickname = data.get('from_chatroom_nickname', '')
            # friend
            self.wx_id = data.get('wx_id', '')
            self.wx_id_search = data.get('wx_id_search', '')
            self.wx_nickname = data.get('wx_nickname', '')
            self.wx_avatar = data.get('wx_avatar', '')
            self.remark_name = data.get('remark_name', '')

    def message_process(self):
        if self.type == 'msg::single':
            self.single_message()
        elif self.type == 'friend::person':
            self.friend_person()
        elif self.type == 'msg::chatroom':
            self.chatroom_message()

    # 好友信息
    def friend_person(self):
        friend_dict[self.wx_nickname] = {'id_': self.wx_id, 'search_': self.wx_id_search}

    # 个人消息
    def single_message(self):
        if not self.is_receive():
            return
        response_msg = ''
        # 文字消息
        if self.data_type_text():
            response_msg = self.single_message_text()

        if response_msg:
            sent_queue_msg(build_queue_msg(self.from_wxid, response_msg))

    def is_receive(self):
        if self.send_or_recv[0] == '0':
            return True
        return False

    def data_type_text(self):
        if self.data_type == '1':
            return True
        return False
