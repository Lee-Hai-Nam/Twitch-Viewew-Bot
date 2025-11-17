# CVAmp - Simple Linux Setup Guide

## Install Dependencies
```bash
sudo apt update
sudo apt install -y python3.11 python3.11-venv python3-pip git chromium-browser
```

## Setup CVAmp
```bash
git clone https://github.com/KevinBytesTheDust/cvamp.git
cd cvamp
python3 -m venv venv
source venv/bin/activate
pip install python-dateutil playwright psutil toml sv-ttk
playwright install chromium
```

## Configure Proxies
Edit `proxy/proxy_list.txt` with your proxies:
```
socks5://user:pass@proxy_ip:port
```

## Run CVAmp
```bash
source venv/bin/activate
python main_cli.py --browser chromium --headless --target-url "https://twitch.tv/channel" --spawn-count 2
```

That's it! The builtin proxy system handles SOCKS5 authentication automatically.