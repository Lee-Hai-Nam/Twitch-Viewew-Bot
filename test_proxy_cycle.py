#!/usr/bin/env python3
"""
Test to check if proxies are being configured correctly
"""
import os
from cvamp.proxy import ProxyGetter

# Test the current proxy file
getter = ProxyGetter("proxy_list.txt")  # ProxyGetter adds the 'proxy/' path automatically
print(f"Found {len(getter.proxy_list)} proxies in proxy list:")

for i, proxy in enumerate(getter.proxy_list):
    print(f"  {i+1}: {proxy}")
    
print("\nTesting proxy cycling (first 3 proxies that would be used):")
for i in range(3):
    proxy = getter.get_proxy_as_dict()
    print(f"  Cycle {i+1}: {proxy}")
    # Put it back to maintain the list (since get_proxy_as_dict rotates the list)
    if proxy:
        getter.proxy_list.pop(0)  # Remove the one at the front
        getter.proxy_list.append(proxy)  # Put it at the end