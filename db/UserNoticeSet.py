#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @File  : UserNoticeSet.py
# @Author: Administrator
# @Date  : 2020/2/14
from db.RemindDB import RemindDB


class UserNoticeSet(RemindDB):

    def get_set(self):
        return self.get_db()['user_notices']

    def insert_notices(self, user, notice_id):
        insert_dic = {'user_id': user, 'notice_id': notice_id}
        self.insert(insert_dic)

    def get_notices(self, user, notice_id):
        search_dic = {'user_id': user, 'notice_id': notice_id}
        return self.find_one(search_dic)

    def del_notices(self, notice_id):
        del_dic = {'notice_id': notice_id}
        self.delete(del_dic)

    def del_notices_user(self, user):
        del_dic = {'user_id': user}
        self.delete(del_dic)
