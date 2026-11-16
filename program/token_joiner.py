import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.util import *
from config.config import *

import requests
import secrets
import time

Title("Discord Token Joiner")

token = CleanToken(input(f"{color.BLUE}\n{INPUT} Token -> {color.RESET}"))
invite = input(f"{color.BLUE}{INPUT} Server Invitation -> {color.RESET}").strip()

if not token:
    print(f"\n{color.blue}{ERROR} Token is empty.{color.RESET}")
    Continue()
    Reset()

if token.count(".") != 2 or not TOKEN_REGEX.match(token):
    print(f"\n{color.blue}{ERROR} Malformed token: expected the format xxxxx.yyyyy.zzzzz.{color.RESET}")
    Continue()
    Reset()

invite_code = invite.split("/")[-1].split("?")[0].strip()

if not invite:
    print(f"\n{color.blue}{ERROR} Invitation is empty.{color.RESET}")
    Continue()
    Reset()

if not invite_code or " " in invite_code:
    print(f"\n{color.blue}{ERROR} Invalid invitation: expected discord.gg/CODE or a full invite URL.{color.RESET}")
    Continue()
    Reset()

headers = DiscordHeaders(token)
headers["X-Super-Properties"] = "eyJvcyI6IkxpbnV4IiwiYnJvd3NlciI6IkNocm9tZSIsImRldmljZSI6IiIsInN5c3RlbV9sb2NhbGUiOiJlbi1VUyIsImNsaWVudF92ZXJzaW9uIjoiMC4wLjAiLCJvc192ZXJzaW9uIjoiIn0="

try:
    probe = requests.get(
        f"{DISCORD_API}/invites/{invite_code}",
        params={"with_counts": "true", "with_expiration": "true"},
        headers=headers,
        timeout=15,
    )
except requests.RequestException:
    print(f"\n{color.blue}{ERROR} Could not reach Discord, check your connection.{color.RESET}")
    Continue()
    Reset()

if probe.status_code == 404:
    print(f"\n{color.blue}{ERROR} Invitation is invalid or has expired.{color.RESET}")
    Continue()
    Reset()

if probe.status_code == 401:
    print(f"\n{color.blue}{ERROR} Token is invalid or expired.{color.RESET}")
    Continue()
    Reset()

if probe.status_code != 200:
    print(f"\n{color.blue}{ERROR} Unexpected response from Discord (HTTP {probe.status_code}).{color.RESET}")
    Continue()
    Reset()

try:
    invite_data = probe.json()
except Exception:
    invite_data = {}

guild = invite_data.get("guild") or {}
server_name = guild.get("name", invite_code)
member_count = invite_data.get("approximate_member_count")
members_str = f" ({member_count} members)" if member_count is not None else ""

if invite_data.get("expires_at") is None:
    print(f"{color.blue}{INFO} Server: {color.WHITE}{server_name}{members_str}{color.BLUE} | Invite never expires{color.RESET}")
else:
    print(f"{color.blue}{INFO} Server: {color.WHITE}{server_name}{members_str}{color.RESET}")

payload = {"session_id": secrets.token_hex(16)}
response = None

for _ in range(5):
    try:
        response = requests.post(f"{DISCORD_API}/invites/{invite_code}", headers=headers, json=payload, timeout=15)
    except requests.RequestException:
        print(f"\n{color.blue}{ERROR} Connection dropped while joining {server_name}.{color.RESET}")
        Continue()
        Reset()

    if response.status_code == 429:
        try:
            wait = float(response.json().get("retry_after", 5))
        except Exception:
            wait = 5.0
        print(f"{blue}[{white}{current_time_hour()}{blue}] {WAIT} Rate limit, retrying in {round(wait, 2)}s...{reset}")
        time.sleep(min(wait, 30) + 0.5)
        continue

    break

if response is not None and response.status_code == 200:
    print(f"\n{blue}[{white}{current_time_hour()}{blue}] {ADD} Status: {white}Joined{blue} | Server: {white}{server_name}{members_str}{blue}\n")
else:
    body = {}
    if response is not None:
        try:
            body = response.json()
        except ValueError:
            pass

    code = body.get("code")

    if response is None:
        reason = "no response from Discord"
    elif response.status_code == 401:
        reason = "token is invalid or expired"
    elif response.status_code == 403:
        reason = "token is banned or blocked from this guild"
    elif code == 10011:
        reason = "unknown invite"
    elif code == 30001:
        reason = "guild limit reached (100 servers)"
    elif code == 40007:
        reason = "token is banned from this guild"
    elif response.status_code == 400 and body.get("captcha_key"):
        reason = "captcha required, use a fresh session_id or retry later"
    else:
        reason = f"HTTP {response.status_code}"

    print(f"\n{blue}[{white}{current_time_hour()}{blue}] {ERROR} Status: {white}{reason}{blue} | Server: {white}{server_name}{blue}\n")

    if body.get("captcha_key"):
        print(f"{blue}{INFO} Captcha keys: {white}{', '.join(body['captcha_key'])}{blue}\n")

Continue()
Reset()