# CVAmp CLI - Simple Setup Guide

## Quick Setup

1. **Install Python 3.11 and dependencies:**
```bash
sudo apt update
sudo apt install python3.11 python3-pip
pip3 install python-dateutil playwright psutil toml sv-ttk
playwright install firefox
```

2. **Prepare your SOCKS5 proxy file:**
Create `proxy/proxy_list.txt` and add your SOCKS5 proxies in this format:
```
socks5://proxy_ip:port:username:password
```

3. **Run CVAmp with Firefox and SOCKS5:**
```bash
python3 main_cli.py --browser firefox --headless --target-url "https://www.twitch.tv/channel_name" --spawn-count 1
```

That's it! The application will start with Firefox using your SOCKS5 proxy.