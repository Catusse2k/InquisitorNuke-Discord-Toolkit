from .config import *

import colorama
import ctypes
import subprocess
import getpass
import os
import re
import time
import sys
import datetime
import requests

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROGRAM_DIR = os.path.join(ROOT, "program")
CONFIG_DIR = os.path.join(ROOT, "config")
START_FILE = os.path.join(ROOT, "start.py")
TOKEN_FILE = os.path.join(ROOT, "TokenDisc.txt")
LOGO_FILE = os.path.join(ROOT, "Img", "blueTiger_Icon.ico")
PAGE_FILE = os.path.join(CONFIG_DIR, "page.txt")

color_webhook = 0xa80505
username_webhook = name_tool
avatar_webhook = "https://media.discordapp.net/attachments/1184160374342299688/1223987317908181073/blueTiger_Logo.png?ex=661bda05&is=66096505&hm=c567e0e9e672ae70de44ddf128301ae0a6737d78a2f2a9f46ff9f2b717f0ac04&=&format=webp&quality=lossless&width=810&height=810"

color = colorama.Fore
blue = color.BLUE
white = color.WHITE
green = color.GREEN
reset = color.RESET
cyan = color.CYAN
red = color.RED
yellow = color.YELLOW
lightred_ex = color.LIGHTRED_EX
lightblack_ex = color.LIGHTBLACK_EX
lightyellow_ex = color.LIGHTYELLOW_EX

for _attribute in dir(color):
    if _attribute.isupper():
        setattr(color, _attribute.lower(), getattr(color, _attribute))

DISCORD_API = "https://discord.com/api/v10"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) discord/1.0.9189 Chrome/138.0.7204.251 Electron/37.5.0 Safari/537.36"

TOKEN_REGEX = re.compile(r"^[\w-]{20,40}\.[\w-]{5,8}\.[\w-]{20,50}$")
WEBHOOK_REGEX = re.compile(r"^https?://(?:ptb\.|canary\.)?discord(?:app)?\.com/api/(?:v\d+/)?webhooks/\d{17,20}/[\w-]{50,150}(?:\?.*)?$")
CHANNEL_REGEX = re.compile(r"^\d{17,20}$")

if os.name == "nt":
    os.system("")
    colorama.init(convert=True)
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stdin.reconfigure(encoding="utf-8")
    except Exception:
        pass
else:
    colorama.init()
    os.environ.setdefault("QTWEBENGINE_CHROMIUM_FLAGS", "--no-sandbox")

try:
    username_pc = getpass.getuser()
except Exception:
    username_pc = "user"

INPUT = f'{blue}[{white}>{blue}] |'
INFO = f'{blue}[{white}!{blue}] |'
WARN = f'{yellow}[{white}!{yellow}] |'
ERROR = f'{blue}[{white}x{blue}] |'
ADD = f'{blue}[{white}+{blue}] |'
WAIT = f'{blue}[{white}~{blue}] |'

GEN_VALID = f'{green}[{white}+{green}] |'
GEN_INVALID = f'{blue}[{white}x{blue}] |'


def current_time_day_hour():
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def current_time_hour():
    return datetime.datetime.now().strftime('%H:%M:%S')

def ModuleInstall(module):
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', module])

def ModuleUninstall(module):
    subprocess.check_call([sys.executable, '-m', 'pip', 'uninstall', module])

def Title(title):
    if os.name == 'nt':
        ctypes.windll.kernel32.SetConsoleTitleW(f"{name_tool} {version_tool} | {title}")
    else:
        sys.stdout.write(f"\x1b]2;{name_tool} {version_tool} | {title}\x07")
        sys.stdout.flush()

def Reset():
    subprocess.run([sys.executable, START_FILE], cwd=ROOT)

def Clear():
    os.system("cls" if os.name == 'nt' else "clear")

def Exit():
    sys.exit()

def StartProgram(program):
    target = os.path.join(PROGRAM_DIR, program)
    if not os.path.isfile(target):
        print(f"\n{red}missing file{reset}: {target}")
        Continue()
        return
    result = subprocess.run([sys.executable, target], cwd=ROOT)
    if result.returncode != 0:
        print(f"\n{red}exit code {result.returncode}{reset}")
        Continue()

def Continue():
    input(color.blue + f"{INFO} Press to continue -> " + color.RESET)

def ErrorChoiceStart():
    print(f"\n{color.blue}{ERROR} Invalid Choice !", color.RESET)
    time.sleep(1)

def ErrorChoice():
    print(f"{color.blue}{ERROR} Invalid Choice !", color.RESET)
    time.sleep(3)
    Reset()

def ErrorId():
    print(f"{color.blue}{ERROR} Invalid ID !", color.RESET)
    time.sleep(3)
    Reset()

def ErrorUrl():
    print(f"{color.blue}{ERROR} Invalid URL !", color.RESET)
    time.sleep(3)
    Reset()

def Errobluege():
    print(f"{color.blue}{ERROR} Browser not installed or driver not up to date !")
    time.sleep(3)
    Reset()

def ErrorToken():
    print(f"{color.blue}{ERROR} Invalid Token !", color.RESET)
    time.sleep(3)
    Reset()

def ErrorNumber():
    print(f"{color.blue}{ERROR} Invalid Number !", color.RESET)
    time.sleep(3)
    Reset()

def ErrorWebhook():
    print(f"{color.blue}{ERROR} Invalid Webhook !", color.RESET)
    time.sleep(3)
    Reset()

def ErrorCookie():
    print(f"{color.blue}{ERROR} Invalid Cookie !", color.RESET)
    time.sleep(3)
    Reset()

def ErrorUsername():
    print(f"{color.blue}{ERROR} Invalid Username !", color.RESET)
    time.sleep(3)
    Reset()

def ErrorModule(e):
    print(f"{color.blue}{ERROR} Error Module (run setup/setup.bat): {white}{e}", color.RESET)
    time.sleep(5)
    Reset()


def DiscordHeaders(token=None):
    headers = {
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.9",
        "Content-Type": "application/json",
        "User-Agent": USER_AGENT,
        "X-Discord-Locale": "en-US",
        "X-Discord-Timezone": "Europe/Rome",
    }
    if token:
        headers["Authorization"] = CleanToken(token)
    return headers


def CleanToken(token):
    token = (token or "").strip().strip('"').strip("'")
    if token.lower().startswith("bot "):
        token = token[4:].strip()
    return token


def DiscordRequest(method, endpoint, token=None, payload=None, params=None, attempts=4):
    for _ in range(attempts):
        try:
            r = requests.request(method, f"{DISCORD_API}{endpoint}", headers=DiscordHeaders(token), json=payload, params=params, timeout=15)
        except requests.RequestException:
            return None
        if r.status_code == 429:
            try:
                wait = float(r.json().get("retry_after", 1))
            except Exception:
                wait = float(r.headers.get("Retry-After", 1))
            time.sleep(min(wait, 30) + 0.15)
            continue
        return r
    return None


def GetTokenUser(token):
    token = CleanToken(token)
    if not TOKEN_REGEX.match(token):
        return None
    r = DiscordRequest("GET", "/users/@me", token=token)
    if r is None or r.status_code != 200:
        return None
    try:
        return r.json()
    except Exception:
        return None


def CensorToken(token):
    parts = token.split(".")
    if len(parts) != 3:
        return f"{token[:10]}...{token[-4:]}"
    return f"{parts[0][:8]}...{parts[2][-4:]}"


def PrintToken(number, token, user):
    if user:
        name = user.get("global_name") or user.get("username") or "unknown"
        print(f"{white}[{blue}{number}{white}]{blue} -> {blue}Status: {white}Valid{blue} | User: {white}{name}{blue} | Token: {white}{CensorToken(token)}")
    else:
        print(f"{white}[{blue}{number}{white}]{blue} -> {blue}Status: {white}Invalid{blue} | Token: {white}{token}")


def ReadTokenFile(path=None):
    path = path or TOKEN_FILE
    tokens = {}
    if not os.path.isfile(path):
        return tokens
    number = 0
    with open(path, "r", encoding="utf-8") as file_token:
        for line in file_token:
            token = CleanToken(line)
            if not token:
                continue
            if token in tokens.values():
                continue
            number += 1
            tokens[number] = token
    return tokens


def CheckWebhook(webhook):
    webhook = (webhook or "").strip().strip('"').strip("'")
    webhook = webhook.replace("discordapp.com", "discord.com")

    if WEBHOOK_REGEX.match(webhook):
        return webhook

    if webhook.startswith(("http://", "https://")):
        try:
            probe = requests.get(webhook, timeout=10, allow_redirects=True, headers={"User-Agent": USER_AGENT})
            final = probe.url.replace("discordapp.com", "discord.com")
            if WEBHOOK_REGEX.match(final):
                return final
            if "/api/webhooks/" in final:
                return final
            match = re.search(r"https?://discord(?:app)?\.com/api/webhooks/[\w/-]+", probe.text or "")
            if match:
                return match.group(0)
        except requests.RequestException:
            pass

    print(f"\n{color.blue}{ERROR} Invalid webhook: expected a discord.com/api/webhooks URL or a link that redirects to one.{color.RESET}")
    time.sleep(2)
    return None


def ChoiceMultiChannelDiscord():
    try:
        num_channels = int(input(f"{INPUT} How many spam channels -> {reset}"))
    except ValueError:
        ErrorNumber()

    selected_channels = []
    number = 0
    for _ in range(num_channels):
        number += 1
        selected_channel_number = input(f"{color.blue}{INPUT} Channel Id {number}/{num_channels} -> {color.RESET}").strip()
        if not CHANNEL_REGEX.match(selected_channel_number):
            ErrorId()
        selected_channels.append(selected_channel_number)

    print(selected_channels)
    return selected_channels


def ChoiceMultiTokenDisord():
    tokens = ReadTokenFile()

    if not tokens:
        print(f"{ERROR} No token in file: {white}{TOKEN_FILE}")
        Continue()
        Reset()
        return []

    print(f"{INFO} {white}{len(tokens)}{blue} Token found ({white}{TOKEN_FILE}{blue})")

    try:
        num_tokens = int(input(f"{INPUT} How many token (max {len(tokens)}) -> {reset}"))
    except Exception:
        ErrorNumber()

    if num_tokens > len(tokens) or num_tokens < 1:
        ErrorNumber()

    print()
    print(f"{blue}Token ({white}{TOKEN_FILE}{blue}):")
    for number, token in tokens.items():
        PrintToken(number, token, GetTokenUser(token))

    selected_tokens = []
    print()
    for number in range(1, num_tokens + 1):
        try:
            selected_token_number = int(input(f"{color.blue}{INPUT} Token {number}/{num_tokens} -> {color.RESET}"))
        except Exception:
            ErrorNumber()

        selected_token = tokens.get(selected_token_number)
        if not selected_token:
            ErrorNumber()
        if selected_token in selected_tokens:
            continue
        selected_tokens.append(selected_token)
    return selected_tokens


def Choice1TokenDiscord():
    tokens = ReadTokenFile()

    if not tokens:
        print(f"{ERROR} No token in file: {white}{TOKEN_FILE}")
        Continue()
        Reset()
        return None

    print(f"{blue}Token ({white}{TOKEN_FILE}{blue}):")
    for number, token in tokens.items():
        PrintToken(number, token, GetTokenUser(token))

    try:
        selected_token_number = int(input(f"\n{color.blue}{INPUT} Token -> {color.RESET}"))
    except Exception:
        ErrorChoice()

    selected_token = tokens.get(selected_token_number)
    if not selected_token:
        ErrorChoice()
    return selected_token


def BrowserPrivate(site, search_bar=True, title="Navigateur Web"):
    try:
        from PyQt5.QtWidgets import QApplication, QMainWindow, QLineEdit, QVBoxLayout, QWidget
        from PyQt5.QtGui import QIcon
        from PyQt5.QtCore import QUrl, Qt
        from PyQt5.QtWebEngineWidgets import QWebEngineView
    except Exception as e:
        ErrorModule(e)

    class WebBrowserApp(QMainWindow):
        def __init__(self, url=None, width=1000, height=300, search_bar=True, title="Navigateur Web"):
            super().__init__()
            self.setWindowTitle(title)

            self.search_bar = search_bar
            self.url_entry = QLineEdit()
            self.url_entry.returnPressed.connect(self.load_url)
            self.url_entry.setText(url or "")
            self.url_entry.setVisible(self.search_bar)

            self.webview = QWebEngineView()

            layout = QVBoxLayout()
            if self.search_bar:
                layout.addWidget(self.url_entry)
            layout.addWidget(self.webview)

            central_widget = QWidget()
            central_widget.setLayout(layout)
            self.setCentralWidget(central_widget)

            if url:
                self.load_url()
            if os.path.isfile(LOGO_FILE):
                self.setWindowIcon(QIcon(LOGO_FILE))

            self.setWindowFlags(Qt.Window | Qt.CustomizeWindowHint | Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint)

        def toggle_search_bar(self, visible):
            self.url_entry.setVisible(visible)

        def load_url(self):
            url = self.url_entry.text().strip()
            if not url:
                return
            if not url.startswith(("http://", "https://")):
                url = f"https://{url}"
                self.url_entry.setText(url)
            self.webview.load(QUrl(url))

        def contextMenuEvent(self, event):
            pass

    def main():
        app = QApplication(sys.argv)
        app.setStyleSheet("""
            QMainWindow {
                background-color: #1c1c1c;
                color: #ffffff;
            }
            QLineEdit {
                background-color: #333333;
                color: #ffffff;
                border: 1px solid #555555;
                padding: 5px;
            }
            QWebEngineView {
                background-color: #1c1c1c;
                color: #ffffff;
                border: none;
            }
        """)
        browser = WebBrowserApp(url=site, width=500, height=10, search_bar=search_bar, title=f"{name_tool} {version_tool} | {title}")
        browser.show()
        sys.exit(app.exec_())

    main()