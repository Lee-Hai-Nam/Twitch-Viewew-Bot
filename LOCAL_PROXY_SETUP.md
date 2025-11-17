# Setting up Local Proxy for SOCKS5 Authentication

## The Problem
Playwright doesn't natively support SOCKS5 proxies with authentication. When you have proxies like:
```
socks5://username:password@host:port
```

You need a local HTTP proxy that forwards traffic to your authenticated SOCKS5 proxy.

## Solution: Using px-proxy

### 1. Install px-proxy
```bash
pip install px-proxy
```

### 2. Create a configuration file

Create a file called `px.ini`:
```ini
[proxy]
# Local address to listen on
listen = 127.0.0.1:8080

# Upstream SOCKS5 proxy with authentication
upstream = socks5://username:password@your-socks-proxy-host:port

# Authentication for the local proxy (optional)
# auth = local_user:local_password

# Other settings
workers = 10
threads = 1
digest = false
```

### 3. Run px-proxy to create the local proxy
```bash
px --conf=px.ini
```

### 4. Update CVAmp to use the local proxy
Instead of your original SOCKS5 proxy, configure CVAmp to use:
```
http://127.0.0.1:8080
```

## Alternative: Using SSH Dynamic Port Forwarding

If your SOCKS5 server is accessible via SSH, you can create a tunnel:

```bash
ssh -D 8080 username@proxy-ssh-server.com
```

This creates a SOCKS proxy on localhost:8080 that forwards through SSH.

## Alternative: Using proxychains

1. Install proxychains:
```bash
sudo apt install proxychains  # Ubuntu/Debian
```

2. Create a proxychains config file `~/.proxychains/proxychains.conf`:
```
[ProxyList]
socks5  proxy_host proxy_port username password
```

3. Run CVAmp through proxychains:
```bash
proxychains python main_cli.py --browser chromium --headless --target-url "https://www.twitch.tv/channel_name" --spawn-count 1
```

## Complete Example with px-proxy

### Step 1: Prepare your proxy information
From your proxy file `proxy/proxy_list.txt`, take an entry like:
```
socks5://8xx4luhKrc:06MS4LO0SV@161.8.172.169:9759
```

### Step 2: Create px.ini
```ini
[proxy]
listen = 127.0.0.1:8080
upstream = socks5://8xx4luhKrc:06MS4LO0SV@161.8.172.169:9759
workers = 10
threads = 1
```

### Step 3: Start the local proxy
```bash
px --conf=px.ini
```

### Step 4: Update your proxy file
Change `proxy/proxy_list.txt` to use the local HTTP proxy:
```
127.0.0.1:8080
```

### Step 5: Run CVAmp normally
```bash
python main_cli.py --browser chromium --headless --target-url "https://www.twitch.tv/channel_name" --spawn-count 1
```

## Multiple Proxies with px-proxy

If you have multiple SOCKS5 proxies, you can run multiple px-proxy instances on different ports:

- px-proxy instance 1: socks5://user:pass@host1:port → listens on 127.0.0.1:8080
- px-proxy instance 2: socks5://user:pass@host2:port → listens on 127.0.0.1:8081
- etc.

Then update your proxy file:
```
127.0.0.1:8080
127.0.0.1:8081
127.0.0.1:8082
...
```

## Verification

To verify that your proxy setup is working, you can test it with curl:

```bash
# Check your real IP
curl ifconfig.co

# Check IP via your local proxy (should show proxy IP)
curl --proxy http://127.0.0.1:8080 ifconfig.co
```

## Automation Script

You can create a startup script to automate this process:

```bash
#!/bin/bash
# start_proxies.sh

# Start px-proxy in background for each SOCKS5 proxy
px --conf=px1.ini &
PX_PID1=$!

px --conf=px2.ini &
PX_PID2=$!

# Wait a moment for proxies to start
sleep 2

# Run CVAmp
python main_cli.py --browser chromium --target-url "https://twitch.tv/channel_name" --spawn-count 2

# Cleanup
kill $PX_PID1 $PX_PID2
```

This approach allows you to use your authenticated SOCKS5 proxies with CVAmp while working within Playwright's limitations.