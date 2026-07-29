
# WebDisplay Server V1.0

> **Work in progress**

Server to manage and control WebDisplay Devices.

> Note: This repository serves as the starting point for the dedicated WebDisplay server implementation. It will eventually replace the internal WebDisplay server and transition the system to a more centralized control architecture.

<!-- ## Documentation

### Getting Started

#### Debian Based Install

Install dependencies:

    sudo apt update
    sudo apt install -y python3 python3-pip git

Create required directories and create and pull git repository:

    mkdir archives
    mkdir WebDisplay
    cd WebDisplay
    git init
    git remote add origin https://github.com/C2311231/WebDisplay.git
    git pull origin main

Create virtual env and install python requirements

    python -m venv .venv
    source .venv/bin/activate
    pip install --break-system-packages -r requirements.txt ## If using CEC replace "requirements.txt" with "requirements_cec.txt"
    deactivate

#### (Optional) Run on boot

Create system service

    sudo nano /etc/systemd/system/WebDisplay.service

Paste this config (Fill in placeholders {})

    [Unit]
    Description=WebDisplay Service

    [Install]
    WantedBy=default.target

    [Service]
    User={Username}
    Restart=always
    ExecStart=/{path/to/WebDisplay/directory}/.venv/bin/python3 /{path/to/WebDisplay/directory}/main.py db.db {port}
    WorkingDirectory=/{path/to/WebDisplay/directory}

### Usage

#### Running Manually:

    /{path/to/WebDisplay/directory}/.venv/bin/python3 /{path/to/WebDisplay/directory}/main.py db.db {port}

#### Accessing the Web Interface:

The web interface is available at: http://{server ip}:{port}  
Other devices should automatically be detected and added to the side menu. -->