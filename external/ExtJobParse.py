#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/1/19 12:56
# @File    : ExtConsumer.py
from queue import Queue
from remind.WorkDay import is_workday
from datetime import datetime
from external.weather.sojson import get_sojson_weather
from external.news.TianNew import TianNew
from external.news.TianSimpleNews import TianSimpleNews
from external.bus.bus import BusTravelTimeSensor
from external.feiyan.CityFeiyan import CityFeiyan
from external.weibo.WeiboHot import WeiboHot
from external.stock.StockImgK import get_stock_img
from external.fund.FundImg import get_fund_img
from consumer.SentConsumer import sent_queue_msg, build_queue_msg
import time
import logging


def tail_sent_queue(message, msg):
    if message:
        message_ = message + str(msg["tail"])
        users = str(msg["to_user"])
        if ',' in users:
            user_arr = users.split(',')
            for user in user_arr:
                if 'from_user:' in user:
                    from_user = user.split(':')[1]
                    friend_msg = str(len(user_arr) - 1) + '个好友提醒已送达，提醒内容：' + message_.split('(来自')[0]
                    sent_queue_msg(build_queue_msg(from_user, friend_msg))
                else:
                    sent_queue_msg(build_queue_msg(user, message_))
        else:
            sent_queue_msg(build_queue_msg(users, message_))


class ExtJobParse:

    def __init__(self, msg):
        self.msg = msg
        self.build_job()

    def build_job(self):
        ext_type = self.msg.get('ext_type')
        job_kind = {
            '0': self.remind_text_job,
            '1': self.remind_weather_job,
            '3': self.news_job,
            '4': self.bus_job,
            '6': self.weibo_job,
            '7': self.yiqing_job,
            '9': self.excessive_job,
            '5': self.stock_job,
            '10': self.fund_job
        }
        return job_kind.get(str(ext_type))()

    def if_workday(self):
        type_ = self.msg["workday"]
        workday = is_workday(datetime.today())
        if type_ == 0:
            return True
        else:
            if workday and type_ == 1:
                return True
            if not workday and type_ == 2:
                return True
            return False

    def remind_text_job(self):
        try:
            if self.if_workday():
                print('do remind_text_job ' + time.asctime() + ',' + str(self.msg))
                message = '[@emoji=\\u23F0]  ' + str(self.msg["do_what"])
                tail_sent_queue(message, self.msg)
        except Exception as e:
            logging.error(str(e))

    def remind_weather_job(self):
        try:
            if self.if_workday():
                print('do remind_weather_job ' + time.asctime() + ',' + str(self.msg))
                city_message = str(self.msg["v1"])
                weather = get_sojson_weather(city_message)
                tail_sent_queue(weather, self.msg)
        except Exception as e:
            logging.error(str(e))

    def news_job(self):
        try:
            if self.if_workday():
                print('do news_job ' + time.asctime() + ',' + str(self.msg))
                news_type = int(self.msg["v1"])
                if news_type == 1:
                    new_msg = TianSimpleNews().reply_text()
                else:
                    new_msg = TianNew().reply_text(10, news_type)
                tail_sent_queue(new_msg, self.msg)
        except Exception as e:
            logging.error(str(e))

    def bus_job(self):
        try:
            if self.if_workday():
                print('do bus_job ' + time.asctime() + ',' + str(self.msg))
                city_no = self.msg["v1"]
                bus_line = self.msg["v2"]
                bus_order = self.msg["v3"]
                if bus_line:
                    line_no_ = bus_line['line_no']
                    name_ = bus_line['line_name']
                    direction_ = str(bus_line['direction'])
                if all([city_no, line_no_, name_, direction_, bus_order]):
                    bus_msg = BusTravelTimeSensor().update(city_no, line_no_, name_, direction_, bus_order)
                    tail_sent_queue(bus_msg, self.msg)
        except Exception as e:
            logging.error(str(e))

    def weibo_job(self):
        try:
            if self.if_workday():
                print('do weibo_job ' + time.asctime() + ',' + str(self.msg))
                text = WeiboHot().reply_text()
                if text:
                    tail_sent_queue(text, self.msg)
        except Exception as e:
            logging.error(str(e))

    def yiqing_job(self):
        try:
            if self.if_workday():
                print('do yiqing_job ' + time.asctime() + ',' + str(self.msg))
                city_no = self.msg["v1"]
                yiqing_txt = CityFeiyan().reply_text(city_no)
                tail_sent_queue(yiqing_txt, self.msg)
        except Exception as e:
            logging.error(str(e))

    def excessive_job(self):
        try:
            if self.if_workday():
                print('do excessive_job ' + time.asctime() + ',' + str(self.msg))
                # 9点不发
                if datetime.now().hour == 9:
                    return
                message = '[@emoji=\\u23F0]  ' + '久坐提醒时间到啦，站起来喝点水，活动一下吧！'
                tail_sent_queue(message, self.msg)
        except Exception as e:
            logging.error(str(e))

    def stock_job(self):
        try:
            if self.if_workday():
                codes = self.msg["v1"]
                print('do fund_job ' + time.asctime() + ',' + str(self.msg))
                message = '[@emoji=\\uD83D\\uDCC8] 股票分时线提醒（' + codes + ')'
                message_ = message + str(self.msg["tail"])
                users = str(self.msg["to_user"])
                sent_queue_msg(build_queue_msg(users, message_))
                code_arr = codes.split(',')
                for code in code_arr:
                    path = get_stock_img(code)
                    sent_queue_msg(build_queue_msg(users, [], 2, path))
        except Exception as e:
            logging.error(str(e))

    def fund_job(self):
        try:
            if self.if_workday():
                codes = self.msg["v1"]
                print('do fund_job ' + time.asctime() + ',' + str(self.msg))
                message = '[@emoji=\\uD83D\\uDCC8] 基金实时净值走势估算提醒（' + codes + ')'
                message_ = message + str(self.msg["tail"])
                users = str(self.msg["to_user"])
                sent_queue_msg(build_queue_msg(users, message_))
                code_arr = codes.split(',')
                for code in code_arr:
                    path = get_fund_img(code)
                    sent_queue_msg(build_queue_msg(users, [], 2, path))
        except Exception as e:
            logging.error(str(e))
