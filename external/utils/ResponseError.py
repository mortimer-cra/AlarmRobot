#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/12/19 11:45
# @File    : ResponseError.py


class ResponseError(Exception):
    """
    当 BaseResponse 的返回值不为 0 时抛出的异常
    """

    def __init__(self, err_code, err_msg):
        super(ResponseError, self).__init__(
            'err_code: {}; err_msg: {}'.format(err_code, err_msg))
        self.err_code = err_code
        self.err_msg = err_msg
