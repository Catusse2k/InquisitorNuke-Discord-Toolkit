import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.util import *
from config.config import *

import requests
import threading
import time
import random

Title("Discord Webhook Spammer")

webhook_url = input(f"{color.BLUE}\n{INPUT} Webhook URL -> {color.RESET}").strip().strip('"')
webhook_url = webhook_url.replace("discordapp.com", "discord.com")

if not webhook_url:
    print(f"\n{color.blue}{ERROR} Webhook URL is empty.{color.RESET}")
    Continue()
    Reset()

webhook_url = CheckWebhook(webhook_url)
if not webhook_url:
    Continue()
    Reset()

base_url, _, query = webhook_url.partition("?")
endpoint = f"{base_url}?wait=true" + (f"&{query}" if query else "")

probe = requests.get(webhook_url, timeout=15, headers={"User-Agent": USER_AGENT})
if probe is None or probe.status_code != 200:
    if probe is not None and probe.status_code == 404:
        print(f"\n{color.blue}{ERROR} This webhook does not exist or was deleted.{color.RESET}")
    elif probe is not None and probe.status_code == 401:
        print(f"\n{color.blue}{ERROR} Invalid webhook token.{color.RESET}")
    else:
        print(f"\n{color.blue}{ERROR} Webhook is not reachable.{color.RESET}")
    Continue()
    Reset()

try:
    webhook_info = probe.json()
    webhook_name = webhook_info.get("name") or "unnamed"
    channel_id = webhook_info.get("channel_id") or "?"
except Exception:
    webhook_name = "unnamed"
    channel_id = "?"

print(f"{color.blue}{INFO} Webhook: {color.WHITE}{webhook_name}{color.BLUE} | Channel: {color.WHITE}{channel_id}{color.RESET}")

message = input(f"{color.BLUE}{INPUT} Message -> {color.RESET}")
if not message.strip():
    print(f"\n{color.blue}{ERROR} Message is empty, nothing would be sent.{color.RESET}")
    Continue()
    Reset()

if len(message) > 2000:
    print(f"{color.blue}{INFO} Message too long, truncated to 2000 characters.{color.RESET}")
    message = message[:2000]

try:
    threads_number = int(input(f"{INPUT} Threads Number -> {color.RESET}"))
except Exception:
    print(f"\n{color.blue}{ERROR} Threads number must be an integer.{color.RESET}")
    Continue()
    Reset()

if threads_number < 1:
    print(f"\n{color.blue}{ERROR} Threads number must be at least 1.{color.RESET}")
    Continue()
    Reset()

if threads_number > 100:
    print(f"{color.blue}{INFO} Capped to 100 threads.{color.RESET}")
    threads_number = 100

lock = threading.Lock()
local = threading.local()
pause_until = 0.0


def get_session():
    if not hasattr(local, "session"):
        s = requests.Session()
        s.headers.update({
            "Content-Type": "application/json",
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.9",
            "User-Agent": USER_AGENT,
            "X-Discord-Locale": "en-US",
            "X-Discord-Timezone": "Europe/Rome",
        })
        adapter = requests.adapters.HTTPAdapter(pool_connections=8, pool_maxsize=threads_number + 8, max_retries=0)
        s.mount("https://", adapter)
        local.session = s
    return local.session


def gate():
    while True:
        with lock:
            delay = pause_until - time.time()
        if delay <= 0:
            return
        time.sleep(min(delay, 5))


def throttle(response):
    global pause_until
    remaining = response.headers.get("X-RateLimit-Remaining")
    reset_after = response.headers.get("X-RateLimit-Reset-After")
    if remaining is None or reset_after is None:
        return
    try:
        if int(remaining) > 0:
            return
        reset_after = float(reset_after)
    except ValueError:
        return
    with lock:
        pause_until = max(pause_until, time.time() + reset_after)


def log(valid, status):
    if valid:
        print(f"{green}[{white}{current_time_hour()}{green}] {GEN_VALID} Message: {color.WHITE}{message}{color.GREEN} | Status: {color.WHITE}{status}{color.GREEN}")
    else:
        print(f"{blue}[{white}{current_time_hour()}{blue}] {GEN_INVALID} Message: {color.WHITE}{message}{color.BLUE} | Status: {color.WHITE}{status}{color.BLUE}")


def send_webhook():
    global pause_until
    payload = {
        "content": message,
        "username": username_webhook,
        "avatar_url": avatar_webhook,
        "tts": False,
        "allowed_mentions": {"parse": []},
        "flags": 4096,
    }

    while True:
        gate()
        try:
            response = get_session().post(endpoint, json=payload, timeout=15)
        except requests.RequestException:
            log(False, "Network")
            time.sleep(1)
            continue

        if response.status_code == 429:
            try:
                retry_after = float(response.json().get("retry_after", 1))
            except Exception:
                retry_after = float(response.headers.get("Retry-After", 1))
            scope = response.headers.get("X-RateLimit-Scope", "")
            if response.headers.get("X-RateLimit-Global") or scope == "global":
                with lock:
                    pause_until = max(pause_until, time.time() + retry_after)
            time.sleep(retry_after + random.uniform(0.05, 0.2))
            continue

        throttle(response)

        if response.status_code in (200, 204):
            log(True, "Send")
        elif response.status_code == 404:
            log(False, "Webhook Not Found")
        elif response.status_code == 401:
            log(False, "Invalid Token")
        elif response.status_code == 400:
            log(False, "Bad Payload")
        elif response.status_code == 403:
            log(False, "Forbidden")
        else:
            log(False, f"HTTP {response.status_code}")
        break


def request():
    threads = []
    for _ in range(threads_number):
        t = threading.Thread(target=send_webhook, daemon=True)
        t.start()
        threads.append(t)

    for thread in threads:
        thread.join()


while True:
    request()