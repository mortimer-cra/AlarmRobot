#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @File  : RemindDB.py
# @Author: Administrator
# @Date  : 2020/2/4
from db.MongoDBClient import MongoDBClient


class RemindDB(MongoDBClient):
    def get_db(self):
        return self.conn['remind']
