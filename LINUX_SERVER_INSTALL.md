# CVAmp Installation and Setup Guide for Linux Server

## Prerequisites

### System Requirements
- Ubuntu 20.04+ / Debian 10+ / CentOS 8+ / RHEL 8+
- Python 3.11
- At least 4GB RAM (recommended for multiple instances)
- Sufficient disk space (especially for logs)
- Root or sudo access

## Step 1: Install System Dependencies

```bash
# For Ubuntu/Debian
sudo apt update
sudo apt install -y python3.11 python3.11-venv python3.11-dev python3-pip git curl wget build-essential libssl-dev libffi-dev

# For CentOS/RHEL/Rocky Linux
sudo dnf update -y
sudo dnf install -y python3.11 python3.11-pip python3.11-devel git curl wget gcc gcc-c++ openssl-devel libffi-devel make

# For Amazon Linux 2
sudo yum update -y
sudo yum install -y python3.11 python3.11-pip python3.11-devel git curl wget gcc gcc-c++ openssl-devel libffi-devel make
```

## Step 2: Install Playwright Browsers

```bash
# Install Chrome dependencies (most reliable for servers)
sudo apt install -y chromium-browser chromium-chromedriver

# Or install via snap (if apt doesn't work)
sudo snap install chromium

# For CentOS/RHEL
sudo dnf install -y chromium
```

## Step 3: Clone and Setup CVAmp

```bash
# Clone the repository
cd ~
git clone https://github.com/KevinBytesTheDust/cvamp.git
cd cvamp

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install Python dependencies
pip install python-dateutil playwright psutil toml sv-ttk
```

## Step 4: Install Playwright Browsers

```bash
# Install Playwright browsers
playwright install chromium firefox

# If you encounter issues, try installing with specific flags
playwright install chromium
```

## Step 5: Configure Proxy List

```bash
# Navigate to proxy directory
cd ~/cvamp/proxy

# Create your proxy list file with SOCKS5 proxies (if using authentication)
# Format: socks5://username:password@host:port
nano proxy_list.txt

# Example content:
# socks5://user1:pass1@proxy1.com:1080
# socks5://user2:pass2@proxy2.com:1080
# socks5://user3:pass3@proxy3.com:1080
```

## Step 6: Handle SOCKS5 with Authentication (Recommended Method)

For SOCKS5 proxies with authentication, install `px-proxy` instead of relying on the internal solution:

```bash
# Install px-proxy
pip install px-proxy

# Create a px configuration file for each proxy
# Create px1.ini for first proxy:
cat > ~/cvamp/px1.ini << 'EOF'
[proxy]
listen = 127.0.0.1:8080
upstream = socks5://your_username:your_password@your_socks_host:your_port
workers = 10
threads = 1
digest = false
EOF

# Create px2.ini for second proxy:
cat > ~/cvamp/px2.ini << 'EOF'
[proxy]
listen = 127.0.0.1:8081
upstream = socks5://your_username2:your_password2@your_socks_host2:your_port2
workers = 10
threads = 1
digest = false
EOF

# Update your proxy/proxy_list.txt to use local HTTP proxies:
echo -e "127.0.0.1:8080\n127.0.0.1:8081" > ~/cvamp/proxy/proxy_list.txt
```

## Step 7: Install Additional Dependencies for Ad Detection

```bash
# Activate virtual environment
source ~/cvamp/venv/bin/activate

# Install any additional requirements that may be needed
pip install python-socks
```

## Step 8: Run CVAmp

### Method 1: Using px-proxy (Recommended for SOCKS5 with authentication)

```bash
# First, start px-proxy in background for each local proxy
cd ~/cvamp
source venv/bin/activate

# Start px-proxy instance 1
nohup px --conf=px1.ini > px1.log 2>&1 &

# Start px-proxy instance 2 (if needed)
nohup px --conf=px2.ini > px2.log 2>&1 &

# Wait a few seconds for proxies to start
sleep 3

# Run CVAmp using the local HTTP proxies
python main_cli.py --browser chromium --headless --target-url "https://www.twitch.tv/your_channel" --spawn-count 2 --spawner-threads 2 --closer-threads 5
```

### Method 2: Direct run (for HTTP proxies or SOCKS5 without authentication)

```bash
# Activate environment
cd ~/cvamp
source venv/bin/activate

# Run directly using the built-in proxy support
python main_cli.py --browser chromium --headless --target-url "https://www.twitch.tv/your_channel" --spawn-count 2
```

## Step 9: Run in Background with Persistence

### Using systemd (recommended for production):

Create a systemd service file:

```bash
sudo tee /etc/systemd/system/cvamp.service << 'EOF'
[Unit]
Description=CVAmp Viewer Amplifier
After=network.target
StartLimitIntervalSec=0

[Service]
Type=simple
Restart=always
RestartSec=1
User=your_username
WorkingDirectory=/home/your_username/cvamp
Environment=PATH=/home/your_username/cvamp/venv/bin
ExecStart=/home/your_username/cvamp/venv/bin/python main_cli.py --browser chromium --headless --target-url "https://www.twitch.tv/your_channel" --spawn-count 5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd
sudo systemctl daemon-reload

# Enable and start the service
sudo systemctl enable cvamp
sudo systemctl start cvamp

# Check status
sudo systemctl status cvamp
```

### Using nohup (alternative method):

```bash
# Create a launch script
cat > ~/cvamp/launch.sh << 'EOF'
#!/bin/bash
cd ~/cvamp
source venv/bin/activate

# Start px-proxy if using SOCKS5 with authentication
nohup px --conf=px1.ini > px1.log 2>&1 &
PX_PID=$!

# Wait for px to start
sleep 3

# Start CVAmp
python main_cli.py --browser chromium --headless --target-url "https://www.twitch.tv/your_channel" --spawn-count 3

# Kill px proxy when done
kill $PX_PID
EOF

chmod +x ~/cvamp/launch.sh

# Run in background
nohup ~/cvamp/launch.sh > cvamp.log 2>&1 &
```

## Step 10: Troubleshooting Common Issues

### Timeout Issues
If experiencing timeouts, try these optimizations:

```bash
# Increase system file descriptor limits
echo "* soft nofile 65536" | sudo tee -a /etc/security/limits.conf
echo "* hard nofile 65536" | sudo tee -a /etc/security/limits.conf
sudo sysctl -p

# Check if browser can be launched manually
source ~/cvamp/venv/bin/activate
python -c "
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto('https://www.google.com', timeout=10000)
    print('Browser launch successful')
    browser.close()
"
```

### Memory Issues
For memory optimization with multiple instances:

```bash
# Reduce spawn interval to avoid resource spikes
python main_cli.py --browser chromium --headless --target-url "https://www.twitch.tv/your_channel" --spawn-count 3 --spawn-interval 5

# Use fewer threads
python main_cli.py --browser chromium --headless --target-url "https://www.twitch.tv/your_channel" --spawner-threads 2 --closer-threads 3 --spawn-count 2
```

### Network Issues
If you get network-related errors:

```bash
# Check if your server can connect to external proxies
telnet your_proxy_host your_proxy_port

# Install additional networking tools if needed
sudo apt install -y dnsutils telnet net-tools
```

## Step 11: Monitoring and Logs

### Check Running Processes
```bash
# Check if CVAmp is running
ps aux | grep python
ps aux | grep cvamp

# Check logs
tail -f ~/cvamp/cvamp.log
tail -f /var/log/syslog | grep cvamp  # if using systemd
```

### Ad Tracking Files
```bash
# Check ad tracking data
cat ~/cvamp/ad_tracking.json
tail -f ~/cvamp/ad_tracking.json
```

### View Server Resources
```bash
# Monitor resources
htop
# or
top

# Check network usage
iftop -i eth0  # replace eth0 with your interface
# or
nethogs
```

## Additional Security Considerations

### Firewall Setup (if needed)
```bash
# Allow necessary ports (adjust as needed)
sudo ufw allow 22/tcp  # SSH
sudo ufw allow 80/tcp  # HTTP
sudo ufw allow 443/tcp # HTTPS
sudo ufw enable
```

### SSL Certificate Updates (if needed)
```bash
# Update certificates if getting SSL errors
sudo apt install ca-certificates
sudo update-ca-certificates
```

## Updating CVAmp

```bash
# Backup important files first
cp ~/cvamp/proxy/proxy_list.txt ~/backup_proxy_list.txt
cp ~/cvamp/ad_tracking.json ~/backup_ad_tracking.json  # if exists

# Update the code
cd ~/cvamp
git pull origin main

# Update dependencies
source venv/bin/activate
pip install --upgrade -r requirements.txt  # if exists
# Or manually update if no requirements.txt
pip install --upgrade python-dateutil playwright psutil toml sv-ttk

# Restart service if using systemd
sudo systemctl restart cvamp
```

This setup should work properly on Linux servers, handling the timeout issues with proper proxy configuration and system optimizations.