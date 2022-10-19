#!/bin/python3

from typing import List
import re
from datetime import datetime, timedelta
import requests
import json
from ics import Calendar, Event
from flask import Flask, request, send_file
import threading


app = Flask(__name__)

TIMEFMT = "%Y-%m-%dT%H:%M:%S"


def log(m: str):
    print(f"[*] {m}")


def get_events(region: str) -> List | None:
    url = f"https://www.epicgames.com/fortnite/competitive/api/en-US/calendar"

    res = requests.post(url)

    if res.status_code != 200:
        log(f"failed: {res.status_code}")
        return None

    e = res.json()

    return e["eventsData"]


def get_cal(events, region):
    c = Calendar()

    now = datetime.now()
    for event in events:
        for window in event['eventWindows']:
            title = window['eventWindowId']
            title = title.split('_Event')[0]
            title = title.split('_Week')[0]

            if region.upper() not in title:
                continue

            fmt = TIMEFMT
            if "." in window['beginTime']:
                fmt += ".%f"
            fmt += "Z"

            beginTime = datetime.strptime(window['beginTime'], fmt)

            if datetime.now() > beginTime:
                continue

            fmt = TIMEFMT
            if "." in window['endTime']:
                fmt += ".%f"
            fmt += "Z"
            endTime = datetime.strptime(window['endTime'], fmt)

            e = Event(
                name=title,
                url=f"https://fortnitetracker.com/events/epicgames_{title}",
                begin=beginTime,
                end=endTime
            )

            c.events.add(e)

    return c.serialize()


@app.route('/cal.ics')
def _events():
    region = request.args.get("region", type=str) or "NAE"

    cal = get_cal(events, region)
    return cal


@app.route('/')
def _index():
    return send_file("index.html")


def update_events():
    global events
    events = get_events("NAE")


events = get_events("NAE")

if __name__ == '__main__':

    threading.Timer(60 * 60 * 12, update_events)
    app.run()
