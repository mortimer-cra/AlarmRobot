#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @File  : Scheduler.py
# @Author: Administrator
# @Date  : 2019/12/11
import logging
import uuid
from schedule.Scheduler import scheduler, TRIGGER_INTERVAL, TRIGGER_DATE, TRIGGER_CRON
from remind.DateEnum import *
from consumer.ExtConsumer import ext_queue
from db.UserJobSet import UserJobSet

logging.basicConfig(level=logging.INFO)


def ext_job(msg):
    ext_queue.put(msg)


class RemindScheduler:

    def __init__(self):
        self.job_id = ''
        self.job_msg_type = 0
        self.job_time = ''
        self.job_repeat = {}
        self.trigger_repeat = ''
        self.job_msg = ''
        self.user_wxid = ''
        self.user_say = ''
        self.v1 = ''
        self.v2 = ''
        self.v3 = ''
        # private
        self.job_corn = {}
        pass

    def add_job(self, job_msg_type, job_time, job_repeat, job_msg, user_wxid, user_say, v1, v2, v3,
                repeat_custom=None):
        self.job_msg_type = job_msg_type
        self.job_time = job_time
        self.job_repeat = job_repeat
        self.job_msg = job_msg
        self.user_wxid = user_wxid
        self.user_say = user_say
        self.v1 = v1
        self.v2 = v2
        self.v3 = v3
        re_flag = 0
        # 校验最大条数
        num = UserJobSet().user_all_num(self.user_wxid)
        if num >= 30:
            return -2
        if num == 0:
            re_flag = 1
        # 生成一个job id
        self.job_id = str(uuid.uuid1()).replace("-", '')
        # 处理job
        if all([self.job_time, self.job_msg, self.user_wxid]):
            try:
                if repeat_custom:
                    # 自定义
                    scheduler.add_job(ext_job, TRIGGER_CRON, hour=repeat_custom,
                                      args=[self.job_msg], id=self.job_id)
                elif self.job_repeat:
                    # 重复
                    self.parse_repeat_time()
                    scheduler.add_job(ext_job, self.trigger_repeat, **self.job_corn,
                                      args=[self.job_msg], id=self.job_id, start_date=self.job_time)
                else:
                    # 单次
                    scheduler.add_job(ext_job, TRIGGER_DATE, run_date=self.job_time,
                                      args=[self.job_msg], id=self.job_id)

                self.add_mongodb(self.job_id)
                return {'job_code': re_flag, 'job_id': self.job_id}
            except Exception as e:
                logging.info('add job exception:', e)
                self.add_mongodb(-1)
        return -1

    def add_mongodb(self, mongo_job_id):
        # user_id + job_id + remark
        mongodb_dic = {'user_id': self.user_wxid, 'job_id': mongo_job_id, 'remark': self.user_say}
        UserJobSet().insert(mongodb_dic)

    def parse_repeat_time(self):
        year_s, mon_s, day_s = self.job_time.split(' ')[0].split('-')
        hour_s, minute_s, second_s = self.job_time.split(' ')[1].split(':')
        job_corn_dict = {'year': year_s, 'month': mon_s, 'day': day_s, 'hour': hour_s,
                         'minute': minute_s, 'second': second_s}
        if self.job_repeat:
            for key in self.job_repeat:
                if self.job_repeat[key] != 1 or REPEAT_KEY_WEEK in self.job_repeat:
                    self.job_corn = self.job_repeat
                    self.trigger_repeat = TRIGGER_INTERVAL
                    return

            if REPEAT_KEY_YEAR in self.job_repeat:
                year_interval = self.job_repeat.get(REPEAT_KEY_YEAR)
                update_dict = {'year': '*/' + str(year_interval)}
            elif REPEAT_KEY_MONTH in self.job_repeat:
                month_interval = self.job_repeat.get(REPEAT_KEY_MONTH)
                del job_corn_dict['year']
                update_dict = {'month': '*/' + str(month_interval)}
            elif REPEAT_KEY_WEEK in self.job_repeat:
                week_interval = self.job_repeat.get(REPEAT_KEY_WEEK)
                del job_corn_dict['year']
                del job_corn_dict['month']
                update_dict = {'week': '*/' + str(week_interval)}
            elif REPEAT_KEY_DAY in self.job_repeat:
                day_interval = self.job_repeat.get(REPEAT_KEY_DAY)
                del job_corn_dict['year']
                del job_corn_dict['month']
                update_dict = {'day': '*/' + str(day_interval)}
            elif REPEAT_KEY_HOUR in self.job_repeat:
                hour_interval = self.job_repeat.get(REPEAT_KEY_HOUR)
                del job_corn_dict['year']
                del job_corn_dict['month']
                del job_corn_dict['day']
                update_dict = {'hour': '*/' + str(hour_interval)}
            elif REPEAT_KEY_MINUTE in self.job_repeat:
                min_interval = self.job_repeat.get(REPEAT_KEY_MINUTE)
                del job_corn_dict['year']
                del job_corn_dict['month']
                del job_corn_dict['day']
                del job_corn_dict['hour']
                update_dict = {'minute': '*/' + str(min_interval)}
            job_corn_dict.update(update_dict)
            self.job_corn = job_corn_dict
            self.trigger_repeat = TRIGGER_CRON


if __name__ == '__main__':
    scheduler.start()
    RemindScheduler().add_job(0, '2019-12-13 10:59:00', {'seconds': 2}, 'hahaha', 'user_wxid', 'user_say')
    while True:
        pass
