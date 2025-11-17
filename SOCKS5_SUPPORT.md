# CVAmp SOCKS5 Proxy Support Documentation

## Current Status

CVAmp supports SOCKS5 proxies with both Chromium and Firefox browsers, but there's an important limitation with Firefox:

- **Chromium**: Full support for SOCKS5 with authentication
- **Firefox**: Supports SOCKS5 without authentication, but **does NOT support SOCKS5 with authentication** due to Playwright limitations

## Supported Proxy Formats

### HTTP Proxies (4 parts: IP:PORT:USER:PASS) - Works with both browsers
```
127.0.0.1:8080:username:password
```

### SOCKS5 No Authentication (2 parts: IP:PORT) - Works with both browsers
```
socks5://127.0.0.1:1080
```

### SOCKS5 With Authentication - Works with Chromium only
```
socks5://username:password@127.0.0.1:1080
```

## Recommended Approach

### For Firefox with Authentication Required
Use Chromium browser instead when you need SOCKS5 with authentication:

```bash
python main_cli.py --browser chromium --headless --target-url "https://www.twitch.tv/channel_name" --spawn-count 1
```

### For Firefox with SOCKS5 (no auth)
Your proxy file can contain:
```
socks5://127.0.0.1:1080
socks5://proxy-server.com:1080
```

### For Chromium with SOCKS5 authentication
Your proxy file can contain:
```
socks5://username:password@127.0.0.1:1080
```

## Error Messages

If you try to use SOCKS5 with authentication in Firefox, you'll see this warning:
```
Firefox does not support SOCKS5 with authentication. Launching without proxy for instance X.
This is a Playwright limitation. Consider using HTTP proxies or Chromium browser instead.
```

## CLI Options

### Browser Selection
- `--browser firefox`: Use Firefox (no SOCKS5 auth support)
- `--browser chromium`: Use Chromium (full SOCKS5 support)

### Headless Mode
- `--headless`: Run without visible browser windows (default)
- `--no-headless`: Run with visible browser windows (for testing)

## Troubleshooting

### If proxies aren't working
1. Check your proxy format in `proxy/proxy_list.txt`
2. For authentication required: Use Chromium instead of Firefox
3. Verify your proxy server is accessible and credentials are correct
4. Test your proxy separately before using with CVAmp

### For Testing with Headed Mode
```bash
python main_cli.py --no-headless --browser firefox --target-url "https://www.twitch.tv/channel_name" --spawn-count 1
```