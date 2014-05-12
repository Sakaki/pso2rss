#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib2
import re
import sqlite3
from datetime import datetime, date
from pyatom import AtomFeed

db_path = ""

def getID(html):
    targets = []
    for line in html:
        if "予告イベント情報！" in line:
            pageid = re.search("id=[0-9]*", line).group(0)
            targets.append(pageid)
    return targets

def splitTag(text):
    while("<" in text):
        start = text.find(">")
        end = text.rfind("<")
        text = text[start+1:end]
    return text

def getEvents(html):
    for num,line in enumerate(html):
        if "<h3>イベントスケジュール</h3>" in line:
            head = num
        elif "<h3>注意事項</h3>" in line:
            tail = num
            break
    eventlst = html[head:(tail-1)]

    events = []
    for line in eventlst:
        if "<h4>" in line and "</h4>":
            day = "".join(re.split("<.*?>", line)[1:-1])
        elif '<th class="sub">' in line:
            time = splitTag(line)
        elif '<td class="icon">' in line:
            type = re.split('alt="|" /', line)[1]
        elif "<td>" in line and "</td>":
            desc = "".join(re.split("<.*?>", line)[1:-1])
            if time != "" and type != "" and desc != 0:
                event = {
                    "day": day,
                    "time": time,
                    "type": type,
                    "desc": desc
                    }
                print day, time, type, desc
                events.append(event)
                time = ""
                type = ""
                desc = ""
    return events

def registerDB(events):
    conn = sqlite3.connect(db_path)
    sql = u"create table if not exists events (time datetime,type text, desc text);"
    conn.execute(sql)

    for event in events:
        year = datetime.today().year
        temp = re.split("[月日]", event["day"])
        month = int(temp[0])
        day = int(temp[3])

        if "終日" in event["time"]:
            time = "00:00:00"
            event.update({"type": "終日"})
        else:
            time = event["time"]+":00"

        if len(time) > 8:
            time = re.split(" ", time)[0] + ":00"
        if len(time) == 7:
            time = "0" + time

        timestr = "{0}-{1:02d}-{2:02d} {3}".format(year, month, day, time)
        sql = "insert or replace into events values ('{0}', '{1}', '{2}')".format(timestr, event["type"], event["desc"]).decode("utf-8")
        conn.execute(sql)

    conn.commit()
    conn.close()

def getCurrentData():
    feed = AtomFeed(title=u"PSO2 予告緊急RSS",
                    subtitle=u"【非公式】PSO2の予告緊急を近い順に表示するよ",
                    feed_url=u"http://sakaki2700.dip.jp/pso2rss",
                    url=u"http://pso2.jp/players/news/?mode=event",
                    author=u"")

    conn = sqlite3.connect(db_path)
    sql = "select * from events where time > datetime('now', '+9 hours') order by time limit 10;".decode("utf-8")

    cursor = conn.cursor()
    cursor.execute(sql)
    for row in cursor:
        feed.add(title=u"【"+row[0]+u"】"+row[1],
                 content=row[2],
                 content_type=u"html",
                 author=u"pso2",
                 url=u"http://pso2.jp/players/news/?mode=event",
                 updated=datetime.utcnow())

    return feed.to_string().encode("utf-8")

if __name__ == "__main__":
    time = datetime.now()
    # 水曜日のメンテ時間内だったら取得する
    if time.weekday() != 2 or time.hour < 11 or time.hour > 17:
        print "メンテ時間外です。取得しても意味ないかも"
        exit()

    #res = open("index.html")
    res = urllib2.urlopen("http://pso2.jp/players/news/?mode=event")
    eventid = getID(res.readlines())[0]
    res.close()

    #res = open("index2.html")
    res = urllib2.urlopen("http://pso2.jp/players/news/?"+eventid)
    events = getEvents(res.readlines())
    res.close()
    registerDB(events)
