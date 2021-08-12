#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2019/12/10 16:27
# @File    : Parser.py
import arrow
import jieba.posseg as pseg
from remind.DateEnum import *
from dateutil.relativedelta import relativedelta
from time_nlp.StringPreHandler import StringPreHandler
from message.FriendDict import friend_dict
from message.SessionDict import *
from remind.ParseError import ParseError
from message.ReplyEnum import ReplyEnum
from remind.Reminder import *
from external.news.NewsChannel import NewsChannel
from remind.WorkDay import workday_dict
from external.ext_dict import *
from external.weibo.WeiboHot import WeiboHot
from db.UserJobSet import UserJobSet


class Parser(object):
    afternoon = None
    noon = None
    do_what = ''
    words = []

    def __init__(self):
        # return
        self.from_nickname = ''
        self.from_wxid = ''
        self.msg_text = ''
        self.friend_nickname = ''
        self.to_user = ''
        self.job_time = ''
        self.do_what = ''
        self.is_anony = False
        self.work_holiday = 0
        self.ext_type = 0
        self.v1 = ''
        self.v2 = ''
        self.v3 = ''
        # about parse
        self.idx = 0
        now_ = arrow.now()
        self.now = now_
        self.now_right_compare = now_
        self.time_fields = {}
        self.parse_beginning = 0
        self.time_delta_fields = {}
        self.repeat = {}
        # temp
        self.remove_time_text = []
        self.ext_key = ''

    def parse(self, text, from_wxid, from_nickname, to_user=''):
        self.msg_text = text
        # 查找是否有朋友
        self.find_friend()
        self.from_nickname = from_nickname
        self.from_wxid = from_wxid
        self.to_user = to_user
        try:
            self.parse_time(text)
        except ValueError as e:
            return str(e)
        self.parse_other()
        # 在这里处理缺失项 三个必要项 缺失一个返回交互信息 放session 缺失一个以上直接返回
        if all([self.job_time, self.to_user, self.do_what]):
            if self.friend_repeat():
                return ReplyEnum.friend_repeat_limit + '，请重新发起'
            reminder_dict = self.build_reminder_dict()
            reminder = Reminder(**reminder_dict)
            return reminder.do_schedule()
        elif all([self.job_time, self.to_user]):
            self.put_missing_type(REMIND_DO_MISSING)
            if not self.is_oneself():
                if self.repeat and '@chatroom' not in self.to_user:
                    session_dict.pop(self.from_wxid)
                    return ReplyEnum.friend_repeat_limit
                return ReplyEnum.non_do_something_friend
            return ReplyEnum.non_do_something
        elif all([self.to_user, self.do_what]):
            self.put_missing_type(REMIND_DATE_MISSING)
            if not self.is_oneself():
                return ReplyEnum.date_parse_error_friend
            return ReplyEnum.date_parse_error
        elif all([self.job_time, self.do_what]):
            self.put_missing_type(REMIND_WHO_MISSING)
            return ReplyEnum.date_parse_error_who
        else:
            return ReplyEnum.parse_remind_error_example

    def parse_time(self, text):
        text = text.replace('每晚', '每天晚上')
        self.words = pseg.lcut(StringPreHandler.numberTranslator(text), HMM=False)
        while self.has_next():

            if (self.time_fields != {} or self.time_delta_fields != {}) and (self.current_word() == '提醒'):
                while self.has_next():
                    self.remove_time_text.append(self.current_word())
                    self.advance()
                break

            self.parse_beginning = self.get_index()
            self.consume_repeat()

            self.consume_year_period() \
            or self.consume_month_period() \
            or self.consume_day_period()

            self.consume_weekday_period() \
            or self.consume_hour_period() \
            or self.consume_minute_period() \
            or self.consume_second_period()

            self.consume_year() \
            or self.consume_month() \
            or self.consume_day()

            self.consume_hour()
            self.consume_word(u'前', u'之前', u'以前')
            self.consume_word(u'时候', u'的时候')
            if self.get_index() != self.parse_beginning:
                try:
                    self.now += relativedelta(**self.time_delta_fields)
                    self.now = self.now.replace(**self.time_fields)
                except ValueError:
                    raise ParseError(ReplyEnum.parse_error_range)
            else:
                self.remove_time_text.append(self.current_word())
                self.advance()
        # 开始校验
        if self.now:
            if self.repeat:
                if self.now_right_compare >= self.now:
                    self.now += relativedelta(**self.repeat)
                    self.now = self.now.replace(**self.time_fields)
            if self.now_right_compare > self.now:
                raise ParseError(ReplyEnum.dead_time)
            if self.now_right_compare != self.now:
                self.job_time = self.now.format("YYYY-MM-DD HH:mm:ss")
                return {'job_time': self.job_time, 'repeat': self.repeat}
        return None

    def parse_other(self):
        self.words = self.remove_time_text
        self.idx = 0
        while self.has_next():
            if self.consume_word_other(u'匿名'):
                self.is_anony = True
            self.consume_word_other(u'准时')
            if self.consume_word_other(u'提醒'):
                if self.has_next():
                    if not self.to_user:
                        if self.words[self.idx] == u'我':
                            self.to_user = self.from_wxid
                            self.advance()
                        elif self.words[self.idx] == self.friend_nickname:
                            self.to_user = friend_dict[self.friend_nickname]['id_']
                            self.advance()
            else:
                self.do_what = self.do_what + self.words[self.idx]
                self.advance()

    def parse_ext(self, text, from_wxid, from_nickname, ext_key):
        self.msg_text = text
        self.from_nickname = from_nickname
        self.from_wxid = from_wxid
        self.ext_key = ext_key
        # 像 天气提醒 这样的默认提醒自己
        self.to_user = from_wxid
        return self.build_ext()

    def build_ext(self):
        ext_kind = {
            WEATHER: self.ext_weather,
            NEWS: self.ext_news,
            BUS: self.ext_bus,
            YIQING: self.ext_yq,
            WEIBO: self.ext_weibo,
            DOUBAN: self.douban,
            EXCESSIVE_SITTING: self.excessive,
            STOCK: self.stock,
            FUND: self.fund
        }
        return ext_kind.get(self.ext_key, self.ext_default)()

    def ext_weather(self):
        self.put_missing_type(WEATHER_CITY_MISSING)
        return ReplyEnum.weather_city

    def ext_news(self):
        channel = ''
        for value in NewsChannel:
            channel += str(value.value) + ' ' + value.name + '\n'

        self.put_missing_type(NEWS_CHANNEL)
        return ReplyEnum.news_channel + channel

    def ext_bus(self):
        self.put_missing_type(BUS_CITY)
        return ReplyEnum.bus_city

    def ext_yq(self):
        self.put_missing_type(YIQING_CITY)
        return '请告诉我你的城市'

    def ext_weibo(self):
        reminder_dict = self.build_reminder_dict()
        reminder_dict[SESSION_TYPE] = REMIND_DATE_MISSING
        reminder_dict['ext_type'] = external_function_dict[WEIBO]
        put_session_dict(**reminder_dict)
        text = WeiboHot().reply_text()
        if text:
            return [text, ReplyEnum.date_parse_error_repeat]
        return ReplyEnum.date_parse_error_repeat

    def douban(self):
        find_dic = {'user_id': self.from_wxid, 'job_id': 'monitoring_douban_rank'}
        find = UserJobSet().find(find_dic)
        if find.count():
            return '豆瓣新片提醒已经在你的提醒列表了\n\n[@emoji=\\uE10F] 你可以发送“我的提醒”查看你的提醒列表哦'
        insert_dic = {'user_id': self.from_wxid, 'job_id': 'monitoring_douban_rank', 'remark': '豆瓣新片提醒'}
        UserJobSet().insert(insert_dic)
        return '已为你添加豆瓣新片提醒，当有7.5分以上的电影出现在豆瓣电影（https://dwz.cn/8ty0QDkx）我将会第一时间提醒你\n\n' \
               '[@emoji=\\uE10F]你可以发送“取消提醒”来取消提醒'

    def excessive(self):
        reminder_dict = self.build_reminder_dict()
        reminder_dict[SESSION_TYPE] = REMIND_DATE_MISSING
        reminder_dict['work_holiday'] = 1
        reminder_dict['ext_type'] = external_function_dict[EXCESSIVE_SITTING]
        # reminder_dict['do_what'] = '久坐提醒\n\n喝一点水，站起来活动一下吧'
        put_session_dict(**reminder_dict)
        return '提醒喵会在每个法定工作日的工作时间（早9点到晚6点）以你设定频率进行久坐提醒，现在来对我说一个提醒频率吧。（请只回复时间频率）\n\n' \
               '[@emoji=\\uE10F]你可以这样告诉我:“每小时”、“每两个小时” ...'

    def stock(self):
        reminder_dict = self.build_reminder_dict()
        reminder_dict[SESSION_TYPE] = STOCK_CODE
        reminder_dict['work_holiday'] = 1
        put_session_dict(**reminder_dict)
        return '请告诉我股票代码，多个用逗号隔开'

    def fund(self):
        reminder_dict = self.build_reminder_dict()
        reminder_dict[SESSION_TYPE] = FUND_CODE
        reminder_dict['work_holiday'] = 1
        put_session_dict(**reminder_dict)
        return '请告诉我基金代码，多个用逗号隔开'

    def ext_default(self):
        return '近期上线，请关注提醒喵朋友圈更新动态~'

    def find_friend(self):
        for key in friend_dict:
            if key in self.msg_text:
                self.friend_nickname = key
                break
        self.msg_text = self.msg_text.replace(' ', '')

    def friend_repeat(self):
        if not self.is_oneself() and '@chatroom' not in self.to_user:
            if self.repeat:
                return True
        return False

    def is_oneself(self):
        if self.from_wxid == self.to_user:
            return True
        else:
            return False

    def put_missing_type(self, type_session):
        reminder_dict = self.build_reminder_dict()
        reminder_dict[SESSION_TYPE] = type_session
        put_session_dict(**reminder_dict)

    def build_reminder_dict(self):
        return {
            'from_wxid': self.from_wxid,
            'job_time': self.job_time,
            'to_user': self.to_user,
            'do_what': self.do_what,
            'from_nickname': self.from_nickname,
            'repeat': self.repeat,
            'msg_text': self.msg_text,
            'is_anony': self.is_anony,
            'work_holiday': self.work_holiday,
            'ext_type': self.ext_type,
            'v1': self.v1,
            'v2': self.v2,
            'v3': self.v3
        }

    def consume_repeat(self):
        beginning = self.get_index()
        if self.consume_word(u'每', u'每隔'):
            self.consume_word(u'间隔')
            repeat_count = self.consume_digit()
            if repeat_count is None:
                repeat_count = 1
            if repeat_count > 100:
                raise ParseError(ReplyEnum.parse_error_range)
            self.consume_word(u'个')
            # 工作日
            self.consume_word(u'法定')
            if self.current_word() in workday_dict:
                self.work_holiday = workday_dict[self.current_word()]
            if self.consume_word(u'年'):
                if repeat_count > 1:
                    raise ParseError(ReplyEnum.month_yeat_repeat)
                self.repeat[REPEAT_KEY_YEAR] = repeat_count
                self.consume_month()
                return self.get_index() - beginning
            elif self.consume_word(u'月'):
                if repeat_count > 1:
                    raise ParseError(ReplyEnum.month_yeat_repeat)
                self.repeat[REPEAT_KEY_MONTH] = repeat_count
                self.consume_day()
                return self.get_index() - beginning
            elif self.consume_word(u'天', u'工作日', u'节假日'):
                # Set repeat first so it can be used in consume_hour()
                self.repeat[REPEAT_KEY_DAY] = repeat_count
                if not self.consume_hour():
                    self.time_fields['hour'] = DEFAULT_HOUR
                    self.time_fields['minute'] = DEFAULT_MINUTE
                    self.time_fields['second'] = DEFAULT_SECOND
                return self.get_index() - beginning
            elif self.consume_word(u'周', u'星期', u'礼拜'):
                # elif self.current_word() in (u'周', u'星期', u'礼拜'):
                self.repeat[REPEAT_KEY_WEEK] = repeat_count
                # 每周周五
                if self.peek_next_word() in (u'周', u'星期', u'礼拜'):
                    self.consume_word(u'周', u'星期', u'礼拜')
                # 每（一）周五  每两周
                weekday = None
                if self.consume_word(u'日', u'天'):
                    weekday = 6
                elif self.consume_digit(False):
                    weekday = self.consume_digit() - 1
                    if not (0 <= weekday <= 6):
                        raise ParseError(ReplyEnum.parse_error_range + '："周' + str(weekday) + '",请尽量在时间前加上“早上” “晚上”等装饰')
                if weekday is not None:
                    self.time_delta_fields['weekday'] = weekday
                    self.time_delta_fields['days'] = 1
                else:
                    # 每两周
                    pass
                # if self.consume_weekday_period():
                #     return self.get_index() - beginning
                return self.get_index() - beginning
            elif self.consume_word(u'小时'):
                self.consume_minute()
                self.repeat[REPEAT_KEY_HOUR] = repeat_count
                return self.get_index() - beginning
            elif self.consume_word(u'半小时') or (self.consume_word(u'半个') and self.consume_word(u'小时', u'钟头')):
                self.time_delta_fields['hours'] = 0
                self.time_delta_fields['minutes'] = 30
                self.repeat[REPEAT_KEY_MINUTE] = 30
                return self.get_index() - beginning
            elif self.consume_word(u'分', u'分钟'):
                if repeat_count < 20:
                    raise ParseError('20分钟以下的事情我相信你是可以自己记住的')
                else:
                    self.repeat[REPEAT_KEY_MINUTE] = repeat_count
                    return self.consume_minute()
            elif self.consume_word(u'秒', u'秒钟'):
                raise ParseError('20分钟以下的事情我相信你是可以自己记住的')
            # elif self.consume_word(u'工作日'):
            #     raise ParseError(ReplyEnum.parse_error_unfinished)
        self.set_index(beginning)
        return 0

    def consume_year(self):
        beginning = self.get_index()
        year = self.consume_digit()
        if year is None or not self.consume_word(u'年', '-', '/', '.'):
            self.set_index(beginning)
            return 0
        if self.consume_month():
            if year > 3000:
                raise ParseError(ReplyEnum.parse_error_range)
            if year < self.now.year:
                raise ParseError(ReplyEnum.parse_error_range)
            self.time_fields['year'] = year
            return self.get_index() - beginning
        return 0

    def consume_month(self):
        beginning = self.get_index()
        if self.consume_word(u'农历', u'阴历'):
            print(u'/:no亲，暂不支持设置农历提醒哦~')
            raise ParseError(ReplyEnum.parse_error_unfinished)
        if self.consume_word(u'工作日', u'节假日'):
            raise ParseError(ReplyEnum.parse_repeat_workday)
        month = self.consume_digit()
        if month is None or not self.consume_word(u'月', '-', '/', '.'):
            self.set_index(beginning)
            return 0
        if month > 12:
            raise ParseError(ReplyEnum.parse_error_range)
        if self.consume_day():
            self.time_fields['month'] = month
            return self.get_index() - beginning
        self.set_index(beginning)
        return 0

    def consume_day(self):
        beginning = self.get_index()
        if self.current_word().endswith(u'节'):
            print(u'暂不支持各种节假日提醒哦~')
            raise ParseError(ReplyEnum.parse_error_unfinished)
        day = self.consume_digit()
        if day is None or (not self.consume_word(u'日', u'号') and beginning == self.parse_beginning):
            # If not in a sub-parse and not ends with ('日', '号')
            self.set_index(beginning)
            return 0
        if day > 31:
            raise ParseError(ReplyEnum.parse_error_range)
        self.time_fields['day'] = day
        # 2016年12月14日周三在上海举办的2016 Google 开发者大会
        # 2016年12月14日(周三)在上海举办的2016 Google 开发者大会
        self.consume_word(u'(', u'（')
        if self.consume_word(u'周', u'星期'):
            self.consume_word(u'日', u'天') or self.consume_digit()
            self.consume_word(u')', u'）')
        # set default time
        if not self.consume_hour():
            self.time_fields['hour'] = DEFAULT_HOUR
            self.time_fields['minute'] = DEFAULT_MINUTE
            self.time_fields['second'] = DEFAULT_SECOND
        self.exclude_time_range(self.consume_day)
        return self.get_index() - beginning

    def consume_hour(self):
        beginning1 = self.get_index()
        if self.consume_word(u'凌晨', u'半夜', u'夜里', u'深夜'):
            self.afternoon = False
            # self.time_delta_fields['days'] = 1
            self.time_fields['hour'] = 0
            self.time_fields['minute'] = DEFAULT_MINUTE
            self.time_fields['second'] = DEFAULT_SECOND
        elif self.consume_word(u'早', u'早上', u'早晨', u'今早', u'上午'):
            self.afternoon = False
            self.time_fields['hour'] = DEFAULT_HOUR
            self.time_fields['minute'] = DEFAULT_MINUTE
            self.time_fields['second'] = DEFAULT_SECOND
        elif self.consume_word(u'中午'):
            self.afternoon = False
            self.noon = True
            self.time_fields['hour'] = 12
            self.time_fields['minute'] = DEFAULT_MINUTE
            self.time_fields['second'] = DEFAULT_SECOND
        elif self.consume_word(u'下午'):
            self.afternoon = True
            self.time_fields['hour'] = 14
            self.time_fields['minute'] = DEFAULT_MINUTE
            self.time_fields['second'] = DEFAULT_SECOND
        elif self.consume_word(u'傍晚'):
            self.afternoon = True
            self.time_fields['hour'] = 18
            self.time_fields['minute'] = DEFAULT_MINUTE
            self.time_fields['second'] = DEFAULT_SECOND
        elif self.consume_word(u'晚上', u'今晚'):
            self.afternoon = True
            self.time_fields['hour'] = 20
            self.time_fields['minute'] = DEFAULT_MINUTE
            self.time_fields['second'] = DEFAULT_SECOND

        beginning2 = self.get_index()
        hour = self.consume_digit()
        if hour is None or not self.consume_word(u'点', u'点钟', ':', u'：', u'.', u'時', u'时'):
            self.set_index(beginning2)
            # Assert fails
            return self.get_index() - beginning1
        if self.afternoon and hour == 0:  # special case for "晚上零点"
            self.time_delta_fields['days'] = 1
        elif hour < 12:
            if self.afternoon or (self.now.hour >= 12 and not self.time_fields
                                  and not self.time_delta_fields and not self.repeat) or (hour == 1 and self.noon):
                hour += 12
        if not (0 <= hour <= 24):
            raise ParseError(ReplyEnum.parse_error_range)
        self.time_fields['hour'] = hour
        if (self.afternoon and hour == 12) or hour == 24:  # special case for "晚上12点"
            raise ParseError('[@emoji=\\uE10F] 没有解析到时间，如要表达0点请用“晚上0点”')
        if not self.consume_minute():
            self.time_fields['minute'] = DEFAULT_MINUTE
            self.time_fields['second'] = DEFAULT_SECOND
        self.exclude_time_range(self.consume_hour)
        return self.get_index() - beginning1

    # consume_minute should not be called by parser directly
    def consume_minute(self):
        beginning = self.get_index()
        minute = self.consume_digit()
        if minute is not None:
            if not (0 <= minute <= 60):
                raise ParseError(ReplyEnum.parse_error_range)
            if self.current_word() == '刻':
                self.advance(1)
                self.time_fields['minute'] = 15
            elif self.current_word() == '刻':
                self.advance(1)
                self.time_fields['minute'] = 45
            else:
                self.time_fields['minute'] = minute
                self.consume_word(u'分', u'分钟', ':')
                self.consume_second()
        elif self.consume_word('半'):
            self.time_fields['minute'] = 30
        return self.get_index() - beginning

    def consume_second(self):
        beginning = self.get_index()
        second = self.consume_digit()
        if second is not None:
            if self.consume_word(u'秒', u'秒钟'):
                if not (0 <= second <= 60):
                    raise ParseError(ReplyEnum.parse_error_range)
                self.time_fields['second'] = second
                return self.get_index() - beginning
        self.set_index(beginning)
        return 0

    def exclude_time_range(self, next_expectation):
        range_index = self.get_index()
        if self.consume_word(u'到', u'至', u'-', u'~'):
            if next_expectation():
                raise ParseError(ReplyEnum.parse_time_range)
        self.set_index(range_index)

    def consume_year_period(self):
        beginning = self.get_index()
        if self.consume_word(u'今年'):
            self.time_delta_fields['years'] = 0
        elif self.consume_word(u'明年'):
            self.time_delta_fields['years'] = 1
        elif self.consume_word(u'后年'):
            self.time_delta_fields['years'] = 2
        else:
            tmp = self.consume_digit()
            if tmp is not None and self.current_word() == u'年' and self.peek_next_word() in (u'后', u'以后', u'之后'):
                self.time_delta_fields['years'] = tmp
                self.advance(2)
        if 'years' not in self.time_delta_fields:
            self.set_index(beginning)
            return 0
        self.consume_word(u'的')
        if self.time_delta_fields['years'] >= 100:
            raise ParseError(ReplyEnum.parse_error_range)
        self.consume_month()
        return self.get_index() - beginning

    def consume_month_period(self):
        beginning = self.get_index()
        if self.current_word() in (u'这', u'这个') and self.peek_next_word() == '月':
            self.consume_word(u'这', u'这个')
            self.consume_word(u'月')
            self.time_delta_fields['months'] = 0
        elif self.current_word() in (u'下', u'下个') and self.peek_next_word() == '月':
            self.consume_word(u'下', u'下个')
            self.consume_word(u'月')
            self.time_delta_fields['months'] = 1
        elif self.current_word().isdigit():
            tmp = self.consume_digit()
            self.consume_word(u'个')
            if self.current_word() == u'月' and self.peek_next_word() in (u'后', u'以后', u'之后'):
                self.time_delta_fields['months'] = tmp
                self.advance(2)
        if 'months' not in self.time_delta_fields:
            self.set_index(beginning)
            return 0
        self.consume_word(u'的')
        if self.time_delta_fields['months'] > 100:
            raise ParseError(ReplyEnum.parse_error_range)
        self.consume_day()  # 下个月五号
        return self.get_index() - beginning

    def consume_day_period(self):
        beginning = self.get_index()
        has_hour = False
        hour = DEFAULT_HOUR
        days = None
        if self.consume_word(u'今天'):
            days = 0
        elif self.consume_word(u'今早'):
            days = 0
            self.afternoon = False
        elif self.consume_word(u'今晚'):
            days = 0
            self.afternoon = True
            hour = 20
        elif self.consume_word(u'明天', u'明日', u'明儿'):
            days = 1
        elif self.consume_word(u'明早'):
            days = 1
            self.afternoon = False
        elif self.consume_word(u'明晚'):
            days = 1
            self.afternoon = True
            hour = 20
        elif self.consume_word(u'后天'):
            days = 2
        elif self.consume_word(u'大后天'):
            days = 3
        else:
            tmp = self.consume_digit()
            if tmp is not None and self.consume_word(u'天'):
                if self.consume_word(u'后', u'以后', u'之后'):
                    days = tmp
                elif self.consume_hour_period():
                    days = tmp
                    has_hour = True
        if days is None:
            self.set_index(beginning)
            return 0
        if days > 1000:
            raise ParseError(ReplyEnum.parse_error_range)
        self.time_delta_fields['days'] = days
        # 明天(周四)晚上19点
        self.consume_word(u'(', u'（')
        if self.consume_word(u'周', u'星期'):
            self.consume_word(u'日', u'天') or self.consume_digit()
            self.consume_word(u')', u'）')
        # 两天后下午三点
        if not has_hour and not self.consume_hour():
            self.time_fields['hour'] = hour
            self.time_fields['minute'] = DEFAULT_MINUTE
            self.time_fields['second'] = DEFAULT_SECOND
        return self.get_index() - beginning

    def consume_weekday_period(self):
        beginning = self.get_index()
        weekday = None
        week_delta = 0
        next_week = 0
        if self.current_word() in (u'这', u'这个') and self.peek_next_word() in (u'周', u'星期', u'礼拜'):
            self.consume_word(u'这', u'这个')
        if self.current_word() in (u'下', u'下个') and self.peek_next_word() in (u'周', u'星期', u'礼拜'):
            self.consume_word(u'下', u'下个')
            next_week = 1
        if self.consume_word(u'周', u'星期', u'礼拜'):
            if self.peek_next_word() in (u'周', u'星期', u'礼拜'):
                self.consume_word(u'周', u'星期', u'礼拜')
            if self.consume_word(u'日', u'天'):
                weekday = 6
            elif self.consume_digit(False):
                weekday = self.consume_digit() - 1
                if not (0 <= weekday <= 6):
                    raise ParseError(ReplyEnum.parse_error_range)
                if next_week:
                    if weekday > self.now.weekday():
                        week_delta = 1

        elif self.current_word().isdigit():
            tmp = self.consume_digit()
            self.consume_word(u'个')
            if self.current_word() in (u'周', u'星期', u'礼拜') and self.peek_next_word() in (u'后', u'以后', u'之后'):
                week_delta = tmp
                self.advance(2)

        if weekday or weekday == 0:
            self.time_delta_fields['weekday'] = weekday
            self.time_delta_fields['days'] = 1
        if week_delta != 0:
            if week_delta > 100:
                raise ParseError(ReplyEnum.parse_error_range)
            self.time_delta_fields['weeks'] = week_delta
        # else:
        #     self.set_index(beginning)
        #     return 0
        if (not weekday and weekday != 0) and not week_delta:
            self.set_index(beginning)
            return 0

        if not self.consume_hour():
            self.time_fields['hour'] = DEFAULT_HOUR
            self.time_fields['minute'] = DEFAULT_MINUTE
        self.exclude_time_range(self.consume_weekday_period)
        return self.get_index() - beginning

    def consume_hour_period(self):
        beginning = self.get_index()
        if self.current_word().isdigit():
            tmp = self.consume_digit()
            self.consume_word(u'个')
            if (self.consume_word(u'半小时') or (self.consume_word(u'半') and self.consume_word(u'钟头'))) \
                    and self.consume_word(u'后', u'以后', u'之后'):
                self.time_delta_fields['hours'] = tmp
                self.time_delta_fields['minutes'] = 30
            elif self.consume_word(u'小时', u'钟头'):
                if self.consume_word(u'后', u'以后', u'之后') or self.consume_minute_period():
                    self.time_delta_fields['hours'] = tmp
        elif self.consume_word(u'半小时') or (self.consume_word(u'半个') and self.consume_word(u'小时', u'钟头')):
            if self.consume_word(u'后', u'以后', u'之后'):
                self.time_delta_fields['hours'] = 0
                self.time_delta_fields['minutes'] = 30
        if 'hours' not in self.time_delta_fields:
            self.set_index(beginning)
            return 0
        if self.time_delta_fields['hours'] > 100:
            raise ParseError(ReplyEnum.parse_error_range)
        return self.get_index() - beginning

    def consume_minute_period(self):
        beginning = self.get_index()
        minute_delta = self.consume_digit()
        if minute_delta is not None:
            if self.consume_word(u'分', u'分钟'):
                self.consume_second_period()
                self.consume_word(u'后', u'以后', u'之后')
                if minute_delta > 1000:
                    raise ParseError(ReplyEnum.parse_error_range)
                self.time_delta_fields['minutes'] = minute_delta
                return self.get_index() - beginning
        elif self.consume_word(u'等会', u'一会', u'一会儿'):
            self.time_delta_fields['minutes'] = 10
            return self.get_index() - beginning
        self.set_index(beginning)
        return 0

    def consume_second_period(self):
        beginning = self.get_index()
        second_delta = self.consume_digit()
        if second_delta is not None:
            if self.consume_word(u'秒', u'秒钟'):
                self.consume_word(u'后', u'以后', u'之后')
                if second_delta > 10000:
                    raise ParseError(ReplyEnum.parse_error_range)
                self.time_delta_fields['seconds'] = second_delta
                return self.get_index() - beginning
        self.set_index(beginning)
        return 0

    def consume_to_end(self):
        self.do_what = ''.join(map(lambda p: p.word, self.words[self.idx:]))
        return len(self.words) - self.idx

    def consume_to_end_other(self):
        self.do_what = ''.join(map(lambda p: p, self.words[self.idx:]))
        return len(self.words) - self.idx

    def consume_word(self, *words):
        if self.current_word() in words:
            self.advance()
            return 1
        return 0

    def consume_word_other(self, *words):
        if self.words[self.idx] in words:
            self.advance()
            return 1
        return 0

    def consume_phrase(self, *words):
        beginning = self.get_index()
        for word in words:
            if not self.consume_word(word):
                self.set_index(beginning)
                return 0
        return self.get_index() - beginning

    def consume_digit(self, consume=True):
        if self.current_word().isdecimal():  # NOTE: isdigit covers too much
            digit = int(self.current_word())
            if consume:
                self.advance()
            return digit
        return None

    def current_word(self):
        if self.idx >= len(self.words):
            return ''
        if self.words[self.idx].word.isspace() \
                or self.words[self.idx].word in [u'的', u'。', u'，', u'’', u'‘', u'！', u'？']:
            self.words.pop(self.idx)  # Do not advance, which will cause a consume
            return self.current_word()
        return self.words[self.idx].word

    def current_tag(self):
        if self.idx >= len(self.words):
            return ''
        if self.words[self.idx].word.isspace() or self.words[self.idx].word in (u'的',):
            self.words.pop(self.idx)
            return self.current_tag()
        return self.words[self.idx].flag

    def peek_next_word(self, step=1):
        beginning = self.get_index()
        word_list = []
        while step:
            step -= 1
            self.advance()
            word_list.append(self.current_word())
        self.set_index(beginning)
        return ''.join(word_list)

    def get_index(self):
        return self.idx

    def set_index(self, idx):
        self.idx = idx

    def has_next(self):
        return self.idx < len(self.words)

    def advance(self, step=1):
        self.idx += step
