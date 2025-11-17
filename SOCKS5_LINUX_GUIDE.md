# CVAmp CLI Guide for Linux Server with SOCKS5 Proxies

## Prerequisites

### System Requirements
- Linux server (Ubuntu/Debian/CentOS/RHEL)
- Python 3.11 installed
- Chrome/Firefox browser installed (for Chromium/Firefox respectively)

### Install Python 3.11
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3.11 python3.11-venv python3.11-dev python3-pip

# CentOS/RHEL/Rocky Linux
sudo dnf install python311 python311-devel python3-pip
```

## Installation

### 1. Clone or Download CVAmp
```bash
git clone https://github.com/KevinBytesTheDust/cvamp.git
cd cvamp
```

### 2. Set Up Virtual Environment (Recommended)
```bash
python3 -m venv venv
source venv/bin/activate  # Activate virtual environment
```

### 3. Install Dependencies
```bash
pip install python-dateutil playwright psutil toml sv-ttk
```

### 4. Install Playwright Browsers
```bash
# For Chromium support
playwright install chromium

# For Firefox support (if you plan to use Firefox)
playwright install firefox

# For WebKit (optional)
playwright install webkit
```

### 5. Prepare Proxy List
Create your proxy file at `proxy/proxy_list.txt` in one of these formats:
```
# SOCKS5 format (no auth)
socks5://127.0.0.1:1080
socks5://192.168.1.100:1080

# SOCKS5 format (with auth)
socks5://username:password@proxy-server.com:1080

# SOCKS5 with separate fields format
socks5:127.0.0.1:1080:username:password
socks5:192.168.1.100:1080:user:pass

# Regular HTTP proxies (for comparison)
127.0.0.1:8080
proxy-server.com:8080:username:password
```

## Running CVAmp CLI

### Basic Usage
```bash
# Run with Firefox browser, headless mode, SOCKS5 proxies
python main_cli.py --browser firefox --headless --target-url "https://www.twitch.tv/channel_name" --spawn-count 5

# Run with Chromium browser
python main_cli.py --browser chromium --headless --target-url "https://www.youtube.com/channel" --spawn-count 3

# Run with custom proxy file
python main_cli.py --browser firefox --proxy-file my_custom_proxy_file.txt --target-url "https://www.twitch.tv/channel_name" --spawn-count 10
```

### All Available Options
```bash
python main_cli.py --help
```

Common options:
- `--browser {chromium,firefox}`: Browser type (default: chromium)
- `--headless`: Run in headless mode (default: True)
- `--no-headless`: Run in headed mode (shows browser windows)
- `--auto-restart`: Enable auto restart of instances
- `--proxy-file PROXY_FILE`: Proxy list file name (default: proxy_list.txt)
- `--spawner-threads SPAWNER_THREADS`: Number of spawner threads (default: 3)
- `--closer-threads CLOSER_THREADS`: Number of closer threads (default: 10)
- `--spawn-interval SPAWN_INTERVAL`: Interval between spawns in seconds (default: 2)
- `--spawn-count SPAWN_COUNT`: Number of instances to spawn (default: 1)
- `--target-url TARGET_URL`: Target URL to watch (required)
- `--no-wait`: Exit immediately after spawning instances (default: False)

### Examples

#### Example 1: Basic Firefox with SOCKS5
```bash
python main_cli.py --browser firefox --headless --target-url "https://www.twitch.tv/my_channel" --spawn-count 5
```

#### Example 2: Firefox with auto-restart and custom proxy file
```bash
python main_cli.py --browser firefox --headless --auto-restart --proxy-file socks5_proxies.txt --target-url "https://www.youtube.com/channel" --spawn-count 10
```

#### Example 3: Chromium with multiple parameters
```bash
python main_cli.py --browser chromium --headless --spawn-count 3 --spawner-threads 5 --closer-threads 15 --spawn-interval 1 --target-url "https://www.twitch.tv/channel_name"
```

### Running in Background

#### Using nohup
```bash
# Run in background and log output
nohup python main_cli.py --browser firefox --headless --target-url "https://www.twitch.tv/channel_name" --spawn-count 5 > cvamp.log 2>&1 &

# Get the process ID
echo $!
```

#### Using screen
```bash
# Install screen (if not installed)
sudo apt install screen

# Start a screen session
screen -S cvamp_session

# Run CVAmp
python main_cli.py --browser firefox --headless --target-url "https://www.twitch.tv/channel_name" --spawn-count 5

# Detach from screen: Ctrl+A, then D
# Reattach to screen: screen -r cvamp_session
```

#### Using tmux
```bash
# Install tmux (if not installed)
sudo apt install tmux

# Create a new tmux session
tmux new-session -d -s cvamp_session

# Run CVAmp in the session
tmux send-keys -t cvamp_session 'python main_cli.py --browser firefox --headless --target-url "https://www.twitch.tv/channel_name" --spawn-count 5' Enter

# Attach to session: tmux attach -t cvamp_session
# Detach from session: Ctrl+B, then D
```

### Monitoring and Management

#### Check running processes
```bash
ps aux | grep python
# or specifically for CVAmp
ps aux | grep main_cli.py
```

#### Stop CVAmp
```bash
# Find the process ID
ps aux | grep main_cli.py

# Kill by PID
kill <PID>

# Or kill all Python processes with main_cli.py (be careful!)
pkill -f "main_cli.py"
```

#### Check logs
CVAmp creates a `cvamp.log` file that you can monitor:
```bash
tail -f cvamp.log
```

## Tips for Linux Server Usage

### 1. Set up a Systemd Service (Optional)
Create a service file at `/etc/systemd/system/cvamp.service`:
```
[Unit]
Description=CVAmp Viewer Amplifier
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/path/to/cvamp
Environment=PATH=/path/to/cvamp/venv/bin
ExecStart=/path/to/cvamp/venv/bin/python main_cli.py --browser firefox --headless --target-url "https://www.twitch.tv/channel_name" --spawn-count 5
Restart=always

[Install]
WantedBy=multi-user.target
```

Then enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable cvamp
sudo systemctl start cvamp
sudo systemctl status cvamp  # Check status
```

### 2. Install Chrome/Chromium for Linux
```bash
# Ubuntu/Debian
sudo apt install chromium-browser

# Or Google Chrome
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
sudo sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
sudo apt update
sudo apt install google-chrome-stable
```

### 3. Resource Management
Monitor resource usage:
```bash
# CPU and memory
htop

# Network usage
nethogs
# or
iftop
```

### 4. Security Considerations
- Store proxy credentials securely
- Limit access to the server
- Use SSH keys for server access
- Keep the system updated

## Troubleshooting

### Common Issues

1. **Browser not found error**
   - Ensure Playwright browsers are installed: `playwright install chromium firefox`
   - Ensure Chrome/Firefox is installed on the system

2. **Permission errors**
   - Run commands with appropriate permissions
   - Ensure write access to working directory for log files

3. **Proxy connection errors**
   - Verify proxy format in proxy list file
   - Test proxy connectivity independently
   - Check proxy authentication credentials

4. **Memory issues with many instances**
   - Reduce the number of concurrent instances
   - Increase server resources if possible
   - Monitor memory usage with `htop`

5. **Display issues (if running headed)**
   - For GUI applications on headless servers, use Xvfb:
   ```bash
   sudo apt install xvfb
   Xvfb :99 -screen 0 1024x768x24 &
   export DISPLAY=:99
   ```

## Important Notes

- For SOCKS5 proxy authentication, format as: `socks5://username:password@host:port` or `socks5:host:port:username:password`
- The CLI version is designed for server environments without X11 display requirements
- Always run in headless mode for server usage to reduce resource consumption
- Monitor system resources when running many browser instances
- SOCKS5 proxies may have different performance characteristics than HTTP proxies