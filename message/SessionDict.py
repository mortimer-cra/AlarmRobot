#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @File  : SessionDict.py
# @Author: Administrator
# @Date  : 2019/12/10
from message.ReplyEnum import ReplyEnum

# session（注意失效时间问题、用户取消问题）
session_dict = {}

# session
SESSION_TYPE = 'session_type'
FROM_WXID = 'from_wxid'
SESSION_THRESHOLD = 'session_threshold'

# session_type
REMIND_DATE_MISSING = 'remind_date_missing'
REMIND_DO_MISSING = 'remind_do_missing'
REMIND_WHO_MISSING = 'remind_who_missing'
JOB_DEL = 'job_del'
JOB_DEL_ADMIN = 'job_del_admin'
ROOM_CHOOSE = 'room_choose'
ROOM_REMIND = 'room_remind'
FRIEND_CHOOSE = 'friend_choose'
FRIENDS_REMIND = 'friends_remind'
WEATHER_CITY_MISSING = 'weather_city_missing'
NEWS_CHANNEL = 'news_channel'
BUS_CITY = 'bus_city'
BUS_LINE = 'bus_line'
BUS_TARGET = 'bus_target'
YIQING_CITY = 'yiqing_city'
FUND_CODE = 'fund_code'
STOCK_CODE = 'stock_code'


# put
def put_session_dict(**kwargs):
    if not kwargs.get(FROM_WXID) or not kwargs.get(SESSION_TYPE):
        return
    # add a key that can control number of time
    kwargs[SESSION_THRESHOLD] = 0
    session_dict[kwargs.get(FROM_WXID)] = kwargs


# threshold
def session_threshold_msg(wxid_session):
    re_msg = ''
    wxid_session[SESSION_THRESHOLD] += 1
    if wxid_session[SESSION_THRESHOLD] > 1:
        re_msg = ReplyEnum.exit_session
    return re_msg


