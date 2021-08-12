#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/12/13 17:09
# @File    : Scheduler.py
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.jobstores.mongodb import MongoDBJobStore
from external.news.TianSimpleNews import *
from external.news.TianNew import *
from db.MongoDBClient import MongoDBClient
from external.fund.RmImgDir import clean_dir
from external.douban.DoubanJob import douban_job
from external.feiyan.FeiyanCache import clean_feiyan_cache

TRIGGER_DATE = 'date'
TRIGGER_INTERVAL = 'interval'
TRIGGER_CALENDARINTERVAL = 'calendarinterval'
TRIGGER_CRON = 'cron'
MISFIRE_GRACE_TIME = 60

jobstores = {
    'default': MongoDBJobStore(client=MongoDBClient().get_client())
}

executors = {
    'default': ThreadPoolExecutor(30)
}

job_defaults = {
    'coalesce': False,
    'max_instances': 3,
    'misfire_grace_time': MISFIRE_GRACE_TIME,
}

scheduler = BackgroundScheduler(jobstores=jobstores, executors=executors, job_defaults=job_defaults)
scheduler.start()

# news schedule
cache_new_simple_id = 'cache_new_simple_id'
cache_new_id = 'cache_new_id'

new_job_id = {cache_new_simple_id, cache_new_id}
for new_job in new_job_id:
    try:
        scheduler.remove_job(new_job, 'default')
    except Exception as e:
        print(str(e))
scheduler.add_job(cache_new_simple_job, "cron", hour=5, minute=0, id=cache_new_simple_id)
scheduler.add_job(cache_new_job, "cron", hour=5, minute=1, id=cache_new_id)

# schedule douban
douban_job_id = 'douban_job_id'
try:
    scheduler.remove_job(douban_job_id, 'default')
except Exception as e:
    print(str(e))
scheduler.add_job(douban_job, "interval", minutes=30, id=douban_job_id)

# delete img_dir
clean_dir_id = 'clean_dir_id'
try:
    scheduler.remove_job(clean_dir_id, 'default')
except Exception as e:
    print(str(e))
scheduler.add_job(clean_dir, "cron", hour=3, minute=5, id=clean_dir_id)


# foreign yiqing
foreign_yiqing_id = 'foreign_yiqing_id'
try:
    scheduler.remove_job(foreign_yiqing_id, 'default')
except Exception as e:
    print(str(e))
scheduler.add_job(clean_feiyan_cache, "interval", minutes=10, id=foreign_yiqing_id)
