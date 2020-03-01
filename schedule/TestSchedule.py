#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/12/12 10:37
# @File    : TestSchedule.py
import logging
import time
import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.mongodb import MongoDBJobStore
from apscheduler.executors.pool import ThreadPoolExecutor
from pymongo import MongoClient

mongoDBhost = 'localhost'  # mongodb 服务器
mongoDBport = '27017'  # 端口号

mongoclient = MongoClient(host=['%s:%s' % (mongoDBhost, mongoDBport)])

logging.basicConfig(level=logging.INFO)

jobstores = {
    'mongo': MongoDBJobStore(client=mongoclient)
    # 'default': SQLAlchemyJobStore(url='sqlite:///jobs.sqlite')
}

executors = {
    'default': ThreadPoolExecutor(60)
    # 'processpool': ProcessPoolExecutor(5)
}

job_defaults = {
    'coalesce': True,
    'max_instances': 1
}

scheduler = BackgroundScheduler(jobstores=jobstores, executors=executors, job_defaults=job_defaults)

scheduler.start()


def dateHourRange(beginDateHour, endDateHour):
    dhours = []
    dhour = datetime.datetime.strptime(beginDateHour, '%Y-%m-%d %H:%M:%S')
    date = beginDateHour[:]
    while date <= endDateHour:
        dhours.append(date)
        dhour = dhour + datetime.timedelta(seconds=1)
        date = dhour.strftime('%Y-%m-%d %H:%M:%S')
    return dhours


def job1(msg):
    time.sleep(1)
    print('do time ' + time.asctime() + ',' + msg)


hour_range = dateHourRange('2019-12-12 11:42:00', '2019-12-12 15:03:00')

# scheduler.add_job(job1, 'interval', seconds=2, start_date='2019-12-12 11:19:00', args=['in'])
# scheduler.add_job(job1, 'interval', seconds=2, start_date='2019-12-12 11:19:00', args=['in'])
# scheduler.add_job(job1, 'interval', seconds=1, start_date='2019-12-12 11:19:00', args=['in'])
# for i in range(23, 24):
# #     # scheduler.add_job(job1, 'interval', seconds=1, start_date='2019-12-12 11:42:00', args=['in'])
# #     s = str(i)
# #     id = s + 'a'
# #     dd = 'da' + s
# #     scheduler.add_job(job1, 'date', run_date='2019-12-12 18:08:00', args=[dd], misfire_grace_time=60, jobstore='mongo',
# #                       id=id)
# scheduler.add_job(job1, 'interval', seconds=2, start_date='2019-12-12 18:10:00', args=['in'], id='adw',
#                   jobstore='mongo')

# di = {'seconds':3}
#
#
# scheduler.add_job(job1, trigger='interval', **di, start_date='2019-12-13 10:57:00', args=['in'],
#                   jobstore='mongo')

# scheduler.add_job(job1, 'date', run_date='2019-12-13 17:01:00', args=['dd'], misfire_grace_time=60, jobstore='mongo',
#                   id='id111')


scheduler.add_job(job1, 'cron', start_date=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), args=['dd'], day='*/3',
                  hour='8',
                  id='id111')

while True:
    pass
