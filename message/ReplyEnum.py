# -*- coding: utf-8 -*-
# @Time    : 2019/11/27 23:00
# @Author  : liu
# @File    : ReplyEnum.py
# @Desc    :
# @Software: PyCharm


class ReplyEnum:
    remind = '提醒'
    remind_head = '温馨提醒'
    date_parse_exception = '啊哦,我没有理解时间,你可以这样和我说：明天下午三点提醒我理发'
    date_parse_error = '希望我什么时间提醒你？'
    date_parse_error_who = '希望提醒谁？'
    date_parse_error_friend = '我没有get到提醒时间呢,你希望我什么时间提醒Ta？'
    middle_case_date_parse_error = '我没有get到提醒时间呢'
    date_parse_error_again = '看不懂的时间,你可以这样和我说：明天下午三点'
    non_do_something = '你希望我在这个时间提醒你做什么事情？'
    non_do_something_friend = '你希望我在这个时间提醒Ta做什么事情？'
    date_parse_not_msgText = '我没有get到具体的时间呢，你可以这样和我说：明天下午三点提醒我理发'
    dead_time = '我没有回到过去的本事呢'
    dead_time_again = '那好像已经是过去时了哦，和我说个未来的时间吧'
    remind_case_exception = '啊哦,我脑子短路了,换种表达方式试试，你可以这样和我说：明天下午三点提醒我理发'
    middle_case_short = '我猜不到你要提醒谁做什么呢，你可以像这样和我说：明天下午三点提醒我理发'
    unfinished_function = '还没有完成的功能'
    non_friend = '你要提醒的人不在我的好友列表，你可以让Ta添加我为微信好友，你就可以让我提醒Ta啦'
    non_remind_person = '我不知道要提醒谁呢,想要提醒好友记得邀请你的好友添加我的微信哦'
    cancel_session = '好的'

    parse_error = '看不懂的时间'
    parse_error_range = '时间超范围了'

    parse_repeat_workday = '如需重复性提醒，请这样告诉我：\n\n“每月20号”\n“每两个小时”\n“每个工作日”\n......'

    parse_date_error_example_again = '你可以这样和我说：\n\n“两个星期后”\n“明天晚上”\n“每月20号”\n......'

    parse_remind_error_example = '你可以这样和我说：\n\n“两个星期后提醒我去复诊”\n“周五晚上提醒我打电话给老妈”\n“每月20号提醒我还信用卡”\n...... '

    weather_city = '你希望提醒哪个城市的天气？'

    exit_session = '\n你可以说“退出”来结束此对话'

    cancel_list = ['取消', '关闭', '退出', '结束', '滚', '停止', '不要', '0']
