#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @File  : UserChatroomSet.py
# @Author: Administrator
# @Date  : 2020/2/4
from db.RemindDB import RemindDB


class UserChatroomSet(RemindDB):

    def get_set(self):
        return self.get_db()['user_chatrooms']

    def insert_chatrooms(self, user, chatroom_id, chatroom_name):
        insert_dic = {'user_id': user, 'chatroom_id': chatroom_id, 'chatroom_name': chatroom_name}
        self.insert(insert_dic)

    def get_chatrooms(self, user):
        search_dic = {'user_id': user}
        return self.find(search_dic)

    def remove(self, chatroom_id):
        del_dic = {'chatroom_id': chatroom_id}
        self.delete(del_dic)
