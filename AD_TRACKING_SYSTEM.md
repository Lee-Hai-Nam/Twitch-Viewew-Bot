# CVAmp Ad Tracking System

## Overview

The CVAmp application now includes a comprehensive ad tracking system that detects and logs advertisements across all streaming platforms. The system automatically detects ads on various platforms and maintains statistics about ad viewing activity.

## Features

### 1. Cross-Platform Ad Detection
- **Twitch**: Detects video ads, sponsor ads, and commercial breaks
- **YouTube**: Detects pre-roll, mid-roll, and display ads with skip buttons
- **Kick**: Detects video advertisements and sponsored content
- **Chzzk**: Detects streaming advertisements and promotional content
- **Generic Support**: Basic ad detection for unknown platforms

### 2. Ad Tracking & Logging
- **Instance-Based Counting**: Tracks ads per individual instance
- **Global Statistics**: Maintains total ad count across all instances
- **Timestamp Logging**: Records when each ad was detected
- **Persistent Storage**: Saves ad data to JSON file (ad_tracking.json)

### 3. Data Storage
The system maintains detailed records in `ad_tracking.json` with the structure:
```json
{
  "total_ads_detected": 150,
  "instances": {
    "1": 25,
    "2": 32,
    "3": 18
  },
  "detection_log": [
    {
      "timestamp": "2023-12-07T10:30:45.123456",
      "instance_id": 1,
      "ad_number_for_instance": 5
    }
  ]
}
```

## Implementation Details

### AdDetector Class
- Uses Playwright selectors to identify ad elements
- Platform-specific detection strategies
- Handles rate limiting to avoid false positives
- Integrates with existing update_status loop

### AdTracker Class
- Thread-safe data management
- Automatic file saving when ads are detected
- Automatic log rotation (keeps last 1000 entries)
- Counter maintenance per instance

### Integration
- Automatically integrated into all site-specific classes
- Runs every 10-second loop in the instance lifecycle
- Works with both proxy types (HTTP and SOCKS5 with authentication)

## How It Works

1. **Detection Loop**: Every 10 seconds during instance operation
2. **Platform Identification**: Determines site from target URL
3. **Element Scanning**: Uses Playwright to check for ad indicators
4. **Recording**: Logs ad to file and increments counters
5. **Status Update**: Continues with normal watching status detection

## Detection Methods

### YouTube
- Looks for skip button elements: `.ytp-ad-skip-button`
- Detects ad overlay containers
- Monitors for ad-related text content

### Twitch
- Identifies skip buttons and ad overlays
- Looks for commercial-related class names
- Checks for ad player elements

### Kick & Chzzk
- Platform-specific selectors for ad containers
- Skip button detection
- Content analysis for ad indicators

## Statistics Access

The system provides programmatic access to statistics:
- `get_total_ads_count()`: Global ad count
- `get_instance_ad_count(instance_id)`: Ads for specific instance
- `get_ads_summary()`: Complete summary with recent detections

## File Management

- **Primary File**: `ad_tracking.json` in the application directory
- **Automatic Cleanup**: Maintains only the last 1000 detection entries
- **Thread-Safe**: Protected against race conditions
- **Error Resilient**: Continues operation if file operations fail

## Benefits

- **Analytics**: Track ad consumption patterns
- **Monetization**: Verify ad view requirements
- **Monitoring**: Understand ad frequency across platforms
- **Reporting**: Generate statistics on ad performance
- **Optimization**: Adjust settings based on ad frequency

## Integration Points

The ad tracking system is seamlessly integrated:
- Works with existing proxy functionality
- Compatible with both Firefox and Chromium
- Operates in background during normal instance operation
- Doesn't impact viewing performance
- Maintains existing anti-detection measures