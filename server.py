# -*- coding:utf-8 -*-

from bottle import route, run, template
import psorss

@route('/')
def index():
    rss = psorss.getCurrentData()
    return rss

run(host='0.0.0.0', port=8000, debug=False)
