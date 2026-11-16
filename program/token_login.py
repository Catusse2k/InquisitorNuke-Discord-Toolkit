import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.util import *
from config.config import *

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.common.exceptions import WebDriverException
import base64
import json
import time

Title("Discord Token Login")

token = CleanToken(input(f"{color.BLUE}\n{INPUT} Token -> {color.RESET}"))

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


def decode_payload(tok):
    try:
        part = tok.split(".")[1]
        part += "=" * (-len(part) % 4)
        return json.loads(base64.urlsafe_b64decode(part))
    except Exception:
        return {}


info = decode_payload(token)
if not info:
    print(f"\n{color.blue}{ERROR} Token payload is not decodable, the token is corrupted.{color.RESET}")
    Continue()
    Reset()

user_id = info.get("sub") or info.get("id")
username = info.get("username")
exp = info.get("exp")

if not user_id:
    print(f"{color.blue}{WARN if 'WARN' in globals() else INFO} No account ID inside the payload, continuing anyway.{color.RESET}")
else:
    print(f"{color.blue}{INFO} Account: {color.WHITE}{username or '?'}{color.BLUE} (ID: {color.WHITE}{user_id}{color.BLUE}){color.RESET}")

if exp and exp < time.time():
    print(f"{color.blue}{ERROR} Token expired on {color.WHITE}{time.strftime('%d/%m/%Y %H:%M', time.localtime(exp))}{color.RESET}")
    Continue()
    Reset()

print(f"""
{color.WHITE}[{color.BLUE}01{color.WHITE}] {color.BLUE}->{color.WHITE} Chrome
{color.WHITE}[{color.BLUE}02{color.WHITE}] {color.BLUE}->{color.WHITE} Firefox
{color.WHITE}[{color.BLUE}03{color.WHITE}] {color.BLUE}->{color.WHITE} Edge
""")

choice = input(f"{color.BLUE}{INPUT} Browser -> {color.RESET}").strip()

if choice not in ("1", "2", "3"):
    print(f"\n{color.blue}{ERROR} Invalid choice, pick 1, 2 or 3.{color.RESET}")
    Continue()
    Reset()

navigator = None
driver = None


def harden(opts):
    opts.add_argument("--disable-blink-features=AutomationControlled")
    opts.add_experimental_option("excludeSwitches", ["enable-automation"])
    opts.add_experimental_option("useAutomationExtension", False)
    if os.name != "nt":
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-dev-shm-usage")


try:
    if choice == "1":
        navigator = "Chrome"
        print(f"{color.BLUE}{INFO} {navigator} Starting..{color.RESET}")
        opts = ChromeOptions()
        harden(opts)
        driver = webdriver.Chrome(options=opts)

    elif choice == "2":
        navigator = "Firefox"
        print(f"{color.BLUE}{INFO} {navigator} Starting..{color.RESET}")
        opts = FirefoxOptions()
        opts.set_preference("dom.webdriver.enabled", False)
        driver = webdriver.Firefox(options=opts)

    else:
        navigator = "Edge"
        print(f"{color.BLUE}{INFO} {navigator} Starting..{color.RESET}")
        opts = EdgeOptions()
        harden(opts)
        driver = webdriver.Edge(options=opts)

    driver.maximize_window()
    print(f"{color.BLUE}{INFO} {navigator} Ready !{color.RESET}")

    driver.get("https://discord.com/login")
    time.sleep(1.5)
    print(f"{color.BLUE}{INFO} Token Connection..{color.RESET}")

    driver.execute_script("localStorage.setItem('token', JSON.stringify(arguments[0]));", token)
    driver.refresh()

    deadline = time.time() + 20
    logged = False
    while time.time() < deadline:
        time.sleep(0.5)
        try:
            if "/channels" in driver.current_url:
                logged = True
                break
        except WebDriverException:
            pass

    if logged:
        print(f"{color.BLUE}{INFO} Connected Token !{color.RESET}")
    else:
        print(f"{color.blue}{ERROR} Login not confirmed: invalid token, locked account or captcha required.{color.RESET}")

    print(f"{color.YELLOW}{INFO} If you leave the tool, {navigator} will close!")
    input(f"{color.BLUE}{INPUT} Leave {navigator} (enter) -> {color.WHITE}")
    Reset()

except WebDriverException as e:
    message = str(e).splitlines()[0] if str(e) else "unknown driver error"
    print(f"\n{color.blue}{ERROR} {navigator or 'Browser'} could not start: {message}{color.RESET}")
    print(f"{color.blue}{INFO} Install the browser or update its driver, then retry.{color.RESET}")
    Continue()
    Reset()

except Exception as e:
    print(f"\n{color.blue}{ERROR} {type(e).__name__}: {e}{color.RESET}")
    Continue()
    Reset()

finally:
    if driver is not None:
        try:
            driver.quit()
        except Exception:
            pass