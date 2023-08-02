# Tanks Battle Server
[![CodeQL](https://github.com/werryxgames/Tanks-Battle-Server/actions/workflows/codeql.yml/badge.svg?branch=master)](https://github.com/werryxgames/Tanks-Battle-Server/actions/workflows/codeql.yml)
[![Code tests](https://github.com/werryxgames/Tanks-Battle-Server/actions/workflows/tests.yml/badge.svg?branch=master)](https://github.com/werryxgames/Tanks-Battle-Server/actions/workflows/tests.yml)

Official server for multiplayer game «Tanks Battle»

You can download «Tanks Battle» from **[WX\_BY\_0 server](http://185.6.27.126)**

# Installation
## Linux
Run command
```bash
cd ~ && sudo apt-get update -y && sudo apt-get install git python -y && git clone https://github.com/werryxgames/Tanks-Battle-Server.git && cd Tanks-Battle-Server && pip install --upgrade pip && pip install -r requirements.txt && python src/main.py
```
to install all dependencies and start server

Add ` --nogui` to the end, to start server without GUI

To start server after first run, simply write
```bash
python ~/Tanks-Battle-Server/src/main.py
```

## Windows
Download code of this repository

Unzip downloaded file to folder

Install [Python](https://python.org/download)

Open terminal (Press Win + R, write `cmd.exe` and press `Enter`)

Run
```bash
cd <Extracted server path>
python src/main.py
```

Add ` --nogui` to the end, to start server without GUI

To start server after first run, simply write
```bash
python <Extracted server path>/src/main.py
```

## Android
Download Termux from F-Droid

Run Termux and write
```bash
termux-setup-storage && cd /sdcard && apt-get update -y && apt-get install git python -y && git clone https://github.com/werryxgames/Tanks-Battle-Server && cd Tanks-Battle-Server && pip install --upgrade pip && pip install -r requirements.txt && python src/main.py
```

You can add ` --nogui` to the end, but Termux haven't GUI by default

To start server after first run, simply write
```bash
python /sdcard/Tanks-Battle-Server/src/main.py
```

# Updating server
## GUI
Stop server

Go to directory with **Tanks Battle Server**

Copy file `accounts.json` to directory, outside of server

Delete **Tanks Battle Server**

Follow [Installation](installation) steps

Move `accounts.json` to new server directory

**Note! Only player data will save**, all configuration and tanks characteristics will be updated

## Linux (Termux)
Stop server

Go to directory with **Tanks Battle Server** (using `cd`)

Run command
```bash
rm tbsold_accounts.json; cp src/accounts.json ../tbsold_accounts.json; rm ../Tanks-Battle-Server -rf && cd .. && git clone https://github.com/werryxgames/Tanks-Battle-Server && mv tbsold_accounts.json Tanks-Battle-Server/accounts.json
```

# Updating
## Updating accounts
To update accounts, use `update/accounts.py`:
`python update/accounts.py <path to old accounts.json>`

It will update content of file to newest format

Example:
```json
[
    {
        "nick": "Werryx",
        "password": "...",
        "xp": 1234,
        "crystals": 567,
        "tanks": [
            1,
            2
        ],
        "guns": [
            0
        ],
        "pts": [
            1
        ],
        "selected_tank": 0,
        "selected_gun": 0,
        "selected_pt": -1,
        "settings": [
            true,
            true,
            1500
        ]
    }
]
```
will be replaced by
```json
[
    {
        "nick": "Werryx",
        "password": "...",
        "xp": 1234,
        "crystals": 567,
        "tanks": [
            0,
            1
        ],
        "selected_tank": 0,
        "settings": [
            true,
            true,
            1500
        ]
    }
]
```

Added tank with ID *0*, it's given by default; pt wasn't selected (*-1*), so `selected_tank` changed to *0*

# Versions
Version support statuses:

**full** - Bug-fixing and security improvements
**security** - Only security fixes
**none** - Unsupported

| Version | Support status     | Approzimate change status date |
| ------- | ------------------ | ------------------------------ |
| 2.0     | **full**           | 18.01.2023                     |
| 1.5.0   | **full**           | 24.12.2022                     |
| 1.4.0   | **full**           | 24.11.2022                     |
| 1.3.0   | **full**           | 24.09.2022                     |
| 1.2.0   | **security**       | 30.06.2023                     |
| 1.1.0   | **security**       | 30.06.2023                     |
| 1.0.0   | **none**           |                                |
