#!/usr/bin/env python3
"""
Test script to verify the anti-detection and user agent features
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cvamp.anti_detect import get_random_user_agent, get_anti_detection_script, get_common_user_agents

def test_user_agents():
    print("Testing user agent generation...")
    
    # Test different browser types
    chrome_ua = get_random_user_agent("chromium")
    firefox_ua = get_random_user_agent("firefox")
    other_ua = get_random_user_agent("safari")  # Should default to Chrome
    
    print(f"Chrome UA: {chrome_ua}")
    print(f"Firefox UA: {firefox_ua}")
    print(f"Other (default Chrome) UA: {other_ua}")
    
    # Verify they're different and not empty
    assert chrome_ua and "Chrome" in chrome_ua, "Chrome UA should contain 'Chrome'"
    assert firefox_ua and "Firefox" in firefox_ua, "Firefox UA should contain 'Firefox'"
    assert other_ua and ("Chrome" in other_ua or "Safari" in other_ua), "Default should contain Chrome/Safari"
    
    print("User agent tests passed!")
    return True

def test_anti_detection_script():
    print("\nTesting anti-detection script...")
    
    script = get_anti_detection_script()
    
    # Check that it contains important elements
    checks = [
        ("webdriver detection removal", "webdriver" in script),
        ("plugins override", "plugins" in script),
        ("languages override", "languages" in script),
        ("permissions override", "permissions" in script),
        ("WebGL spoofing", "WebGL" in script),
        ("automation indicators removal", "cdc_" in script),
    ]
    
    for check_name, condition in checks:
        if condition:
            print(f"  [PASS] {check_name}")
        else:
            print(f"  [FAIL] {check_name}")
    
    # All should be present
    if all(condition for _, condition in checks):
        print("Anti-detection script tests passed!")
        return True
    else:
        print("Some anti-detection script tests failed!")
        return False

def test_common_user_agents():
    print("\nTesting common user agents dictionary...")
    
    agents = get_common_user_agents()
    
    expected_browsers = ["chrome", "firefox", "safari"]
    
    for browser in expected_browsers:
        if browser in agents and len(agents[browser]) > 0:
            print(f"  [PASS] {browser.capitalize()} agents available: {len(agents[browser])}")
        else:
            print(f"  [FAIL] {browser.capitalize()} agents missing or empty")
            return False
    
    print("Common user agents tests passed!")
    return True

def main():
    print("Testing anti-detection and user agent features...\n")
    
    tests = [
        test_user_agents,
        test_anti_detection_script,
        test_common_user_agents,
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"Error in {test.__name__}: {e}")
            results.append(False)
    
    print(f"\nOverall result: {'PASS' if all(results) else 'FAIL'}")
    return 0 if all(results) else 1

if __name__ == "__main__":
    sys.exit(main())