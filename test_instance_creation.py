#!/usr/bin/env python3
"""
Test script to verify the complete slippers integration including lifecycle management
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cvamp.instance import Instance
from cvamp.utils import InstanceStatus
import threading


def dummy_status_reporter(instance_id, status):
    print(f"Instance {instance_id} status: {status}")


def test_instance_creation():
    print("Testing instance creation with SOCKS5 auth...")
    
    # Create a mock proxy dict with SOCKS5 auth (similar to your setup)
    proxy_dict = {
        'server': 'socks5://161.8.172.169:9759',
        'username': '8xx4luhKrc',
        'password': '06MS4LO0SV'
    }
    
    print(f"Proxy dict: {proxy_dict}")
    
    # Test instance creation
    instance = Instance(
        proxy_dict=proxy_dict,
        target_url="https://www.twitch.tv/test_channel",
        status_reporter=dummy_status_reporter,
        instance_id=1,
        browser_type="chromium"
    )
    
    print(f"Instance created with proxy: {instance.proxy_dict}")
    print(f"Has SOCKS5 auth check: {bool('socks5://' in proxy_dict.get('server', '') and proxy_dict.get('username', ''))}")
    print(f"Instance slippers_proxy initially: {instance.slippers_proxy}")
    print(f"Instance local_proxy_url initially: {instance.local_proxy_url}")
    
    # Check that the instance has the right properties
    print(f"Instance ID: {instance.id}")
    print(f"Browser type: {instance.browser_type}")
    
    print("Test completed!")


if __name__ == "__main__":
    test_instance_creation()