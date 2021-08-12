#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @File  : Reminder.py
# @Author: Administrator
# @Date  : 2019/12/11
from remind.RemindUtil import nature_time, datetime
from schedule.RemindScheduler import RemindScheduler
from remind.WorkDay import *
from message.NextReply import reply_ok
from external.ext_dict import *
from db.JobsSet import JobsSet


class Reminder(object):

    def __init__(self, from_wxid, job_time, to_user, do_what, from_nickname, repeat, msg_text, is_anony, work_holiday,
                 ext_type, v1, v2, v3, repeat_custom=None):
        self.from_wxid = from_wxid
        self.from_nickname = from_nickname
        self.job_time = job_time
        self.repeat = repeat
        self.repeat_custom = repeat_custom
        self.to_user = to_user
        self.do_what = do_what
        self.msg_text = msg_text
        self.is_anony = is_anony
        self.external_type = ext_type
        self.workday_type = work_holiday
        self.v1 = v1
        self.v2 = v2
        self.v3 = v3
        # private
        self.tail = ''
        self.job_msg = {}
        # build function
        self.build_tail()
        self.build_job_msg()

    def time_until(self):
        day = datetime.strptime(self.job_time, '%Y-%m-%d %H:%M:%S')
        if self.workday_type == 1:
            if int(self.external_type) == 9:
                if not is_workday(day):
                    day = datetime.strptime(datetime.strftime(datetime.today(), '%Y-%m-%d 09:00:00'),
                                            '%Y-%m-%d %H:%M:%S')
            self.job_time = next_workday(day).strftime("%Y-%m-%d %H:%M:%S")
        elif self.workday_type == 2:
            self.job_time = next_holiday(day).strftime("%Y-%m-%d %H:%M:%S")
        return nature_time(self.job_time)

    def build_job_msg(self):
        self.job_msg = {'to_user': self.to_user, 'do_what': self.do_what, 'tail': self.tail,
                        'workday': self.workday_type, 'ext_type': self.external_type, 'v1': self.v1, 'v2': self.v2,
                        'v3': self.v3}
        pass

    def build_tail(self):
        if not self.to_self():
            if self.is_anony:
                self.tail = ' (来自匿名提醒)'
            else:
                self.tail = ' (来自 ' + self.from_nickname + ' 的提醒)'
        if self.repeat and ('@chatroom' not in self.to_user):
            self.tail = '\n\n [@emoji=\\uE10F] 发送“取消提醒”可以取消'

    def do_schedule(self):
        job = RemindScheduler().add_job(self.external_type, self.job_time, self.repeat, self.job_msg, self.from_wxid,
                                        self.msg_text, self.v1, self.v2, self.v3, self.repeat_custom)
        if job == -1:
            return '服务器好像出了点问题，请稍后再试试[@emoji=\\uE058]'
        elif job == -2:
            return '[@emoji=\\uE10F]你已经有15个待提醒事项了，你可以取消一些后再创建。有更多的需求？欢迎私聊开发者申请'
        else:
            job_code = job.get('job_code')
            job_id = job.get('job_id')
            return self.parse_return_msg(job_code, job_id)

    def to_self(self):
        return True if self.from_wxid == self.to_user else False

    def parse_return_msg(self, job_code, job_id):
        next_time = JobsSet().next_run_time(job_id, self.msg_text)
        if next_time:
            first_msg = ''
            first_add = ''
            tail = ''
            if self.repeat:
                first_msg = '第一次'
            if job_code:
                first_add = '\n\n [@emoji=\\uE10F] 你可以发送“我的提醒”来查看你已创建的提醒列表，发送“取消提醒”可以取消'
            sb = '你'
            if not self.to_self():
                if '@chatroom' in self.to_user:
                    sb = '群成员'
                else:
                    sb = 'ta'
            # 检测是否有外部功能提醒
            for key in external_function_dict:
                if key in self.do_what:
                    tail = '\n\n[@emoji=\\uE10F]  如需' + key + '提醒请发送“' \
                           + key + '提醒”进行设置，此条提醒将要提醒的内容为“' + self.do_what + '”'

            return reply_ok(next_time, first_msg, first_add, sb, tail)
        else:
            return '好的，我会准时提醒'
