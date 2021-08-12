#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @File  : DoubanJob.py
# @Author: Administrator
# @Date  : 2020/3/2
from external.douban.DoubanSpider import douban_spider, DoubanSet
from db.UserJobSet import UserJobSet
from consumer.SentConsumer import *
from datetime import datetime


def douban_job():
    try:
        douban_spider()
        unsent = DoubanSet().get_unsent()
        if not unsent.count():
            return None
        movie_message = ''
        for movie in unsent:
            movie_id = movie.get('movie_id')
            title = movie.get('title')
            rate = movie.get('rate')
            url = movie.get('url')
            movie_message += '\n\n' + title + '（' + rate + '分）\n' + url
            # 更新状态
            DoubanSet().update_movie(movie_id)

        # 开始推送
        message = '[@emoji=\\uD83D\\uDCFD][@emoji=\\uFE0F] 豆瓣新片提醒（' + str(
            datetime.now().strftime('%H:%M:%S')) + '）\n' \
                                                   '又有7.5分以上的电影出现啦，快去看看吧' + movie_message
        message += '\n\n [@emoji=\\uE10F] 发送“取消提醒”可以取消'
        users = UserJobSet().find({'job_id': 'monitoring_douban_rank'})
        if users.count():
            for user in users:
                sent_queue_msg(build_queue_msg(user.get('user_id'), message))
    except Exception as e:
        print(str(e))


if __name__ == '__main__':
    douban_job()
