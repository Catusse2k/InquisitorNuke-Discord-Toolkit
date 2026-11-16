import os
import sys
import stat
import platform
import subprocess

BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(BASE)
IS_WIN = platform.system() == "Windows"
IS_LINUX = platform.system() == "Linux"
VENV = os.path.join(ROOT, ".venv")
PY = os.path.join(VENV, "Scripts", "python.exe") if IS_WIN else os.path.join(VENV, "bin", "python")
REQUIREMENTS = os.path.join(ROOT, "requirements.txt")

DEFAULT_PACKAGES = ["requests", "colorama", "selenium", "PyQt5", "PyQtWebEngine"]
LINUX_SYSTEM = ["libgl1", "libnss3", "libxcomposite1", "libxdamage1", "libxrandr2", "libxtst6", "libasound2", "libgbm1", "libxcb-cursor0"]


def step(text):
    print(f"[*] {text}")


def ok(text):
    print(f"[+] {text}")


def fail(text):
    print(f"[x] {text}")
    sys.exit(1)


def run(args):
    return subprocess.run(args, cwd=ROOT, check=True)


if sys.version_info < (3, 10):
    fail(f"Python 3.10+ required, found {platform.python_version()}")

if IS_WIN:
    os.system("")
else:
    os.system("clear")

print()
print("  InquisitorNuke setup")
print("  --------------------")
print()

step("checking platform")
if not (IS_WIN or IS_LINUX):
    fail(f"unsupported platform: {platform.system()}")
ok(platform.system())

step("preparing virtual environment")
if os.path.isdir(VENV):
    ok("already present")
else:
    run([sys.executable, "-m", "venv", VENV])
    ok("created")

step("upgrading pip")
run([PY, "-m", "pip", "install", "--upgrade", "pip", "--disable-pip-version-check", "-q"])
ok("updated")

if not os.path.isfile(REQUIREMENTS):
    with open(REQUIREMENTS, "w", encoding="utf-8") as file:
        file.write("\n".join(DEFAULT_PACKAGES) + "\n")
    ok("requirements.txt generated")

step("installing dependencies")
run([PY, "-m", "pip", "install", "-r", REQUIREMENTS, "--disable-pip-version-check", "-q"])
ok("installed")

step("verifying imports")
try:
    run([PY, "-c", "import requests, colorama, selenium, PyQt5.QtWebEngineWidgets"])
    ok("imports working")
except subprocess.CalledProcessError:
    if IS_LINUX:
        fail("missing system libraries, run: sudo apt install " + " ".join(LINUX_SYSTEM))
    fail("Qt WebEngine not working")

step("creating project files")
for path, content in {
    "TokenDisc.txt": "",
    "config/__init__.py": "",
    "config/page.txt": "1",
}.items():
    full = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    if not os.path.isfile(full):
        with open(full, "w", encoding="utf-8") as file:
            file.write(content)
ok("done")

step("writing launchers")
with open(os.path.join(ROOT, "run.bat"), "w", encoding="utf-8", newline="\r\n") as file:
    file.write('@echo off\ncd /d "%~dp0"\n".venv\\Scripts\\python.exe" start.py\npause\n')

sh_path = os.path.join(ROOT, "run.sh")
with open(sh_path, "w", encoding="utf-8", newline="\n") as file:
    file.write('#!/usr/bin/env bash\ncd "$(dirname "$0")"\n./.venv/bin/python start.py\n')
os.chmod(sh_path, os.stat(sh_path).st_mode | stat.S_IEXEC)
ok("run.bat / run.sh")

print()
ok("setup complete")
print("    start with: run.bat" if IS_WIN else "    start with: ./run.sh")
print()