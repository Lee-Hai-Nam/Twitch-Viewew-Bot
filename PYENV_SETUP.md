# Setting up CVAmp with Python 3.11 via pyenv on Linux Server

## Install pyenv (if not already installed)

```bash
# Install dependencies needed for building Python
# Ubuntu/Debian
sudo apt update
sudo apt install -y make build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev

# CentOS/RHEL/Rocky Linux
sudo dnf install -y gcc gcc-c++ make zlib-devel bzip2 bzip2-devel readline-devel sqlite sqlite-devel openssl-devel tk-devel libffi-devel xz-devel

# Install pyenv
curl https://pyenv.run | bash

# Add to your shell profile
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
echo 'command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
echo 'eval "$(pyenv init -)"' >> ~/.bashrc

# Reload shell
exec "$SHELL"
```

## Install Python 3.11.0
```bash
# Install Python 3.11.0
pyenv install 3.11.0

# Set as global default for this system
pyenv global 3.11.0

# Verify installation
python --version  # Should show Python 3.11.0
```

## Set up the CVAmp project
```bash
# Clone or copy the CVAmp project
git clone https://github.com/KevinBytesTheDust/cvamp.git
cd cvamp

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install python-dateutil playwright psutil toml sv-ttk

# Install Playwright browsers
playwright install firefox chromium
```

## Run with SOCKS5 and Firefox
```bash
# Make sure your proxy/proxy_list.txt is set up with SOCKS5 proxies like:
# socks5://proxy_ip:port:username:password

# Run the CLI
python main_cli.py --browser firefox --headless --target-url "https://www.twitch.tv/channel_name" --spawn-count 1
```

## For persistent background execution
```bash
# Using nohup
nohup python main_cli.py --browser firefox --headless --target-url "https://www.twitch.tv/channel_name" --spawn-count 5 > cvamp.log 2>&1 &

# Check if it's running
jobs
tail -f cvamp.log
```

## Setting Python 3.11 as default for this project directory (optional)
```bash
# Set Python 3.11.0 for this project specifically
pyenv local 3.11.0

# This creates a .python-version file in the project directory
# Python will automatically use 3.11.0 when in this directory
```