#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @File  : YuController.py
# @Author: Administrator
# @Date  : 2020/2/22
import time
from flask import Flask, request, jsonify
from consumer.ReceiveConsumer import on_message

app = Flask(__name__)


@app.route("/", methods=["POST", "GET"])
def index():
    if request.method == "POST":
        message = request.json
        if message:
            on_message(message)
        return jsonify({"code": 200})


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8074, debug=True)
