#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/1/10 16:45
# @File    : VoiceRecognition.py
from qqai.classes import *

APP_ID = 00000
APP_KEY = 'xxxxxx'


class AudioRecognitionEcho(QQAIClass):
    """语音识别-echo版"""
    api = 'https://api.ai.qq.com/fcgi-bin/aai/aai_asr'

    def __init__(self, app_id, app_key):
        super().__init__(app_id, app_key)

    def make_params(self, audio_format, speech, rate=None):
        """获取调用接口的参数"""
        params = {'app_id': self.app_id,
                  'time_stamp': int(time.time()),
                  'nonce_str': int(time.time()),
                  'format': audio_format,
                  'speech': self.get_base64(speech),
                  }
        if rate is not None:
            params['rate'] = 16000
        params['sign'] = self.get_sign(params)
        return params

    def run(self, audio_format, speech, rate=None):
        params = self.make_params(audio_format, speech, rate)
        response = self.call_api(params)
        if response.status_code != 200:
            response = self.try_again(params)
        if response:
            result = json.loads(response.text)
            return result
        return None

    def try_again(self, params):
        try_num = 10
        for i in range(0, try_num):
            print('retry ..%s' % str(i))
            response = self.call_api(params)
            if response.status_code == 200:
                return response
        return None


def get_voice_text(path):
    if path:
        try:
            re_msg = AudioRecognitionEcho(APP_ID, APP_KEY).run(4, open(path, 'rb'))
            if re_msg:
                ret = re_msg.get('ret')
                if ret == 0:
                    return re_msg.get('data').get('text')
            else:
                return None
        except Exception as e:
            print(str(e))
    return None


if __name__ == '__main__':
    for i in range(1, 100):
        path = r'E:\浏览器下载\可爱猫4.4.0含开发包\可爱猫4.4.0\data\temp\\wxid_0u8rum7n0msk12\497f45eea599ffe5e5374dd60e60ffa62872327803@chatroom64601_1581642697.silk'
        text = get_voice_text(path)
        print(text)
        time.sleep(0.5)
