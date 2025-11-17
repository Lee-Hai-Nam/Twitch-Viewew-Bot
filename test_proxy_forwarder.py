#!/usr/bin/env python3
"""
Test script to verify the proxy forwarder functionality
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cvamp.proxy_forwarder import create_socks5_forwarding_proxy

def test_proxy_forwarder():
    print("Testing proxy forwarder...")
    
    # Test with a fake SOCKS5 URL to make sure the parsing works
    try:
        # This will attempt to create a proxy server but fail to connect to the SOCKS5 server
        # (which is expected since we're using fake credentials)
        socks_url = "socks5://testuser:testpass@127.0.0.1:1080"
        
        print(f"Creating proxy forwarder for: {socks_url}")
        
        # This should create the local proxy server even if the upstream SOCKS5 doesn't exist
        proxy_server, local_url = create_socks5_forwarding_proxy(socks_url)
        
        print(f"Local proxy server created: {local_url}")
        print(f"Target SOCKS5: {socks_url}")
        print("Proxy forwarder test completed successfully!")
        
        # Clean up - shutdown the server
        proxy_server.shutdown()
        
    except Exception as e:
        print(f"Error during proxy forwarder test: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    result = test_proxy_forwarder()
    if result:
        print("\nProxy forwarder test PASSED!")
    else:
        print("\nProxy forwarder test FAILED!")
        sys.exit(1)