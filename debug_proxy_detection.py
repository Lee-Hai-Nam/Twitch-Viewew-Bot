#!/usr/bin/env python3
"""
Debug script to check proxy detection logic
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cvamp.proxy import ProxyGetter

# Test the proxy detection logic that will be used in instance.py
getter = ProxyGetter("proxy_list.txt")
print(f"Found {len(getter.proxy_list)} proxies in proxy list:")

for i, proxy_dict in enumerate(getter.proxy_list):
    print(f"  {i+1}: {proxy_dict}")
    
    # Test the exact same logic from instance.py
    has_socks5_auth = proxy_dict and "socks5://" in proxy_dict.get("server", "") and proxy_dict.get("username", "")
    print(f"    Has SOCKS5 auth: {has_socks5_auth}")
    
    if has_socks5_auth:
        socks_url = f"socks5://{proxy_dict['username']}:{proxy_dict['password']}@{proxy_dict['server'].replace('socks5://', '')}"
        print(f"    SOCKS URL would be: {socks_url}")
    print()