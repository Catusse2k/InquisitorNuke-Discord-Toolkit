<div align="center">

# InquisitorNuke

**Cross-platform Discord automation and token operations toolkit**

Modular CLI suite for token management, bulk guild operations, browser session injection, and webhook throughput testing with built-in rate-limit mitigation.

</div>

## Table of Contents

- [Overview](#overview)
- [Feature Matrix](#feature-matrix)
- [Project Structure](#project-structure)
- [System Requirements](#system-requirements)
- [Installation](#installation)
- [Obtaining Required Inputs](#obtaining-required-inputs)
- [Running the Suite](#running-the-suite)
- [Module Reference](#module-reference)
- [Configuration](#configuration)
- [Rate-Limit Model](#rate-limit-model)
- [Troubleshooting](#troubleshooting)
- [FAQ](#faq)
- [Disclaimer](#disclaimer)
- [License](#license)

---

## Overview

**InquisitorNuke** is a menu-driven Python application designed to interface with the Discord REST API through a suite of targeted operational tools. It supports operations involving user tokens and webhook endpoints, featuring input validation, explicit error logging, and a shared rate-limit management layer to handle long-running operations gracefully.

The suite runs on Windows 10/11 and modern Linux distributions featuring a graphical desktop environment. All platform-dependent behaviors (ANSI coloring, console clearing, window titles, and virtual environment paths) are dynamically resolved at runtime.

---

## Feature Matrix

| Module | Purpose | Implementation Notes |
| :--- | :--- | :--- |
| **01 — Webhook Spammer** | High-volume webhook dispatch | Thread pool with per-thread sessions, global/per-bucket 429 rate-limit handling, and randomized jitter. |
| **02 — Token Nuker** | Continuous profile mutation | Loops over custom statuses, 29 locales, three UI themes, and three presence states on a 350 ms tick interval. |
| **03 — Token Joiner** | Guild joining via invite | Pre-resolves invite metadata, automatically retries on 429 status codes, and maps Discord API error codes to human-readable logs. |
| **04 — Token Leaver** | Bulk account detachment from guilds | Paginated fetching (200 guilds/page), three parallel workers, and automated guild deletion for owned guilds. |
| **05 — Token Login** | Live browser session token injection | JWT payload parsing, expiration warnings, hardened Chrome/Firefox/Edge drivers, and session validation polling. |

---

## Project Structure

```text
InquisitorNuke/
├── start.py                  # Main menu entry point and boot sequence
├── config/
│   ├── config.py             # Application metadata, version, and author configuration
│   └── util.py               # API transport layer, validation, helper utilities, ANSI colors
├── program/
│   ├── token_joiner.py       # Invite resolution and server joining logic
│   ├── token_leaver.py       # Guild leave and server deletion orchestrator
│   ├── token_login.py        # Web driver token injection module
│   ├── token_nuker.py        # Profile status and settings mutation loop
│   └── webhook_spammer.py    # Multi-threaded webhook payload dispatcher
└── setup/
    ├── setup.py              # Cross-platform dependency and environment installer
    ├── setup.bat             # Windows launcher for setup.py
    ├── setup_fallback.bat    # Alternative launcher using Windows 'py' launcher
    └── requirements.txt      # Python dependencies list
```

> **Note:** The installation process automatically generates execution scripts `run.bat` (Windows) and `run.sh` (Linux) in the project root directory.

---

## System Requirements

### Operating Systems
* **Windows**: Windows 10 or Windows 11 (64-bit).
* **Linux**: Ubuntu 20.04+, Debian 11+, or equivalent Linux distribution with an active X11/Wayland desktop environment (required for browser driver injection).

### Prerequisites
* **Python**: Version 3.10 or newer (with `venv` module available).
* **Web Browser**: Google Chrome, Mozilla Firefox, or Microsoft Edge (required for the Token Login module).

### Python Dependencies
Installed automatically into a local virtual environment (`.venv`) via `setup/requirements.txt`:
* `requests` — HTTP transport layer.
* `colorama` — ANSI color formatting for Windows terminals.
* `selenium` — Web driver automation for session injection.
* `PyQt5`, `PyQtWebEngine` — Embedded browser components.

### Linux System Dependencies
Qt WebEngine requires native libraries that cannot be installed via `pip`:

```bash
sudo apt update && sudo apt install -y python3 python3-venv python3-pip \
  libgl1 libnss3 libxcomposite1 libxdamage1 libxrandr2 \
  libxtst6 libasound2 libgbm1 libxcb-cursor0
```

---

## Installation

The setup script provisions `.venv`, installs dependencies from `setup/requirements.txt`, validates module imports, and generates system launchers.

### Windows
1. Ensure Python 3.10+ is installed with **"Add Python to PATH"** enabled.
2. Clone or download the repository.
3. Open a console in the project directory and run:
   ```cmd
   setup\setup.bat
   ```
   *(If `python` is not mapped in your environment, execute `setup\setup_fallback.bat` instead).*

### Linux
1. Install native system dependencies listed above.
2. Open terminal in the project root and execute:
   ```bash
   python3 setup/setup.py
   ```
3. The installer grants execution privileges to `run.sh` automatically.

---

## Obtaining Required Inputs

### User Token
1. Open Discord in a web browser and log in.
2. Press `F12` to open Developer Tools and select the **Application** tab.
3. Expand **Local Storage** and select `https://discord.com`.
4. Copy the value stored in the `token` key.

### Webhook URL
1. Open channel settings (*Edit Channel* -> *Integrations* -> *Webhooks*).
2. Create or select a webhook and click **Copy Webhook URL**.

### Invite Link
1. Right-click the server icon and select **Invite People**.
2. Copy the resulting `discord.gg/...` link.

---

## Running the Suite

Use the generated launchers to start the suite in the project root:

* **Windows**: `run.bat`
* **Linux**: `./run.sh`

---

## Configuration

Core configuration settings are stored inside `config/`:

| File | Key Variables | Description |
| :--- | :--- | :--- |
| `config/config.py` | `name_tool`, `version_tool`, `creator` | Identity metadata, versioning, and author attribution strings. |
| `config/util.py` | `USER_AGENT`, `DISCORD_API`, `username_webhook` | HTTP headers, REST base API parameters, and payload defaults. |

---

## Rate-Limit Model

* **429 Handling**: Automatically parses `retry_after` header values and pauses execution.
* **Header Inspection**: Monitored via `X-RateLimit-Remaining` and `X-RateLimit-Reset-After`.
* **Global Rate-Limits**: Signals containing `X-RateLimit-Global` trigger a synchronized thread pause.

---

## Troubleshooting

| Symptom | Cause | Resolution |
| :--- | :--- | :--- |
| `'python' is not recognized` | Python is missing from system `PATH`. | Run `setup\setup_fallback.bat` or reinstall Python with `PATH` enabled. |
| `ModuleNotFoundError` | Script was run directly with system interpreter. | Always launch via `run.bat` or `./run.sh`. |
| Qt libraries missing on Linux | Missing native packages. | Run the `apt install` command listed under System Requirements. |
| WebDriver Exception | Missing browser or driver mismatch. | Ensure Chrome, Firefox, or Edge is installed on the system. |

---

## FAQ

**Does this require a Discord Bot token?**  
No. All modules operate on standard user account tokens and webhooks.

**Can multiple tokens be run concurrently?**  
Modules operate per account session. Launch multiple terminal instances to handle separate accounts simultaneously.

---

## Disclaimer

This software is provided for educational and administrative testing purposes only. Automated operation of user accounts may violate Discord Terms of Service. Use at your own risk.

---

## License

Released under the **MIT License**.

<div align="center">

Developed by **Catusse2k**

</div>
