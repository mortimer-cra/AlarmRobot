#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/12/13 11:31
# @File    : ParseError.py


class ParseError(ValueError):
    def __init__(self, value):
        self.value = value
