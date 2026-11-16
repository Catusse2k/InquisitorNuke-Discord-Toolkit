import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.util import *
from config.config import *

import requests
import threading
import time

Title("Discord Token Leaver")

token = CleanToken(input(f"{color.BLUE}\n{INPUT} Token -> {color.RESET}"))

if not token:
    print(f"\n{color.blue}{ERROR} Token is empty.{color.RESET}")
    Continue()
    Reset()

if token.count(".") != 2 or not TOKEN_REGEX.match(token):
    print(f"\n{color.blue}{ERROR} Malformed token: expected the format xxxxx.yyyyy.zzzzz.{color.RESET}")
    Continue()
    Reset()

headers = DiscordHeaders(token)

if token.startswith("mfa."):
    mfa_code = input(f"{color.BLUE}{INPUT} MFA Code -> {color.RESET}").strip()
    if not mfa_code.isdigit() or len(mfa_code) != 6:
        print(f"\n{color.blue}{ERROR} MFA code must be 6 digits.{color.RESET}")
        Continue()
        Reset()
    headers["X-Discord-MFA-Authorization"] = mfa_code

try:
    me = requests.get(f"{DISCORD_API}/users/@me", headers=headers, timeout=15)
except requests.RequestException:
    print(f"\n{color.blue}{ERROR} Could not reach Discord, check your connection.{color.RESET}")
    Continue()
    Reset()

if me.status_code == 401:
    print(f"\n{color.blue}{ERROR} Token is invalid, expired or the MFA code is wrong.{color.RESET}")
    Continue()
    Reset()

if me.status_code == 403:
    print(f"\n{color.blue}{ERROR} Token is locked or requires verification.{color.RESET}")
    Continue()
    Reset()

if me.status_code != 200:
    print(f"\n{color.blue}{ERROR} Unexpected response from Discord (HTTP {me.status_code}).{color.RESET}")
    Continue()
    Reset()

try:
    account = me.json()
except Exception:
    account = {}

print(f"{color.blue}{INFO} Account: {color.WHITE}{account.get('global_name') or account.get('username') or 'unknown'}{color.RESET}")

guilds = []
after = None

while True:
    params = {"limit": 200}
    if after:
        params["after"] = after
    try:
        r = requests.get(f"{DISCORD_API}/users/@me/guilds", headers=headers, params=params, timeout=15)
    except requests.RequestException:
        break
    if r.status_code != 200:
        break
    batch = r.json()
    if not batch:
        break
    guilds.extend(batch)
    after = batch[-1]["id"]
    if len(batch) < 200:
        break

if not guilds:
    print(f"\n{color.blue}{ERROR} This account is not in any guild.{color.RESET}")
    Continue()
    Reset()

print(f"{color.blue}{INFO} Guilds to leave: {color.WHITE}{len(guilds)}{color.RESET}\n")

lock = threading.Lock()


def log(line):
    with lock:
        print(line)


def LeaveServer(chunk):
    for guild in chunk:
        gid = guild["id"]
        name = guild.get("name", gid)
        owner = guild.get("owner", False)

        for _ in range(3):
            try:
                res = requests.delete(f"{DISCORD_API}/users/@me/guilds/{gid}", headers=headers, timeout=15)
            except requests.RequestException:
                log(f"{blue}[{white}{current_time_hour()}{blue}] {ERROR} Status: {white}network error{blue} | Server: {white}{name}{blue}")
                break

            if res.status_code == 429:
                try:
                    wait = float(res.json().get("retry_after", 2))
                except Exception:
                    wait = 2.0
                time.sleep(min(wait, 30) + 0.3)
                continue

            if res.status_code in (200, 204):
                log(f"{green}[{white}{current_time_hour()}{green}] {ADD} Status: {white}Leave{green} | Server: {white}{name}{green}")
                break

            if res.status_code == 400 and owner:
                try:
                    d = requests.delete(f"{DISCORD_API}/guilds/{gid}", headers=headers, timeout=15)
                except requests.RequestException:
                    log(f"{blue}[{white}{current_time_hour()}{blue}] {ERROR} Status: {white}network error{blue} | Server: {white}{name}{blue}")
                    break
                if d.status_code in (200, 204):
                    log(f"{green}[{white}{current_time_hour()}{green}] {ADD} Status: {white}Deleted (owner){green} | Server: {white}{name}{green}")
                elif d.status_code == 401:
                    log(f"{blue}[{white}{current_time_hour()}{blue}] {ERROR} Status: {white}MFA code required{blue} | Server: {white}{name}{blue}")
                else:
                    log(f"{blue}[{white}{current_time_hour()}{blue}] {ERROR} Status: {white}HTTP {d.status_code}{blue} | Server: {white}{name}{blue}")
                break

            if res.status_code == 401:
                log(f"{blue}[{white}{current_time_hour()}{blue}] {ERROR} Status: {white}invalid token{blue} | Server: {white}{name}{blue}")
                break

            try:
                code = res.json().get("code")
            except ValueError:
                code = None
            log(f"{blue}[{white}{current_time_hour()}{blue}] {ERROR} Status: {white}HTTP {res.status_code}{f' ({code})' if code else ''}{blue} | Server: {white}{name}{blue}")
            break


threads = []
for chunk in [guilds[i:i + 3] for i in range(0, len(guilds), 3)]:
    t = threading.Thread(target=LeaveServer, args=(chunk,), daemon=True)
    t.start()
    threads.append(t)
for thread in threads:
    thread.join()

Continue()
Reset()