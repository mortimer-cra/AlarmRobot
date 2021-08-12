#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @File  : SessionMessage.py
# @Author: Administrator
# @Date  : 2020/1/16
from message.SessionDict import *
from remind.Parser import Parser
from remind.Reminder import *
from message.FriendDict import *
from schedule.Scheduler import *
from external.weather.AreaDict import check_city
from remind.DateEnum import *
from external.ext_dict import *
from external.news.NewsChannel import check_news_channel_value
from external.weather.sojson import get_sojson_weather
from external.news.TianNew import TianNew
from external.news.TianSimpleNews import TianSimpleNews
from external.bus.bus import BusTravelTimeSensor
from external.feiyan.CityFeiyan import CityFeiyan
from db.UserJobSet import UserJobSet
from external.fund.FundImg import get_fund_img
from external.stock.StockImgK import get_stock_img


class SessionMessage:
    def __init__(self, msg, from_wxid, from_nickname):
        self.msg = msg
        self.from_wxid = from_wxid
        self.from_nickname = from_nickname
        self.wxid_session = session_dict[self.from_wxid]

    def build_session_message(self):
        session_kind = {
            REMIND_DATE_MISSING: self.remind_date_missing,
            REMIND_DO_MISSING: self.remind_do_missing,
            REMIND_WHO_MISSING: self.remind_who_missing,
            JOB_DEL: self.job_del,
            JOB_DEL_ADMIN: self.job_del_admin,
            WEATHER_CITY_MISSING: self.weather_city_missing,
            NEWS_CHANNEL: self.news_channel,
            BUS_CITY: self.bus_city,
            BUS_LINE: self.bus_line,
            BUS_TARGET: self.bus_target,
            YIQING_CITY: self.yiqing_city,
            ROOM_CHOOSE: self.room_choose,
            ROOM_REMIND: self.room_remind,
            FRIEND_CHOOSE: self.friend_choose,
            FRIENDS_REMIND: self.friends_remind,
            FUND_CODE: self.fund,
            STOCK_CODE: self.stock
        }
        return session_kind.get(self.wxid_session[SESSION_TYPE], self.default_session)()

    def default_session(self):
        pass

    def remind_date_missing(self):
        if self.msg == '现在':
            self.msg = '一秒后'
        try:
            job_time_dict = Parser().parse_time(self.msg)
        except ValueError as e:
            return self.build_threshold_msg(str(e) + ',' + ReplyEnum.parse_date_error_example_again)
        if job_time_dict:
            repeat_ = job_time_dict.get('repeat', '')
            # 功能提醒控制
            if self.wxid_session['ext_type']:
                # 久坐提醒自定义
                if self.wxid_session['ext_type'] == 9:
                    if REPEAT_KEY_HOUR in repeat_:
                        hour = repeat_[REPEAT_KEY_HOUR]
                        if int(hour) < 9:
                            self.wxid_session['repeat_custom'] = '9-18/' + str(hour)
                        else:
                            return self.build_threshold_msg('时间间隔不合理，请再告诉我一次合理的提醒间隔')
                    else:
                        return self.build_threshold_msg('久坐提醒要以小时为单位，请再告诉我一次提醒频率，比如“每两个小时”')
                # 控制功能提醒的频率
                elif repeat_:
                    if REPEAT_KEY_MINUTE in repeat_ or REPEAT_KEY_HOUR in repeat_:
                        # 股票提醒放开小时
                        if self.wxid_session['ext_type'] == 5:
                            if REPEAT_KEY_HOUR in repeat_:
                                pass
                            else:
                                return self.build_threshold_msg('股票的重复提醒要至少以小时为单位，请重新告诉我提醒的时间')
                        else:
                            return self.build_threshold_msg(
                                '实用功能的重复提醒要至少以天为单位哦，' + ReplyEnum.parse_date_error_example_again_ext)
            # 不是提醒自己
            if self.from_wxid != self.wxid_session['to_user'] and '@chatroom' not in self.wxid_session['to_user']:
                if repeat_:
                    return ReplyEnum.friend_repeat_limit + '，试试说个时间点吧'
            self.wxid_session.update(job_time_dict)
            return self.pop_del_reminder()
        # 回复其他选项的
        if not job_time_dict and self.wxid_session['ext_type']:
            if self.wxid_session['ext_type'] == 7:
                city = check_city(self.msg)
                if city:
                    return self.yiqing_city(city)
            if self.wxid_session['ext_type'] == 1:
                city = check_city(self.msg)
                if city:
                    return self.weather_city_missing(city)
            if self.wxid_session['ext_type'] == 3:
                if self.msg.isdigit() and check_news_channel_value(int(self.msg)):
                    return self.news_channel(int(self.msg))
            session_dict.pop(self.from_wxid)
            return None
        return self.build_threshold_msg(ReplyEnum.parse_error + '，' + ReplyEnum.parse_date_error_example_again)

    def remind_do_missing(self):
        self.wxid_session['do_what'] = self.msg
        return self.pop_del_reminder()

    def remind_who_missing(self):
        if self.msg in ['我', '我自己']:
            self.wxid_session['to_user'] = self.from_wxid
        elif self.msg in friend_dict:
            repeat_session = self.wxid_session.get('repeat', '')
            if repeat_session:
                session_dict.pop(self.from_wxid)
                return ReplyEnum.friend_repeat_limit
            self.wxid_session['to_user'] = friend_dict[self.msg]['id_']
        else:
            session_dict.pop(self.from_wxid)
            return ReplyEnum.non_friend
        return self.pop_del_reminder()

    def job_del(self):
        if self.msg:
            flag = False
            num_arr = self.msg.replace('，', ',').split(',')
            for nu in num_arr:
                if nu.isdigit():
                    job_id = self.wxid_session.get(str(nu), '')
                    if job_id:
                        if str(job_id).startswith('monitoring_'):
                            del_dic = {'user_id': self.from_wxid, 'job_id': job_id}
                            UserJobSet().delete(del_dic)
                        else:
                            scheduler.remove_job(job_id, 'default')
                        flag = True
            if flag:
                session_dict.pop(self.from_wxid)
                return '已经取消啦，' + self.query_remind()
            else:
                re_msg = session_threshold_msg(self.wxid_session)
                return '告诉我要取消的提醒对应的数字序号(多个用逗号隔开,像这样[@emoji=\\uE231] 1,2,3)' + re_msg

    def job_del_admin(self):
        if self.msg:
            flag = False
            num_arr = self.msg.replace('，', ',').split(',')
            for nu in num_arr:
                if nu.isdigit():
                    if self.wxid_session.get(str(nu), ''):
                        scheduler.remove_job(self.wxid_session[str(nu)], 'default')
                        flag = True
            if flag:
                session_dict.pop(self.from_wxid)
                return '已取消'

    def query_remind(self):
        query_remind_find_all = UserJobSet().find_all(self.from_wxid)
        if query_remind_find_all:
            return '以下提醒正在进行中[@emoji=\\uE11B]\n\n' + query_remind_find_all
        else:
            return '我这里已经没有你的提醒了[@emoji=\\uD83D\\uDE48]'

    def weather_city_missing(self, city=None):
        if not city:
            city = check_city(self.msg)
        if city:
            self.wxid_session['v1'] = self.msg
            self.wxid_session['ext_type'] = external_function_dict[WEATHER]
            if self.wxid_session['job_time']:
                return self.pop_del_reminder()
            else:
                weather = get_sojson_weather(city)
                self.wxid_session[SESSION_TYPE] = REMIND_DATE_MISSING
                if weather:
                    re_arr = [weather, ReplyEnum.date_parse_error_repeat]
                    return re_arr
                return ReplyEnum.date_parse_error_repeat
        else:
            return self.build_threshold_msg('我没有get到城市名称，如果是县城要加“县”字哦，比如：黎平县 [@emoji=\\uE405]')

    def news_channel(self, num=0):
        if not num:
            num = int(self.msg)
        if not self.msg.isdigit() or (not check_news_channel_value(num)):
            return self.build_threshold_msg('请回复相应的数字序号哦')
        self.wxid_session['v1'] = str(num)
        self.wxid_session['ext_type'] = external_function_dict[NEWS]
        self.wxid_session[SESSION_TYPE] = REMIND_DATE_MISSING
        if num == 1:
            new_msg = TianSimpleNews().reply_text()
        else:
            new_msg = TianNew().reply_text(10, num)
        if new_msg:
            return [new_msg, ReplyEnum.date_parse_error_repeat]
        return ReplyEnum.date_parse_error_repeat

    def bus_city(self):
        if self.msg:
            split = self.msg.replace('市', '').replace('路', '').split(' ')
            if len(split) != 2:
                return self.build_threshold_msg('请用空格隔开城市和公交线路。像这样：成都  84')
            sensor = BusTravelTimeSensor()
            city_id = sensor.city(split[0])
            if not city_id:
                session_dict.pop(self.from_wxid)
                return '暂不支持你的城市哦'
            line_arr = sensor.line_key(city_id, split[1])
            if not line_arr:
                session_dict.pop(self.from_wxid)
                return '暂不支持你的公交线路哦'
            re_line_msg = '找到以下结果，请告诉我相应的数字序号\n\n'
            line_idx = 1
            session_dict_line = {}
            for line in line_arr:
                name_line = line['name_']
                sn_line = line['info']['sn']
                re_line_msg += str(line_idx) + '. ' + name_line + '(始发站为 ' + sn_line + ')\n'
                session_dict_line[str(line_idx)] = line
                line_idx += 1
            self.wxid_session[SESSION_TYPE] = BUS_LINE
            self.wxid_session['v1'] = city_id
            self.wxid_session['session_dict_line'] = session_dict_line
            return re_line_msg

    def bus_line(self):
        if not self.msg.isdigit():
            return self.build_threshold_msg('请回复相应的数字序号哦')
        dict_line_num = self.wxid_session['session_dict_line'].get(self.msg, '')
        if not dict_line_num:
            return self.build_threshold_msg('请回复相应的数字序号哦')
        city_id = self.wxid_session['v1']
        name_line = dict_line_num['name_']
        no_line = dict_line_num['info']['lineNo']
        direction_line = dict_line_num['info']['direction']
        line_res = BusTravelTimeSensor().line(city_id, no_line, name_line, direction_line)
        if line_res == -1:
            session_dict.pop(self.from_wxid)
            return '暂不支持你的公交线路哦'
        if line_res:
            bus_line_dict = {'line_no': no_line, 'line_name': name_line, 'direction': direction_line}
            del self.wxid_session['session_dict_line']
            self.wxid_session['v2'] = bus_line_dict
            self.wxid_session[SESSION_TYPE] = BUS_TARGET
            # wxid_session['do_what'] += '(' + name_line + '路)'
            return '请告诉我你的车站（回数字）\n\n' + line_res
        session_dict.pop(self.from_wxid)
        return '哦吼，请求数据出了点小问题'

    def bus_target(self):
        if not self.msg.isdigit():
            return self.build_threshold_msg('请回复相应的数字序号哦')
        self.wxid_session['v3'] = self.msg
        self.wxid_session['ext_type'] = external_function_dict[BUS]
        if self.wxid_session['job_time']:
            return self.pop_del_reminder()
        else:
            self.wxid_session[SESSION_TYPE] = REMIND_DATE_MISSING
            city_no = self.wxid_session["v1"]
            bus_line = self.wxid_session["v2"]
            bus_order = self.wxid_session["v3"]
            if bus_line:
                line_no_ = bus_line['line_no']
                name_ = bus_line['line_name']
                direction_ = str(bus_line['direction'])
            if all([city_no, line_no_, name_, direction_, bus_order]):
                bus_msg = BusTravelTimeSensor().update(city_no, line_no_, name_, direction_, bus_order)
                re_arr = [bus_msg, ReplyEnum.date_parse_error_repeat]
                return re_arr
            return ReplyEnum.date_parse_error_repeat

    def yiqing_city(self, city=None):
        if not city:
            city = check_city(self.msg)
        if city:
            self.wxid_session['v1'] = self.msg
            self.wxid_session['ext_type'] = external_function_dict[YIQING]
            yiqing_txt = CityFeiyan().reply_text(self.msg)
            if self.wxid_session['job_time']:
                return self.pop_del_reminder()
            else:
                self.wxid_session[SESSION_TYPE] = REMIND_DATE_MISSING
                re_arr = [yiqing_txt,
                          ReplyEnum.date_parse_error_repeat + '\n\n[@emoji=\\uE10F] 疫情提醒建议设置在每天早上九点及以后的时间']
                return re_arr
        else:
            return self.build_threshold_msg('我没有get到城市名称（不是省和县哦），请再告诉我一下')

    def room_choose(self):
        num_arr = self.msg.replace('，', ',').split(',')
        user_arr = []
        for nu in num_arr:
            if not nu:
                continue
            if not nu.isdigit():
                return self.build_threshold_msg('请回复相应的数字序号哦，多个用“，”隔开，像这样：1,2,3')
            user = self.wxid_session.get(str(nu), '')
            if user:
                user_arr.append(user)
        user_id = ",".join(str(i) for i in user_arr)
        if not user_id:
            return self.build_threshold_msg('请回复相应的数字序号哦，多个用“，”隔开，像这样：1,2,3')
        self.wxid_session[SESSION_TYPE] = ROOM_REMIND
        self.wxid_session['chatroom_id'] = user_id
        return '请说出群提醒的时间和内容，像这样：周一上午10点提醒开会'

    def room_remind(self):
        chatroom_id = self.wxid_session['chatroom_id']
        session_dict.pop(self.from_wxid)
        return Parser().parse(self.msg, self.from_wxid, self.from_nickname, chatroom_id)

    def friend_choose(self):
        num_arr = self.msg.replace('，', ',').split(',')
        user_arr = []
        for nu in num_arr:
            if not nu:
                continue
            if not nu.isdigit():
                return self.build_threshold_msg('请回复相应的数字序号哦，多个用“，”隔开，像这样：1,2,3')
            user = self.wxid_session.get(str(nu), '')
            if user:
                user_arr.append(user)
        user_id = ",".join(str(i) for i in user_arr)
        if not user_id:
            return self.build_threshold_msg('请回复相应的数字序号哦，多个用“，”隔开，像这样：1,2,3')
        self.wxid_session[SESSION_TYPE] = FRIENDS_REMIND
        self.wxid_session['user_id'] = user_id
        return '请说出提醒的时间和内容，像这样：明天上午十点提醒戴口罩'

    def friends_remind(self):
        user_id = self.wxid_session['user_id']
        session_dict.pop(self.from_wxid)
        # 增加好友提醒反馈
        from_user = ',from_user:' + self.from_wxid
        user_id += from_user
        return Parser().parse(self.msg, self.from_wxid, self.from_nickname, user_id)

    def stock(self):
        re_arr = []
        message = '[@emoji=\\uD83D\\uDCC8] 股票分时线提醒（' + self.msg + ')'
        re_arr.append(message)
        num_arr = self.msg.replace('，', ',').split(',')
        for nu in num_arr:
            if not nu:
                continue
            nu = str(nu).lower()
            import re
            match = re.match('^(?i)s[hz]\\d{6}$', nu)
            if not match:
                return self.build_threshold_msg('没有找到相应的股票，请换个股票代码试试，比如 sh600000')
            path = get_stock_img(nu)
            if not path:
                return self.build_threshold_msg('没有找到相应的股票，请换个股票代码试试，比如 sh600000')
            re_arr.append({'msg_type': 2, 'msg_arg': path})
        self.wxid_session['v1'] = self.msg
        self.wxid_session['ext_type'] = external_function_dict[STOCK]
        self.wxid_session[SESSION_TYPE] = REMIND_DATE_MISSING
        re_message = ReplyEnum.date_parse_error_repeat + '\n\n[@emoji=\\uE10F] 股票提醒建议设置在每天9:30到15:00'
        re_arr.append(re_message)
        return re_arr

    def fund(self):
        re_arr = []
        message = '[@emoji=\\uD83D\\uDCC8] 基金实时净值走势估算提醒（' + self.msg + ')'
        re_arr.append(message)
        num_arr = self.msg.replace('，', ',').split(',')
        for nu in num_arr:
            if not nu:
                continue
            if not nu.isdigit():
                return self.build_threshold_msg('请回复基金代码哦，多个用“，”隔开，像这样：519772,090010')
            path = get_fund_img(str(nu))
            if not path:
                return self.build_threshold_msg('没有找到相应的基金，请换个基金代码试试')
            re_arr.append({'msg_type': 2, 'msg_arg': path})
        self.wxid_session['v1'] = self.msg
        self.wxid_session['ext_type'] = external_function_dict[FUND]
        self.wxid_session[SESSION_TYPE] = REMIND_DATE_MISSING
        re_message = ReplyEnum.date_parse_error_repeat + '\n\n[@emoji=\\uE10F] 基金提醒建议设置在每天9:30到15:00'
        re_arr.append(re_message)
        return re_arr

    def pop_del_reminder(self):
        session_dict.pop(self.from_wxid)
        del self.wxid_session[SESSION_TYPE]
        del self.wxid_session[SESSION_THRESHOLD]
        return Reminder(**self.wxid_session).do_schedule()

    def build_threshold_msg(self, re_message):
        re_msg = session_threshold_msg(self.wxid_session)
        return re_message + re_msg
