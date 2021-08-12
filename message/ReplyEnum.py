# -*- coding: utf-8 -*-
# @Time    : 2019/11/27 23:00
# @Author  : liu
# @File    : ReplyEnum.py
# @Desc    :
# @Software: PyCharm


class ReplyEnum:
    remind = '提醒'

    welcome_example = '[@emoji=\\uE11B]你好呀！现在我是你的专属提醒喵啦！你可以像给一个朋友发消息那样让我提醒你\n\n ' \
                      '[@emoji=\\uE231] 如需创建提醒你可以这样告诉我：\n' \
                      '  “提醒我两个小时后关空调”\n' \
                      '  “明晚八点提醒我买牙膏”\n' \
                      '  “每月5号提醒我还房贷”\n' \
                      '  “每周五晚上提醒我洗衣服”\n' \
                      '  “每隔两个星期提醒我理发”\n' \
                      '  “每个工作日下午2点提醒我送资料”\n' \
                      '    ...... \n' \
                      '   觉得打字麻烦？不方便打字？你还可以发语音给提醒喵哦\n\n' \
                      '[@emoji=\\uE231] 如需提醒微信好友请发送 “好友提醒”\n' \
                      '[@emoji=\\uE231] 如需天气、疫情等实用功能提醒请发送“功能提醒”' \
                      '\n\n' \
                      '如果觉得提醒喵好用，欢迎分享给自己的小伙伴，你们还可以相互提醒哦[@emoji=\\uE405]'

    date_parse_error = '希望我什么时间提醒你？'
    date_parse_error_friend = '希望我什么时间提醒ta？'
    date_parse_error_repeat = '如需将此提醒设置为定时提醒，请直接回复我时间，像这样告诉我：“每天早上十点”'
    date_parse_error_who = '希望提醒谁？'
    non_do_something = '你希望我在这个时间提醒你做什么事情？'
    non_do_something_friend = '你希望我在这个时间提醒ta做什么事情？'

    weather_city = '你希望提醒哪个城市的天气？'
    news_channel = '为你准备了一些可供选择的新闻频道，请选择一个（回数字）\n\n'
    bus_city = '请告诉我你的城市和公交线路，像这样：成都  84'

    dead_time = '我没有回到过去的本事呢'

    non_friend = '没有找到要提醒的好友，如需提醒微信好友需要提醒喵为你们的共同好友哦'
    friend_repeat_limit = '好友提醒暂不开放重复提醒'

    exception_unknow = '哦吼~ 好像出了点小问题'

    parse_error = '[难过]我没有get到时间'
    parse_time_range = '[@emoji=\\uE10F] 时间范围暂时还不支持哦'
    parse_error_range = '[@emoji=\\uE10F] 时间范围不合理'
    month_yeat_repeat = '[@emoji=\\uE10F] 当前仅支持分、时、天、周的时间间隔提醒'
    parse_error_unfinished = '[@emoji=\\uE10F] 暂不支持各种节假日提醒哦~'

    parse_repeat_workday = '[@emoji=\\uE10F] 如需重复性提醒，请这样告诉我：\n\n“每月20号”\n“每两个小时”\n“每个工作日”\n......'
    parse_date_error_example_again = '试试这样和我说：\n' \
                                     '  “两个小时后”\n' \
                                     '  “明晚八点”\n' \
                                     '  “每月5号”\n' \
                                     '    ......'
    parse_date_error_example_again_ext = '试试这样和我说：\n\n“每天早上七点”\n“每周周一”\n“每月5号”\n ......'
    function_example = '试试发送下面的关键词来创建一个功能提醒吧\n\n' \
                       '    [@emoji=\\u2615]  久坐提醒\n' \
                       '    [@emoji=\\uE223]  倒数日提醒\n' \
                       ' \n' \
                       '    [@emoji=\\uD83C\\uDF24]  天气提醒\n' \
                       '    [@emoji=\\uD83D\\uDCF0]  新闻提醒\n' \
                       '    [@emoji=\\uD83D\\uDE8C]  公交车提醒（实时位置）\n' \
                       '    [@emoji=\\uE40C]  疫情提醒\n' \
                       '    [@emoji=\\uD83D\\uDCC8]  股票提醒(分时线图)\n' \
                       '    [@emoji=\\uD83D\\uDCC8]  基金提醒(实时净值估算)\n' \
                       '    [@emoji=\\uE348]  微博热榜提醒\n' \
                       '    [@emoji=\\uD83D\\uDCFD][@emoji=\\uFE0F]  豆瓣新片提醒\n' \
                       '    ......'
    parse_remind_error_example = '[@emoji=\\uE231] 如需创建普通提醒试试这样告诉我：\n' \
                                 '  “提醒我两个小时后关空调”\n' \
                                 '  “明晚八点提醒我买牙膏”\n' \
                                 '  “每月5号提醒我还房贷”\n' \
                                 '  “每周五晚上提醒我洗衣服”\n' \
                                 '  “每隔两个星期提醒我理发”\n' \
                                 '  “每个工作日下午2点提醒我送资料”\n' \
                                 '    ...... \n' \
                                 '[@emoji=\\uE231] 如需查看提醒请说 “我的提醒”\n' \
                                 '[@emoji=\\uE231] 如需天气等实用功能提醒请说 “功能提醒”'

    exit_session = '\n\n [@emoji=\\uE10F] 你可以说“退出”来结束此对话'
    cancel_list = ['取消', '关闭', '退出', '结束', '滚', '停止', '不要', '0', '不需要', '不希望', '算了']
    cancel_session = '[@emoji=\\uE420]'

    who_are_u = ['你是谁', '你是', '你谁', '你叫什么', '什么名字', '名字是']
