#!/usr/bin/env python3
"""
Test script to check if slippers proxy creation works in the current environment
"""
try:
    import slippers
    print("Slippers is importable")
    
    # Test creating a slippers proxy with a fake SOCKS5 URL
    # Note: This will fail to connect to the fake server, but should create the local proxy
    socks_url = "socks5://fakeuser:fakepass@192.0.2.0:1080"
    
    print(f"Creating slippers proxy for: {socks_url}")
    
    proxy_obj = slippers.proxy(socks_url)
    local_proxy_url = proxy_obj.__enter__()
    
    print(f"Local proxy URL created: {local_proxy_url}")
    
    # Clean up
    proxy_obj.__exit__(None, None, None)
    print("Proxy cleaned up successfully")
    
    print("Slippers is working correctly!")

except ImportError as e:
    print(f"Slippers import error: {e}")
except Exception as e:
    print(f"Slippers proxy creation error: {e}")
    print("This is expected if the SOCKS5 server is unreachable, but the local proxy should still be created")
    # Even if the server is unreachable, the local proxy should be created
    import slippers
    socks_url = "socks5://fakeuser:fakepass@127.0.0.1:1080"  # Use localhost to avoid network errors if possible
    
    print(f"Trying with localhost: {socks_url}")
    proxy_obj = slippers.proxy(socks_url)
    local_proxy_url = proxy_obj.__enter__()
    print(f"Local proxy URL created: {local_proxy_url}")
    proxy_obj.__exit__(None, None, None)
    print("Local proxy test completed")