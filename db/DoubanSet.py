#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @File  : DoubanSet.py
# @Author: Administrator
# @Date  : 2020/3/2
from db.RemindDB import RemindDB


class DoubanSet(RemindDB):

    def get_set(self):
        return self.get_db()['douban_new']

    def insert_douban(self, movie_id, title, rate, url, status=0):
        insert_dic = {'movie_id': movie_id, 'title': title, 'rate': rate, 'url': url, 'status': status}
        self.insert(insert_dic)

    def get_movie(self, movie_id):
        search_dic = {'movie_id': movie_id}
        return self.find_one(search_dic)

    def get_unsent(self):
        search_dic = {'status': 0}
        return self.find(search_dic)

    def update_movie(self, movie_id):
        dic = {'movie_id': movie_id}
        new_dic = self.get_movie(movie_id)
        new_dic['status'] = 1
        self.update(dic, new_dic)
