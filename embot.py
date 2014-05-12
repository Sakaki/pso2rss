#!/usr/bin/env python
#coding:utf-8

import sqlite3
import twitter
from datetime import datetime

consumerKey = ""
consumerSecret = ""
accessToken = ""
accessSecret = ""

db_path = ""

api = twitter.Api(consumerKey,consumerSecret,accessToken,accessSecret)

conn = sqlite3.connect(db_path)
sql = "select * from events where time > datetime('now', '+9 hours') and type = '緊急' order by time limit 1;".decode("utf-8")
cursor = conn.cursor()
events = cursor.execute(sql)

temp = datetime.now()
time = "{0}:{1}".format(temp.hour, temp.minute)

for event in events:
    raw = u"【bot】次の予告緊急は{0}の{1}だよ！さぁ、君も宇宙の平和を守りに行こう！！".format(event[0][11:16], event[2], time.decode("utf-8"))
tweet = raw

api.PostUpdates(status=tweet)
