# CVAmp with SOCKS5 Authentication Support

## New Feature: SOCKS5 with Authentication

CVAmp now supports SOCKS5 proxies with authentication using the `slippers` library as a workaround for Playwright's limitations.

### How It Works

Playwright doesn't natively support SOCKS5 proxies with authentication. To overcome this limitation, CVAmp now uses the `slippers` library which:

1. Creates a temporary local HTTP proxy server on your machine
2. This local proxy forwards all traffic to your SOCKS5 proxy server with authentication
3. CVAmp browsers connect to this local proxy, which handles the SOCKS5 authentication transparently

### Installation

Install the required dependency:
```bash
pip install slippers
```

Or if using Poetry:
```bash
poetry add slippers
```

### Proxy Format

Your proxy file should contain SOCKS5 proxies with authentication in this format:
```
socks5://username:password@host:port
```

Example `proxy/proxy_list.txt`:
```
socks5://myuser:mypass@127.0.0.1:1080
socks5://8xx4luhKrc:06MS4LO0SV@161.8.172.169:9759
```

### Browser Support

SOCKS5 with authentication now works with both browsers:
- ✅ Chromium (with slippers workaround)
- ✅ Firefox (with slippers workaround)

### Usage

Run normally - the system will automatically detect SOCKS5 with authentication and use the slippers workaround:

```bash
# CLI version
python main_cli.py --browser firefox --headless --target-url "https://www.twitch.tv/channel_name" --spawn-count 1

# Or with Chromium
python main_cli.py --browser chromium --headless --target-url "https://www.twitch.tv/channel_name" --spawn-count 1
```

### Fallback Behavior

If slippers is not installed but SOCKS5 with authentication is configured:
- The application will log a warning
- It will run without proxy (browsers connect directly)
- The application continues to run

### Requirements

- Python 3.11 (as before)
- slippers library (new requirement)
- Playwright browsers (chromium/firefox)

### Troubleshooting

1. **"slippers not installed" error**: Install slippers with `pip install slippers`

2. **"Browser does not support socks5 proxy authentication"**: This error should no longer appear when slippers is installed

3. **SOCKS5 connection issues**: Verify your SOCKS5 server is reachable and credentials are correct

### Benefits

- Full SOCKS5 with authentication support for both Chromium and Firefox
- Seamless integration without changing proxy file format
- Maintains all existing functionality
- Graceful fallback if slippers is not available