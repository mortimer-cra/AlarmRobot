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
WEATHER_CITY_MISSING = 'weather_city_missing'


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
    if wxid_session[SESSION_THRESHOLD] > 2:
        re_msg = ReplyEnum.exit_session
    return re_msg


