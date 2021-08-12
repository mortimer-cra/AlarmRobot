#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @File  : UserFriendsSet.py
# @Author: Administrator
# @Date  : 2020/2/4
from db.RemindDB import RemindDB
import uuid
from consumer.SentConsumer import sent_queue_msg, build_queue_msg


class UserFriendsSet(RemindDB):

    def get_set(self):
        return self.get_db()['user_friends']

    def insert_friend(self, user_id, user_name, friends_id, status='1'):
        insert_dic = {'user_id': user_id, 'user_name': user_name, 'friends_id': friends_id, 'status': status}
        self.insert(insert_dic)

    def find_friends(self, user_id):
        friends_arr = []
        search_code = {'user_id': user_id}
        users = self.find(search_code)
        if not users:
            return -1
        for user in users:
            friend_id = user.get('friends_id')
            friend = self.find_one({'friends_id': friend_id, 'user_id': {'$ne': user_id}})
            friend_dic = {'user_id': friend['user_id'], 'user_name': friend['user_name'], 'status': friend['status']}
            friends_arr.append(friend_dic)
        return friends_arr

    def share_add(self, user_id, user_name, share_id, share_name):
        friends_id = str(uuid.uuid1()).replace("-", '')
        self.insert_friend(user_id, user_name, friends_id, '0')
        self.insert_friend(share_id, share_name, friends_id)

    def del_friends(self, user_id):
        search_code = {'user_id': user_id}
        users = self.find(search_code)
        if not users:
            return
        for user in users:
            friend_id = user.get('friends_id')
            self.delete({'friends_id': friend_id})
        pass

    def update_status(self, user_id, user_name):
        dic = {'user_id': user_id, 'status': '0'}
        find = self.find_one(dic)
        if not find:
            return
        friends_id = find.get('friends_id')
        new_dic = {'user_id': user_id, 'user_name': user_name, 'friends_id': friends_id, 'status': '1'}
        self.update(dic, new_dic)
        # 查找邀请者，发送提示
        friend = self.find_one({'friends_id': friends_id, 'user_id': {'$ne': user_id}})
        share_id = friend['user_id']
        share_name = friend['user_name']
        sent_queue_msg(build_queue_msg(share_id, user_name+' 已通过你的分享成为提醒喵的好友，现在你可以发送“好友提醒”来提醒ta了'))
        sent_queue_msg(build_queue_msg(user_id, '你已接受 ' + share_name+' 的名片分享，你可以发送“好友提醒”来提醒ta哦'))


if __name__ == '__main__':
    UserFriendsSet().share_add('111', 'user_name1', 'wxid_8j0iupav1oh21', 'jipian')
    UserFriendsSet().share_add('333', 'user_name3', 'wxid_8j0iupavzoh21', 'jipian')
    UserFriendsSet().share_add('444', 'user_name4', 'wxid_8j0iupaz1oh21', 'jipian')
    UserFriendsSet().update_status('444', 'user_name1')
    UserFriendsSet().update_status('333', 'user_name1')
    friends = UserFriendsSet().find_friends('wxid_8j0iupavz1oh21')
    print(friends)
    # UserFriendsSet().del_friends('222')
