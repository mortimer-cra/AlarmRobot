#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @File  : JobsSet.py
# @Author: Administrator
# @Date  : 2020/2/4
from db.MongoDBClient import MongoDBClient
from remind.RemindUtil import nature_time, datetime
from remind.WorkDay import *


class JobsSet(MongoDBClient):

    def get_set(self):
        return self.conn['apscheduler']['jobs']

    def next_run_time(self, job_id, remark):
        find = self.find_one({'_id': job_id})
        if find:
            aps_timestamp = find['next_run_time']
            day = datetime.fromtimestamp(aps_timestamp)
            for key in workday_dict:
                if key in remark:
                    if workday_dict[key] == 1:
                        day = next_workday(day)
                    elif workday_dict[key] == 2:
                        day = next_holiday(day)
            if remark == '久坐提醒' and (not is_workday(datetime.today())):
                day = datetime.strptime(datetime.strftime(datetime.today(), '%Y-%m-%d 09:00:00'), '%Y-%m-%d %H:%M:%S')
                day = next_workday(day)
            return nature_time(day.strftime("%Y-%m-%d %H:%M:%S"))
        return None
