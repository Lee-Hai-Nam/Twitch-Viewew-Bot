# CVAmp Anti-Detection and User Agent Features

## Overview

The CVAmp application now includes advanced anti-detection capabilities and dynamic user agent rotation to help browser instances appear more legitimate and avoid bot detection mechanisms.

## Features Added

### 1. Random User Agent Rotation
- Automatically selects a random user agent from a pool of realistic browser signatures
- Supports different user agents for Chrome/Chromium and Firefox browsers
- Rotates user agent for each instance to avoid fingerprinting

### 2. Comprehensive Anti-Detection Script
The application now injects JavaScript that:
- Removes webdriver detection properties
- Spoofs browser plugins information
- Modifies language settings to appear legitimate
- Overrides permissions API to prevent detection
- Fakes WebGL vendor/renderer information
- Removes automation-indicating properties and variables

### 3. Browser-Specific User Agents
- **Chrome/Chromium**: Modern Chrome user agent strings
- **Firefox**: Realistic Firefox user agent strings
- **Safari**: Safari browser signatures (for completeness)

## Implementation Details

### User Agent Generation
The system selects random user agents from a curated list of real, current browser signatures:

**Chrome:**
- `Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36`
- `Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36`
- `Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36`

**Firefox:**
- `Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0`
- `Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/115.0`
- `Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0`

### Anti-Detection Script Features
```javascript
// Removes webdriver property that indicates automation
Object.defineProperty(navigator, 'webdriver', { get: () => undefined });

// Spoofs plugins (prevents detection based on plugin count)
Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });

// Sets common languages
Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });

// Overrides permissions API
// Spoofs WebGL information
// Removes automation-indicating variables
```

## Integration

The anti-detection features are automatically applied to all instances:
1. Random user agent is selected when spawning a page
2. Anti-detection script is injected into each page
3. Features work with both:
   - Regular proxy configurations
   - SOCKS5 with authentication (via local proxy server)
   - HTTP proxies

## Benefits

- **Reduced Detection Risk**: Makes browser instances harder to identify as automated
- **Improved Performance**: Reduces likelihood of being blocked by anti-bot systems
- **Enhanced Legitimacy**: More realistic browser fingerprinting characteristics
- **Automatic Application**: Features work without additional configuration

## Technical Architecture

The features are implemented in:
- `cvamp/anti_detect.py` - User agent generation and anti-detection script
- `cvamp/instance.py` - Integration with browser instance creation

All features are backwards compatible and don't affect existing functionality.