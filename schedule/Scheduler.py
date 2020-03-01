#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/12/13 17:09
# @File    : Scheduler.py
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.jobstores.mongodb import MongoDBJobStore
from schedule.MongoDBUtil import MongoDBUtil
from external.news.TianSimpleNews import clean_job_simple
from external.news.TianNew import clean_job

TRIGGER_DATE = 'date'
TRIGGER_INTERVAL = 'interval'
TRIGGER_CALENDARINTERVAL = 'calendarinterval'
TRIGGER_CRON = 'cron'
MISFIRE_GRACE_TIME = 60

jobstores = {
    'default': MongoDBJobStore(client=MongoDBUtil().get_client())
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

# news clean schedule
scheduler.add_job(clean_job_simple, "cron", hour=0, minute=0)
scheduler.add_job(clean_job, "cron", hour=0, minute=1)
