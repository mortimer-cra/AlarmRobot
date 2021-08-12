#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/12/10 16:38
# @File    : InitJieba.py
import jieba
import os
from message.FriendDict import friend_dict

jieba.initialize()

# 增加不可分词
for word in open(os.path.dirname(__file__) + '/resource/ignore_words.txt', 'r', encoding="utf-8"):
    if word.strip():
        # Wait until #350 of jieba is fixed
        jieba.add_word(word.strip(), 1e-9)

# 增加自定义分词
# jieba.add_word(u'下月', 9999)
jieba.add_word(u'我', 9999)
jieba.add_word(u'工作日', 9999)
jieba.add_word(u'下个', 9999)
jieba.add_word(u'这个', 9999)
jieba.add_word(u'这', 9999)
jieba.add_word(u'下', 9999)


# 初始化好友名称分词（待加入更新）
def init_friend_jieba():
    print('enter add_friend_jieba ...')
    for key in friend_dict:
        jieba.add_word(key, 9999)


# 增加
def add_jieba(key):
    jieba.add_word(key, 9999)
