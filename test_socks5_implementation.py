#!/usr/bin/env python3
"""
Test script to verify the SOCKS5 proxy and Firefox implementation works with the updated CVAmp code
"""
import os
import sys
import tempfile

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cvamp.proxy import ProxyGetter
from cvamp.manager import InstanceManager


def test_proxy_parsing():
    """Test that the proxy parsing works with SOCKS5 format"""
    print("Testing proxy parsing...")
    
    # Create a temporary proxy file with SOCKS5 format
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        # Test various SOCKS5 formats
        f.write("socks5://127.0.0.1:1080\n")
        f.write("socks5:127.0.0.1:1080:username:password\n")
        f.write("socks5:127.0.0.1:1080:password\n")  # No username
        f.write("127.0.0.1:8080\n")  # Regular HTTP proxy
        f.write("socks5://username:password@127.0.0.1:1080\n")  # Auth format
        proxy_file = f.name
    
    try:
        getter = ProxyGetter(proxy_file_name=proxy_file)
        print(f"Successfully parsed {len(getter.proxy_list)} proxies")
        
        for i, proxy in enumerate(getter.proxy_list):
            print(f"  Proxy {i+1}: {proxy}")
        
        # Clean up
        os.unlink(proxy_file)
        return True
    except Exception as e:
        print(f"Error in proxy parsing: {e}")
        if os.path.exists(proxy_file):
            os.unlink(proxy_file)
        return False


def test_manager_creation():
    """Test creating manager with Firefox and SOCKS5"""
    print("\nTesting manager creation with Firefox...")
    
    # Create a temporary proxy file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("socks5://127.0.0.1:1080\n")
        proxy_file = f.name
    
    try:
        # Create manager with Firefox
        manager = InstanceManager(
            spawn_thread_count=1,
            delete_thread_count=1,
            headless=True,  # Use headless for testing
            auto_restart=False,
            proxy_file_name=proxy_file,
            spawn_interval_seconds=1,
            browser_type="firefox"
        )
        
        print(f"Manager created successfully with browser type: {manager.get_browser_type()}")
        print(f"Available proxies: {len(manager.proxies.proxy_list)}")
        
        # Test switching browser type
        manager.set_browser_type("chromium")
        print(f"Browser type changed to: {manager.get_browser_type()}")
        
        # Clean up
        manager.delete_all_instances()
        os.unlink(proxy_file)
        return True
    except Exception as e:
        print(f"Error in manager creation: {e}")
        import traceback
        traceback.print_exc()
        if os.path.exists(proxy_file):
            os.unlink(proxy_file)
        return False


def test_cli_help():
    """Test that CLI works"""
    print("\nTesting CLI help output...")
    try:
        import subprocess
        result = subprocess.run([sys.executable, "main_cli.py", "--help"], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("CLI help output works correctly")
            # Print first few lines to verify
            lines = result.stdout.split('\n')
            for line in lines[:10]:  # First 10 lines
                print(f"  {line}")
            return True
        else:
            print(f"CLI help failed with return code {result.returncode}")
            print(f"Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"Error in CLI test: {e}")
        return False


def main():
    print("Testing SOCKS5 and Firefox implementation in CVAmp...")
    
    tests = [
        ("Proxy parsing", test_proxy_parsing),
        ("Manager creation", test_manager_creation),
        ("CLI functionality", test_cli_help),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"Running {test_name} test...")
        try:
            result = test_func()
            results.append((test_name, result))
            status = "PASSED" if result else "FAILED"
            print(f"{test_name} test: {status}")
        except Exception as e:
            print(f"{test_name} test: ERROR - {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
    
    print(f"\n{'='*50}")
    print("Test Summary:")
    all_passed = True
    for test_name, result in results:
        status = "PASSED" if result else "FAILED"
        print(f"  {test_name}: {status}")
        if not result:
            all_passed = False
    
    if all_passed:
        print("\nAll tests PASSED! SOCKS5 and Firefox implementation is working correctly.")
        return 0
    else:
        print("\nSome tests FAILED!")
        return 1


if __name__ == "__main__":
    sys.exit(main())