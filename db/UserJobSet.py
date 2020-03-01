#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @File  : UserJobSet.py
# @Author: Administrator
# @Date  : 2020/2/4
from db.RemindDB import RemindDB
from db.JobsSet import JobsSet
from message.SessionDict import *
from schedule.Scheduler import *


class UserJobSet(RemindDB):

    def get_set(self):
        return self.get_db()['user_job']

    # 根据user查询全部的记录
    def find_all(self, user):
        search_dic = {'user_id': user, 'job_id': {'$ne': -1}}
        find_user = self.find(search_dic)
        re_line = ''
        if find_user:
            for li in find_user:
                job_id = li.get('job_id', '')
                remark = li.get('remark')
                if str(job_id).startswith('monitoring_'):
                    re_line += ('[@emoji=\\u2714] ' + remark + '(将在事件触发后提醒)\n')
                else:
                    next_time = JobsSet().next_run_time(job_id, remark)
                    if next_time:
                        re_line += ('[@emoji=\\u2714] ' + remark + '(将在' + next_time + '提醒)\n')
        return re_line

    # 在删的时候加session
    def del_find_all(self, user):
        search_dic = {'user_id': user, 'job_id': {'$ne': -1}}
        find_user = self.find(search_dic)
        re_line = ''
        session_dict_del = {}
        if find_user:
            for lin in find_user:
                num = str(self.index)
                job_id = lin.get('job_id')
                remark = lin.get('remark')
                if str(job_id).startswith('monitoring_'):
                    re_line += (num + '. ' + remark + '(将在事件触发后提醒)\n')
                else:
                    next_time = JobsSet().next_run_time(job_id, remark)
                    if not next_time:
                        continue
                    re_line += (num + '. ' + remark + '(将在' + next_time + '提醒)\n')
                # 装进session
                session_dict_del.update({num: job_id})
                self.index_add()
        if session_dict_del:
            session_dict_del.update({SESSION_TYPE: JOB_DEL, FROM_WXID: user})
            put_session_dict(**session_dict_del)
        return re_line

    # 管理员根据用户删除
    def del_find_all_sys(self, user, from_wxid):
        search_dic = {'user_id': user, 'job_id': {'$ne': -1}}
        find_user = self.find(search_dic)
        re_line = ''
        session_dict_del = {}
        if find_user:
            for lin in find_user:
                num = str(self.index)
                job_id = lin.get('job_id')
                remark = lin.get('remark')
                next_time = JobsSet().next_run_time(job_id, remark)
                if next_time:
                    re_line += (num + '. ' + remark + '(将在' + next_time + '提醒)\n')
                    # 装进session
                    session_dict_del.update({num: job_id})
                    self.index_add()
        if session_dict_del:
            session_dict_del.update({SESSION_TYPE: JOB_DEL_ADMIN, FROM_WXID: from_wxid})
            put_session_dict(**session_dict_del)
        return re_line

    # 管理员删除全部功能提醒
    def del_remark_admin(self, remark):
        search_dic = {'remark': remark, 'job_id': {'$ne': -1}}
        find_remind = self.find(search_dic)
        if find_remind:
            num = 0
            fail_num = 0
            for find in find_remind:
                try:
                    job_id = find.get('job_id')
                    scheduler.remove_job(job_id, 'default')
                    num += 1
                except Exception as e:
                    fail_num += 1
            return remark + ': ' + str(num) + '条已删除,失败' + str(fail_num) + '条'
        return None

    def find_user_jobs(self, user):
        search_dic = {'user_id': user, 'job_id': {'$ne': -1}}
        find_user = self.find(search_dic)
        re_jobs = []
        if find_user:
            for l in find_user:
                job_id = l.get('job_id')
                find = JobsSet().find_one({'_id': job_id})
                if find:
                    re_jobs.append(job_id)
        return re_jobs

    def user_all_num(self, user):
        search_dic = {'user_id': user, 'job_id': {'$ne': -1}}
        find_user = self.find(search_dic)
        re_num = 0
        if find_user:
            for line in find_user:
                job_id = line.get('job_id')
                find = JobsSet().find_one({'_id': job_id})
                if find:
                    re_num += 1
        return re_num
