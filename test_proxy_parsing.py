#!/usr/bin/env python3
from cvamp.proxy import ProxyGetter

# Test the current proxy file
getter = ProxyGetter("proxy_list.txt")  # Just the filename, ProxyGetter adds the path
print(f"Found {len(getter.proxy_list)} proxies:")
for i, proxy in enumerate(getter.proxy_list):
    print(f"  {i+1}: {proxy}")