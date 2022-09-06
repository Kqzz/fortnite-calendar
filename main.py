#!/bin/python3

from typing import List
import re
from datetime import datetime, timedelta
import requests
import json
from ics import Calendar, Event
from flask import Flask, request
import threading


app = Flask(__name__)

find_events = re.compile('(?<=imp_calendar = ).*(?=;<\/script>)')


def log(m: str):
    print(f"[*] {m}")


def get_events(region: str) -> List | None:
    url = f"https://fortnitetracker.com/events?region={region}"
    log(f"GET: {url}")

    req = requests.get(url)

    if req.status_code != 200:
        log(f"failed: {req.status_code}")
        return None

    page = req.text.replace("\r\n", "").replace("00.001", "00")
    events_txt = find_events.findall(page, re.DOTALL)

    e = json.loads(events_txt[0])

    return e


def get_cal(events, hype, console):
    c = Calendar()

    for event in events:
        data = event.get("customData")
        date = datetime.strptime(
            data["windows"][0]["beginTime"], "%Y-%m-%dT%H:%M:%S+00:00")
        title = data["title"]

        if "HYPE" in title and not hype:
            continue

        if "CONSOLE" in title and not console:
            continue

        log(f"{title}: {date}")

        e = Event(
            name=title,
            url=f"https://fortnitetracker.com/events/{data['windows'][0]['eventId']}",
            begin=date,
            end=date + timedelta(hours=1, minutes=30)
        )

        c.events.add(e)

    return c.serialize()


@app.route('/cal.ics')
def _events():
    hype = request.args.get("hype", type=bool) or False
    console = request.args.get("console", type=bool) or False

    cal = get_cal(events, hype, console)
    return cal


def update_events():
    global events
    events = get_events("NAE")


events = get_events("NAE")

if __name__ == '__main__':

    threading.Timer(60 * 60 * 24, update_events)
    app.run()
