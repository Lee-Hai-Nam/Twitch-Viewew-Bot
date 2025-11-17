#!/usr/bin/env python3
"""
Test script to verify SOCKS5 proxy functionality with Firefox in Playwright
"""
import asyncio
from playwright.sync_api import sync_playwright
import sys

def test_firefox_socks5_proxy():
    print("Testing Firefox with SOCKS5 proxy...")
    
    # Example proxy dict for SOCKS5 - this would need to be provided by user
    # Format: {"server": "socks5://127.0.0.1:1080", "username": "user", "password": "pass"}
    proxy_config = {
        "server": "socks5://127.0.0.1:1080",  # This is just an example - replace with real proxy
        # "username": "username",  # Optional
        # "password": "password"   # Optional
    }
    
    try:
        print(f"Launching Firefox with proxy: {proxy_config}")
        
        with sync_playwright() as p:
            # Launch Firefox with SOCKS5 proxy
            browser = p.firefox.launch(
                headless=False,  # Set to True for headless operation
                proxy=proxy_config  # Apply the SOCKS5 proxy
            )
            
            print("Firefox launched successfully")
            
            # Create a new context with the same proxy
            context = browser.new_context(
                proxy=proxy_config,
                # Set viewport and other options as needed
                viewport={"width": 800, "height": 600}
            )
            
            # Create a new page
            page = context.new_page()
            
            # Test navigation to a site to verify proxy is working
            print("Navigating to httpbin.org/ip to check IP...")
            page.goto("https://httpbin.org/ip", timeout=10000)
            
            # Get the content to see if the IP has changed
            content = page.content()
            print("Page content:", content[:500] + "..." if len(content) > 500 else content)
            
            # Wait a bit to see the page
            page.wait_for_timeout(2000)
            
            # Close everything
            context.close()
            browser.close()
            
            print("Test completed successfully!")
            return True
            
    except Exception as e:
        print(f"Error occurred: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Starting SOCKS5 proxy test with Firefox...")
    result = test_firefox_socks5_proxy()
    
    if result:
        print("SOCKS5 proxy test with Firefox: PASSED")
    else:
        print("SOCKS5 proxy test with Firefox: FAILED")
        sys.exit(1)