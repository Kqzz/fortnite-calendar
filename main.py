from typing import List
import re
import requests
from datetime import datetime
import json

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


events = get_events("NAE")

for event in events:
    data = event.get("customData")
    date = datetime.strptime(data["windows"][0]["beginTime"], "%Y-%m-%dT%H:%M:%S+00:00")
    title = data["title"]

    log(f"{title}: {date}")
