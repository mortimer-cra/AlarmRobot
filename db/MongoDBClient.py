#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @File  : MongoDBClient.py
# @Author: Administrator
# @Date  : 2020/2/4
from pymongo import MongoClient

settings = {
    "ip": '127.0.0.1',  # ip
    "port": 27017,  # 端口
}


class MongoDBClient(object):
    def __init__(self):
        try:
            self.conn = MongoClient(settings["ip"], settings["port"])
        except Exception as e:
            print(e)
        self.index = 1

    def get_client(self):
        return self.conn

    def get_db(self):
        return None

    def get_set(self):
        return None

    def insert(self, dic):
        return self.get_set().insert_one(dic)

    def update(self, dic, newdic):
        return self.get_set().update(dic, newdic)

    def delete(self, dic):
        return self.get_set().remove(dic)

    def find(self, dic):
        return self.get_set().find(dic)

    def find_one(self, dic):
        return self.get_set().find_one(dic)

    def index_add(self):
        self.index += 1
