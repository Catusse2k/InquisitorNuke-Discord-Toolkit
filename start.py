import os
import sys
import time
import subprocess
import datetime
import shutil
import requests
import re
import webbrowser
from colorama import init, Fore

BASE = os.path.dirname(os.path.abspath(__file__))
START_FILE = os.path.abspath(__file__)
CONFIG_DIR = os.path.join(BASE, "config")
PAGE_FILE = os.path.join(CONFIG_DIR, "page.txt")

if not os.path.isfile(os.path.join(CONFIG_DIR, "config.py")):
    print(f"config folder not found under {BASE}")
    sys.exit(1)

if BASE not in sys.path:
    sys.path.insert(0, BASE)

os.chdir(BASE)

from config.config import *
from config.util import *

Title("Loading")

green_light = Fore.LIGHTGREEN_EX
green_dark = Fore.GREEN

popup_version = ""
ascii_art = r"""
██▓ ███▄    █   █████   █    ██  ██▓  ██████  ██▓▄▄▄█████▓ ▒█████   ██▀███      ███▄    █  █    ██  ██ ▄█▀▓█████ 
▓██▒ ██ ▀█   █ ▒██▓  ██▒ ██  ▓██▒▓██▒▒██    ▒ ▓██▒▓  ██▒ ▓▒▒██▒  ██▒▓██ ▒ ██▒    ██ ▀█   █  ██  ▓██▒ ██▄█▒ ▓█   ▀ 
▒██▒▓██  ▀█ ██▒▒██▒  ██░▓██  ▒██░▒██▒░ ▓██▄   ▒██▒▒ ▓██░ ▒░▒██░  ██▒▓██ ░▄█ ▒   ▓██  ▀█ ██▒▓██  ▒██░▓███▄░ ▒███   
░██░▓██▒  ▐▌██▒░██  █▀ ░▓▓█  ░██░░██░  ▒   ██▒░██░░ ▓██▓ ░ ▒██   ██░▒██▀▀█▄     ▓██▒  ▐▌██▒▓▓█  ░██░▓██ █▄ ▒▓█  ▄ 
░██░▒██░   ▓██░░▒███▒█▄ ▒▒█████▓ ░██░▒██████▒▒░██░  ▒██▒ ░ ░ ████▓▒░░██▓ ▒██▒   ▒██░   ▓██░▒▒█████▓ ▒██▒ █▄░▒████▒
░▓  ░ ▒░   ▒ ▒ ░░ ▒▒░ ▒ ░▒▓▒ ▒ ▒ ░▓  ▒ ▒▓▒ ▒ ░░▓    ▒ ░░   ░ ▒░▒░▒░ ░ ▒▓ ░▒▓░   ░ ▒░   ▒ ▒ ░▒▓▒ ▒ ▒ ▒ ▒▒ ▓▒░░ ▒░ ░
 ▒ ░░ ░░   ░ ▒░ ░ ▒░  ░ ░░▒░ ░ ░  ▒ ░░ ░▒  ░ ░ ▒ ░    ░      ░ ▒ ▒░   ░▒ ░ ▒░   ░ ░░   ░ ▒░░░▒░ ░ ░ ░ ░▒ ▒░ ░ ░  ░
 ▒ ░   ░   ░ ░    ░   ░  ░░░ ░ ░  ▒ ░░  ░  ░   ▒ ░  ░      ░ ░ ░ ▒    ░░   ░       ░   ░ ░  ░░░ ░ ░ ░ ░░ ░    ░   
 ░           ░     ░       ░      ░        ░   ░               ░ ░     ░                 ░    ░     ░  ░      ░  ░  
"""

WIDTH = 62
ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")
SPINNER = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]

pages = {
    "1": ("DISCORD", [
        ("01", "Webhook Spammer", "flood a webhook"),
        ("02", "Token Nuker", "spam account settings"),
        ("03", "Token Joiner", "join a guild with the tokens"),
        ("04", "Token Leaver", "leave every guild"),
        ("05", "Token Login", "open the token in the browser"),
        ("00", "Exit", "close InquisitorNuke"),
    ])
}


def vlen(text):
    return len(ANSI_RE.sub("", text))


def pad(text, width=WIDTH):
    return text + " " * max(0, width - vlen(text))


def row(content=""):
    return f"{cyan}│{reset} {pad(content)} {cyan}│{reset}"


def row_pair(left, right):
    gap = max(1, WIDTH - vlen(left) - vlen(right))
    return row(f"{left}{' ' * gap}{right}")


def top(title=None):
    if title:
        dashes = "─" * max(0, WIDTH - vlen(title) - 1)
        return f"{cyan}╭─ {white}{title} {cyan}{dashes}╮{reset}"
    return f"{cyan}╭{'─' * (WIDTH + 2)}╮{reset}"


def bottom():
    return f"{cyan}╰{'─' * (WIDTH + 2)}╯{reset}"


def center_block(text):
    columns = shutil.get_terminal_size((100, 30)).columns
    return "\n".join(line.center(columns) for line in text.splitlines())


def read_page():
    for candidate in (PAGE_FILE, os.path.join(CONFIG_DIR, "Page.txt")):
        try:
            with open(candidate, "r", encoding="utf-8") as file:
                page = file.read().strip()
            return page if page in pages else "1"
        except Exception:
            continue
    return "1"


def render(page_id):
    section, entries = pages[page_id]

    print(popup_version + center_block(ascii_art))
    print()

    print(top())
    print(row_pair(f"{white}{name_tool}{reset}  {lightblack_ex}•{reset}  {cyan}v{version_tool}{reset}",
                   f"{lightblack_ex}[{white}Developed By {creator}{lightblack_ex}]{reset}"))
    print(bottom())
    print()

    print(top(section))
    print(row())
    for number, label, description in entries:
        if number == "00":
            print(row())
        accent = lightblack_ex if number == "00" else red
        print(row(f"{accent}{number}{reset}  {white}{label:<26}{lightblack_ex}{description}{reset}"))
    print(row())
    print(bottom())
    print()

    print(top("SYSTEM"))
    print(row_pair(
        f"{lightblack_ex}USER{reset}  {white}{username_pc}{reset}",
        f"{lightblack_ex}PAGE{reset}  {white}{page_id}/{len(pages)}{reset}  {lightblack_ex}TIME{reset}  {white}{current_time_hour()}{reset}"
    ))
    print(bottom())


def boot():
    Clear()
    columns = shutil.get_terminal_size((100, 30)).columns
    margin = " " * max(0, (columns - 46) // 2)
    steps = ["resolving paths", "loading configuration", "checking environment", "starting interface"]

    print()
    print()
    for step in steps:
        for frame in SPINNER:
            sys.stdout.write(f"\r{margin}{cyan}{frame}{reset} {lightblack_ex}{pad(step, 34)}{reset}")
            sys.stdout.flush()
            time.sleep(0.035)
        sys.stdout.write(f"\r{margin}{green}✓{reset} {white}{pad(step, 34)}{reset}\n")
        sys.stdout.flush()

    print()
    total = 24
    for percent in range(101):
        filled = total * percent // 100
        bar = f"{cyan}{'█' * filled}{lightblack_ex}{'░' * (total - filled)}{reset}"
        sys.stdout.write(f"\r{margin}{bar} {white}{percent:3d}%{reset}")
        sys.stdout.flush()
        time.sleep(0.011)

    sys.stdout.write(f"\n\n\r{margin}{lightblack_ex}ready{reset} {lightblack_ex}•{reset} {white}{name_tool} {version_tool}{reset}\n")
    sys.stdout.flush()
    time.sleep(0.45)


boot()

while True:

    page_id = read_page()
    Title(f"Page {page_id}")
    Clear()
    render(page_id)

    choice = input(f"\n{cyan}╭─[{white}{username_pc}{cyan}@{white}inquisitor{cyan}]\n{cyan}╰─❯ {reset}").strip().lower()

    if choice in ["1", "01"]:
        StartProgram("webhook_spammer.py")

    elif choice in ["2", "02"]:
        StartProgram("token_nuker.py")

    elif choice in ["3", "03"]:
        StartProgram("token_joiner.py")

    elif choice in ["4", "04"]:
        StartProgram("token_leaver.py")

    elif choice in ["5", "05"]:
        StartProgram("token_login.py")

    elif choice in ["0", "00", "q", "exit"]:
        Exit()

    else:
        ErrorChoiceStart()