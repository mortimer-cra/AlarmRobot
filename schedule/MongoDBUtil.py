#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @File  : MongoDBUtil.py
# @Author: Administrator
# @Date  : 2019/12/12
from pymongo import MongoClient
from remind_parse.RemindUtil import nature_time, datetime
from message.SessionDict import *
from schedule.WorkDay import *

settings = {
    "ip": '127.0.0.1',  # ip
    "port": 27017,  # 端口
    "db_name": "remind",  # 数据库名字，没有则自动创建
    "set_name": "user_job"  # 集合名字，没有则自动创建
}

apscheduler = {
    "db_name": "apscheduler",  # 数据库名字，没有则自动创建
    "set_name": "jobs"  # 集合名字，没有则自动创建
}


class MongoDBUtil(object):
    def __init__(self):
        try:
            self.conn = MongoClient(settings["ip"], settings["port"])
        except Exception as e:
            print(e)
        self.db = self.conn[settings["db_name"]]
        self.my_set = self.db[settings["set_name"]]
        self.apscheduler_db = self.conn[apscheduler["db_name"]]
        self.apscheduler_set = self.apscheduler_db[apscheduler["set_name"]]
        self.index = 1

    def get_client(self):
        return self.conn

    # 插入
    def insert(self, dic):
        self.my_set.insert_one(dic)

    # 更新
    def update(self, dic, newdic):
        self.my_set.update(dic, newdic)

    # 删除
    def delete(self, dic):
        self.my_set.remove(dic)

    # remind查找
    def db_find(self, dic):
        return self.my_set.find(dic)

    # apscheduler查找
    def apscheduler_find_one(self, dic):
        return self.apscheduler_set.find_one(dic)

    # next_run_time
    def next_run_time(self, job_id, remark):
        find = self.apscheduler_find_one({'_id': job_id})
        if find:
            aps_timestamp = find['next_run_time']
            day = datetime.fromtimestamp(aps_timestamp)
            for key in workday_dict:
                if key in remark:
                    if workday_dict[key] == 1:
                        day = next_workday(day)
                    elif workday_dict[key] == 2:
                        day = next_holiday(day)
            return nature_time(day.strftime("%Y-%m-%d %H:%M:%S"))
        return None

    # 根据user查询全部的记录
    def find_all(self, user):
        search_dic = {'user_id': user, 'job_id': {'$ne': -1}}
        find_user = self.db_find(search_dic)
        re_line = ''
        if find_user:
            for line in find_user:
                num = str(self.index)
                job_id = line.get('job_id')
                remark = line.get('remark')
                next_time = self.next_run_time(job_id, remark)
                if next_time:
                    re_line += (num + '、' + remark + '(将在' + next_time + '提醒)\n')
                    self.index_add()
        return re_line

    # 在删的时候加session
    def del_find_all(self, user):
        search_dic = {'user_id': user, 'job_id': {'$ne': -1}}
        find_user = self.db_find(search_dic)
        re_line = ''
        session_dict = {}
        if find_user:
            for line in find_user:
                num = str(self.index)
                job_id = line.get('job_id')
                remark = line.get('remark')
                next_time = self.next_run_time(job_id, remark)
                if next_time:
                    re_line += (num + '、' + remark + '(将在' + next_time + '提醒)\n')
                    # 装进session
                    session_dict.update({num: job_id})
                    self.index_add()
        if session_dict:
            session_dict.update({SESSION_TYPE: JOB_DEL, FROM_WXID: user})
            put_session_dict(**session_dict)
        return re_line

    def user_all_num(self, user):
        search_dic = {'user_id': user, 'job_id': {'$ne': -1}}
        find_user = self.db_find(search_dic)
        re_num = 0
        if find_user:
            for line in find_user:
                job_id = line.get('job_id')
                find = self.apscheduler_find_one({'_id': job_id})
                if find:
                    re_num += 1
        return re_num

    def index_add(self):
        self.index += 1


