#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/1/10 10:43
# @File    : MessageParse.py
from message.SessionDict import *
from remind.Parser import Parser
import logging
import threading
import time
import json
from consumer.SentConsumer import build_queue_msg, sent_queue_msg
from consumer.SentConsumerChatRoom import build_queue_msg_chatroom, sent_queue_msg_chatroom
from schedule.Scheduler import *
from external.tencent_voice.VoiceRecognition import get_voice_text
from message.SessionMessage import SessionMessage
from external.ext_dict import *
from external.chatbot.TuLingRobot import TuLingRobot
from api.api import get_robot_wxid
from external.weather.AreaDict import check_city
from external.feiyan.CityFeiyan import CityFeiyan
from db.UserJobSet import UserJobSet
from db.UserFriendsSet import UserFriendsSet
from remind.InitJieba import *
from db.UserChatroomSet import UserChatroomSet
from message.SystemMessage import *
from external.feiyan.FeiyanCache import get_foreign_yiqing, check_country

logging.basicConfig(level=logging.INFO)

CANCEL = '取消提醒'
QUERY = '我的提醒'
FUNCTION = '功能提醒'
FRIENDS = '好友提醒'
GROUP = '群提醒'

check_frequently_message_dict = {}


def check_frequently(message):
    if str(message.get('Event', '')) != 'EventFriendMsg':
        return True
    from_wxid = message.get('from_wxid', '')
    msg_time = int(time.time())
    if from_wxid:
        if check_frequently_message_dict:
            if from_wxid == check_frequently_message_dict.get('from_wxid', ''):
                time_diff = int(msg_time) - int(check_frequently_message_dict.get('time', ''))
                if time_diff < 2:
                    return False
        check_frequently_message_dict['from_wxid'] = from_wxid
        check_frequently_message_dict['time'] = msg_time
    return True


class MessageParse:
    def __init__(self, message):
        self.type = message.get('Event', '')
        self.data_type = message.get('type', '')
        self.msg = message.get('msg', '')
        self.json_msg = message.get('json_msg', '')
        # single
        self.from_wxid = message.get('from_wxid', '')
        self.from_nickname = message.get('from_name', '')
        # chatRoom
        self.from_chatroom_wxid = message.get('final_from_wxid', '')
        self.from_chatroom_name = message.get('final_from_name', '')
        # function
        if check_frequently(message):
            self.build_message()

    def build_message(self):
        message_kind = {
            'EventFriendMsg': self.private_message,
            'EventGroupMsg': self.chatroom_message,
            'EventGroupMemberAdd': self.invate_chatroom,
            'EventGroupMemberDecrease': self.remove_chatroom,
            'EventFriendVerify': self.friend_apply
        }
        return message_kind.get(str(self.type), self.other_message)()

    # 个人消息
    def private_message(self):
        response_msg = ''
        # 去除自己的
        if self.from_wxid == get_robot_wxid():
            return
        # 文字消息
        if self.data_type_text():
            response_msg = self.message_text()
        # voice
        elif self.data_type_voice():
            text = get_voice_text(r'' + self.msg)
            if text:
                self.msg = text
                response_msg = '"' + text + '"\n\n' + self.message_text()
            else:
                response_msg = '哦吼~网络好像出了点小问题，试试用打字的吧'
        # 好友申请
        elif self.data_type_friend():
            # 增加好友字典
            friend_dict[self.from_nickname] = {'id_': self.from_wxid}
            # 增加结巴分词
            add_jieba(self.from_nickname)
            # 更改名片状态，发送名片分享好友提醒
            UserFriendsSet().update_status(self.from_wxid, self.from_nickname)
            # 发送欢迎消息
            response_msg = ReplyEnum.welcome_example
        # 被删除
        elif self.delete_robot():
            # 删除全部提醒任务
            find_jobs = UserJobSet().find_user_jobs(self.from_wxid)
            if find_jobs:
                for line in find_jobs:
                    try:
                        scheduler.remove_job(str(line), 'default')
                    except Exception as e:
                        logging.info(str(e))
            # 删除好友字典
            friend_dict.pop(self.from_nickname)
            # 删除好友db
            UserFriendsSet().del_friends(self.from_wxid)
            pass

        if response_msg:
            if isinstance(response_msg, list):
                for re_msg in response_msg:
                    sent_queue_msg(build_queue_msg(self.from_wxid, re_msg))
            else:
                sent_queue_msg(build_queue_msg(self.from_wxid, response_msg))

    # 群消息
    def chatroom_message(self):
        response_msg = ''
        if self.data_type_text():
            response_msg = self.chatroom_text()

        if response_msg:
            sent_queue_msg_chatroom(
                build_queue_msg_chatroom(self.from_wxid, self.from_chatroom_wxid, self.from_chatroom_name,
                                         response_msg))

    # 群邀请
    def invate_chatroom(self):
        group_msg = json.loads(self.json_msg)
        guest = group_msg['guest']
        flag = False
        for number in guest:
            if get_robot_wxid() == number['wxid']:
                flag = True
                break
        if not flag:
            return
        group_wxid = group_msg['group_wxid']
        group_name = group_msg['group_name']
        inviter_wxid = group_msg['inviter']['wxid']
        UserChatroomSet().insert_chatrooms(inviter_wxid, group_wxid, group_name)
        sent_queue_msg(build_queue_msg(inviter_wxid, '提醒喵已接受你的群邀请，如需创建群提醒请发送“群提醒”。'))

    # 被移除群
    def remove_chatroom(self):
        group_msg = json.loads(self.json_msg)
        if get_robot_wxid() != group_msg['member_wxid']:
            return
        UserChatroomSet().remove(self.from_wxid)

    # 好友名片申请
    def friend_apply(self):
        json_msg = json.loads(self.json_msg)
        share_wxid = json_msg.get('share_wxid', '')
        if share_wxid:
            share_nickname = json_msg.get('share_nickname')
            UserFriendsSet().share_add(self.from_wxid, self.from_nickname, share_wxid, share_nickname)

    # 其他类型的消息处理
    def other_message(self):
        pass

    def message_text(self):
        # 0、处理系统消息
        if self.msg.startswith(SYSTEM_DZ_MSG):
            return self.admin_msg()
        # 1、处理session
        if self.from_wxid in session_dict:
            try:
                if self.msg in ReplyEnum.cancel_list:
                    # 消除会话留存
                    session_dict.pop(self.from_wxid)
                    return ReplyEnum.cancel_session
                if ReplyEnum.remind in self.msg and \
                        (not ('提醒一次' in self.msg or '提醒1次' in self.msg)) and \
                        session_dict[self.from_wxid][SESSION_TYPE] != ROOM_REMIND and \
                        session_dict[self.from_wxid][SESSION_TYPE] != FRIENDS_REMIND:
                    session_dict.pop(self.from_wxid)
                    return self.build_remind()
                if self.msg == GROUP:
                    session_dict.pop(self.from_wxid)
                    return self.build_remind()
                session = SessionMessage(self.msg, self.from_wxid, self.from_nickname).build_session_message()
                if session:
                    return session
            except Exception as e:
                logging.error('deal_session_dict session Error:', e)
                # 发生异常时清除缓存
                session_dict.pop(self.from_wxid)
                return ReplyEnum.exception_unknow
        # 2、处理msg中的提醒
        if ReplyEnum.remind in self.msg:
            return self.build_remind()
        else:
            # 在这里先处理下暂时的疫情
            if YIQING in self.msg:
                replace = self.msg.replace(' ', '').replace(YIQING, '')
                # 国内城市
                city = check_city(replace)
                if city:
                    return CityFeiyan().reply_text_chatroom(city)
                # 国外
                country = check_country(replace)
                if country:
                    return get_foreign_yiqing(replace)
                return '试试用国内城市（不是省和县）或者国家名称，像这样和我说：“成都疫情”、“意大利疫情”'
            # 没有提醒关键词的，先过滤一遍外部应用关键词
            for key in external_function_dict:
                if key in self.msg:
                    return '[@emoji=\\uE10F] 试试这样说 ："' + key + '提醒"'
            return TuLingRobot().reply_text(self.msg, self.from_wxid)

    def chatroom_text(self):
        if self.msg:
            split_arr = self.msg.split('  ')
            if not split_arr:
                return None
            for sb in split_arr:
                if get_robot_wxid() in sb:
                    msg_str = split_arr[len(split_arr) - 1]
                    if ReplyEnum.remind in msg_str.replace('提醒喵', ''):
                        return '为了不打扰到群里其他人，个人提醒服务请私聊提醒喵哦'
                    if self.who_are_u(msg_str):
                        return '我是人见人爱的提醒喵！添加我为微信好友可体验提醒服务哦，欢迎来撩我！'

                    # 拓展功能
                    if YIQING in msg_str:
                        replace = msg_str.replace(' ', '').replace(YIQING, '')
                        # 国内城市
                        city = check_city(replace)
                        if city:
                            return CityFeiyan().reply_text_chatroom(city)
                        # 国外
                        country = check_country(replace)
                        if country:
                            return get_foreign_yiqing(replace)
                        return '试试用国内城市或者国家名称（不是省和县），像这样和我说：“成都疫情”、“意大利疫情”'
                    return TuLingRobot().reply_text(msg_str, self.from_wxid)
        return None

    def build_remind(self):
        remind_kind = {
            QUERY: self.query_remind,
            CANCEL: self.cancel_remind,
            FUNCTION: self.function_remind,
            FRIENDS: self.friends_remind,
            GROUP: self.group_remind
        }
        return remind_kind.get(self.msg, self.default_remind)()

    def cancel_remind(self):
        cancel_remind_find_all = UserJobSet().del_find_all(self.from_wxid)
        if cancel_remind_find_all:
            return '需要取消下面哪条提醒？告诉我相应的数字序号(多个用逗号隔开)[@emoji=\\uD83D\\uDC47]\n\n' + cancel_remind_find_all
        else:
            return '已经没有你的提醒了[@emoji=\\uD83D\\uDE48]'

    def query_remind(self):
        query_remind_find_all = UserJobSet().find_all(self.from_wxid)
        if query_remind_find_all:
            return '以下提醒正在进行中，发送“取消提醒”可以取消其中的提醒\n\n' + query_remind_find_all
        else:
            return '已经没有你的提醒了[@emoji=\\uD83D\\uDE48]'

    def function_remind(self):
        return ReplyEnum.function_example

    def group_remind(self):
        chatrooms = UserChatroomSet().get_chatrooms(self.from_wxid)
        if not chatrooms or chatrooms.count() == 0:
            return "邀请提醒喵到群聊可以发布群提醒哦"
        if chatrooms.count() == 1:
            room_id = chatrooms[0]['chatroom_id']
            room_name = chatrooms[0]['chatroom_name']
            session_room_remind = {SESSION_TYPE: ROOM_REMIND, FROM_WXID: self.from_wxid, 'chatroom_id': room_id}
            put_session_dict(**session_room_remind)
            return '找到了一个群聊："' + room_name + '"\n\n请说出群提醒的时间和内容，像这样：周一上午10点 开会'
        else:
            index = 1
            session_room_choose = {}
            choose_number = '请选择要提醒的群聊（回数字，多个用逗号隔开）\n'
            for number in chatrooms:
                choose_number += str(index) + '、' + number['chatroom_name'] + '\n'
                # 装进session
                session_room_choose.update({str(index): number['chatroom_id']})
                index += 1
            if session_room_choose:
                session_room_choose.update({SESSION_TYPE: ROOM_CHOOSE, FROM_WXID: self.from_wxid})
                put_session_dict(**session_room_choose)
            return choose_number

    def friends_remind(self):
        friends = UserFriendsSet().find_friends(self.from_wxid)
        if not friends:
            return '你还没有好友可以提醒。\n\n' \
                   '[@emoji=\\uE10F] 将提醒喵的微信名片分享给要提醒的好友，对方添加提醒喵后你们就可以互相提醒啦'
        if len(friends) == 1:
            user_id = friends[0].get('user_id')
            user_name = friends[0].get('user_name')
            status = friends[0].get('status')
            if status == '0':
                return '请等待提醒喵通过好友验证哦'
            session_friends_remind = {SESSION_TYPE: FRIENDS_REMIND, FROM_WXID: self.from_wxid, 'user_id': user_id}
            put_session_dict(**session_friends_remind)
            return '找到了一个好友 ：“' + user_name + '”' + '\n\n请说出提醒的时间和内容，像这样：明天上午十点提醒戴口罩'
        session_dict_friends = {}
        num = 1
        re_line = '请选择要提醒的好友（回数字，多个用逗号隔开）\n'
        for friend in friends:
            status = friend.get('status')
            if not int(status):
                continue
            user_id = friend.get('user_id')
            user_name = friend.get('user_name')
            re_line += str(num) + '. ' + user_name + '\n'
            # 装进session
            session_dict_friends.update({str(num): user_id})
            num += 1
        if session_dict_friends:
            session_dict_friends.update({SESSION_TYPE: FRIEND_CHOOSE, FROM_WXID: self.from_wxid})
            put_session_dict(**session_dict_friends)
        return re_line

    def default_remind(self):
        for ext_key in external_function_dict:
            if ext_key == self.msg.replace(' ', '').replace(ReplyEnum.remind, ''):
                return Parser().parse_ext(self.msg, self.from_wxid, self.from_nickname, ext_key)
        return Parser().parse(self.msg, self.from_wxid, self.from_nickname)

    def admin_msg(self):
        split = self.msg.split(' ')
        do_sys = split[1]
        # 通知
        if do_sys == SYSTEM_NOTICE_MSG:
            if split[2] == 'del':
                clean_system_dict()
            else:
                put_system_dict(split[2], split[3])
            return 'ok'
        # 取消用户的提醒
        elif do_sys == SYSTEM_CANCEL_USER:
            user_name = split[2]
            # 先模糊查找用户id
            user_id = ''
            for key in friend_dict:
                if user_name in key:
                    user_id = friend_dict[key]['id_']
            if not user_id:
                return 'no user'
            # 找到用户微信id后 查询全部的提醒
            cancel_remind_admin = UserJobSet().del_find_all_sys(user_id, self.from_wxid)
            if not cancel_remind_admin:
                return 'no remind'
            return cancel_remind_admin
        # 取消提醒
        elif do_sys == SYSTEM_CANCEL_REMIND:
            remind = split[2]
            return UserJobSet().del_remark_admin(remind)
        # 手动缓存新闻
        elif do_sys == SYSTEM_CACHE:
            threading.Thread(target=cache_new_job).start()
            return 'ok'

    def data_type_text(self):
        if self.data_type == 1:
            return True
        return False

    def data_type_voice(self):
        if self.data_type == 34:
            return True
        return False

    def data_type_friend(self):
        if self.data_type == 10000 and self.msg.startswith('你已添加了'):
            return True
        return False

    def delete_robot(self):
        if self.data_type == 10000 and '开启了朋友验证' in self.msg:
            return True
        return False

    def who_are_u(self, key):
        for k in ReplyEnum.who_are_u:
            if k in key:
                return True
        return False
