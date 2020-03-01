#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @File  : MessageProcessing.py
# @Author: Administrator
# @Date  : 2019/12/10
from message.FriendDict import friend_dict
from message.ReplyEnum import ReplyEnum
from message.SessionDict import *
import logging
from msg_consumer.SentConsumer import build_queue_msg, sent_queue_msg
from message.RemindEnum import CANCEL, QUERY
from schedule.MongoDBUtil import MongoDBUtil
from schedule.Scheduler import scheduler
import emoji

logging.basicConfig(level=logging.INFO)


# 消息解析
class MessageProcessing:

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

    # 群消息
    def chatroom_message(self):
        pass

    def single_message_text(self):
        # 1、处理session
        if self.from_wxid in session_dict:
            try:
                return self.deal_session_dict()
            except Exception as e:
                logging.error('deal_session_dict session Error:', e)
                # 发生异常时清除缓存
                session_dict.pop(self.from_wxid)
                return ReplyEnum.exception_unknow
        else:
            # 2、处理msg中的提醒
            if ReplyEnum.remind in self.msg:
                if self.msg == CANCEL:
                    return self.cancel_remind()
                elif self.msg == QUERY:
                    return self.query_remind()
                else:
                    return Parser().parse(self.msg, self.from_wxid, self.from_nickname)
            else:
                return TianRobot().reply_text(self.msg, self.from_wxid)

    def cancel_remind(self):
        cancel_remind_find_all = MongoDBUtil().del_find_all(self.from_wxid)
        if cancel_remind_find_all:
            return '需要取消下面哪条提醒？告诉我相应的数字序号(多个用逗号隔开)\n\n' + cancel_remind_find_all
        else:
            return '我这里已经没有你的提醒了'

    def query_remind(self):
        query_remind_find_all = MongoDBUtil().find_all(self.from_wxid)
        if query_remind_find_all:
            return '你的提醒都在这里啦\n\n' + query_remind_find_all
        else:
            return '我这里已经没有你的提醒了'

    def deal_session_dict(self):
        if self.msg in ReplyEnum.cancel_list:
            # 消除会话留存
            session_dict.pop(self.from_wxid)
            return ReplyEnum.cancel_session
        if ReplyEnum.remind in self.msg:
            session_dict.pop(self.from_wxid)
            return Parser().parse(self.msg, self.from_wxid, self.from_nickname)

        wxid_session = session_dict[self.from_wxid]
        # 解析时间缺失项
        if wxid_session[SESSION_TYPE] == REMIND_DATE_MISSING:
            try:
                job_time_dict = Parser().parse_time(self.msg)
            except ValueError as e:
                re_msg = session_threshold_msg(wxid_session)
                return str(e) + ',' + ReplyEnum.parse_date_error_example_again + re_msg
            if job_time_dict:
                session_dict.pop(self.from_wxid)
                wxid_session.update(job_time_dict)
                del wxid_session[SESSION_TYPE]
                del wxid_session[SESSION_THRESHOLD]
                return Reminder(**wxid_session).do_schedule()
            re_msg = session_threshold_msg(wxid_session)
            return ReplyEnum.parse_error + ',' + ReplyEnum.parse_date_error_example_again + re_msg
        # 解析do_what缺失项
        if wxid_session[SESSION_TYPE] == REMIND_DO_MISSING:
            session_dict.pop(self.from_wxid)
            wxid_session['do_what'] = self.msg
            del wxid_session[SESSION_TYPE]
            del wxid_session[SESSION_THRESHOLD]
            return Reminder(**wxid_session).do_schedule()
        # 解析to_user缺失项
        if wxid_session[SESSION_TYPE] == REMIND_WHO_MISSING:
            if self.msg in ['我', '我自己']:
                wxid_session['to_user'] = self.from_wxid
            elif self.msg in friend_dict:
                wxid_session['to_user'] = friend_dict[self.msg]['id_']
            else:
                session_dict.pop(self.from_wxid)
                return ReplyEnum.non_friend
            session_dict.pop(self.from_wxid)
            del wxid_session[SESSION_TYPE]
            del wxid_session[SESSION_THRESHOLD]
            return Reminder(**wxid_session).do_schedule()
        # 解析weather city
        if wxid_session[SESSION_TYPE] == WEATHER_CITY_MISSING:
            city = check_city(self.msg)
            if city:
                session_dict.pop(self.from_wxid)
                del wxid_session[SESSION_TYPE]
                del wxid_session[SESSION_THRESHOLD]
                wxid_session['v1'] = self.msg
                return Reminder(**wxid_session).do_schedule()
            else:
                re_msg = session_threshold_msg(wxid_session)
                return '看不懂的城市名称，如果是县城要加“县”字哦，比如：黎平县' + re_msg
        # 解析取消提醒
        if wxid_session[SESSION_TYPE] == JOB_DEL:
            if self.msg:
                flag = False
                num_arr = self.msg.replace('，', ',').split(',')
                for nu in num_arr:
                    if nu.isdigit():
                        if wxid_session.get(str(nu), ''):
                            scheduler.remove_job(wxid_session[str(nu)], 'default')
                            flag = True
                if flag:
                    session_dict.pop(self.from_wxid)
                    return '已经取消啦，' + self.query_remind()
                else:
                    re_msg = session_threshold_msg(wxid_session)
                    return '回复相应的数字序号(多个用逗号隔开,像这样： 1,2,3)让我来取消对应的提醒' + re_msg

    def is_receive(self):
        if self.send_or_recv[0] == '0':
            return True
        return False

    def data_type_text(self):
        if self.data_type == '1':
            return True
        return False
