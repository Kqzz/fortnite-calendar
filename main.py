from typing import Dict
import requests
import re

def log(m: str):
    print(f"[*] {m}")

def get_events(region: str) -> typing.Dict|None:
    url = f"https://fortnitetracker.com/events?region={region}"
    log(f"GET: {url}")

    req = requests.get(url)

    if req.status_code != 200:
        log(f"failed: {req.status_code}")
        return None 
    
    log(req.content)

get_events("NAE")
