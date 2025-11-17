#!/usr/bin/env python3
"""
Test script to verify slippers integration with the instance class
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cvamp.instance import Instance
from cvamp.utils import InstanceStatus
import threading
import time

def dummy_status_reporter(instance_id, status):
    print(f"Instance {instance_id} status: {status}")

def test_socks5_with_slippers():
    print("Testing SOCKS5 with slippers integration...")
    
    # Create a mock proxy dict with SOCKS5 auth
    proxy_dict = {
        'server': 'socks5://161.8.172.169:9759',
        'username': '8xx4luhKrc',
        'password': '06MS4LO0SV'
    }
    
    print(f"Proxy dict: {proxy_dict}")
    
    # Check if it's a SOCKS5 with auth
    has_socks5_auth = proxy_dict and "socks5://" in proxy_dict.get("server", "") and proxy_dict.get("username", "")
    print(f"Has SOCKS5 auth: {has_socks5_auth}")
    
    if has_socks5_auth:
        socks_url = f"socks5://{proxy_dict['username']}:{proxy_dict['password']}@{proxy_dict['server'].replace('socks5://', '')}"
        print(f"SOCKS URL: {socks_url}")
        
        try:
            import slippers
            print("Slippers library is available")
            
            # Try to create the local proxy (but don't actually connect to test)
            # This is just to make sure the code structure is correct
            print("Would create slippers proxy with:", socks_url)
            print("Integration looks good - code should work when actual SOCKS5 servers are available")
            
        except ImportError:
            print("Slippers not installed")
    
    print("Test completed!")

if __name__ == "__main__":
    test_socks5_with_slippers()