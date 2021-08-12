#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @File  : Test.py
# @Author: Administrator
# @Date  : 2020/2/4
from db.UserJobSet import UserJobSet

if __name__ == '__main__':
    search_dic = {'user_id': 'weiboikmd'}
    find = UserJobSet().user_all_num(search_dic)
    print(find)
    for line in find:
        print(line)
    pass
