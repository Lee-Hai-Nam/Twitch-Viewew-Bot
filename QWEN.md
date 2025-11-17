# CVAmp (Crude Viewer Amplifier) - Project Overview

## Project Description
CVAmp is a Python-based GUI application that spawns multiple muted Google Chrome instances via Playwright, each with a different HTTP proxy connection. Each instance navigates to a streaming channel and selects the lowest possible resolution to amplify viewer counts on streaming platforms like Twitch, YouTube, and Kick. The application provides a visual interface to manage these instances with a color-coded status system.

## Architecture
The project is organized as follows:

- `cvamp/` - Main source package containing all application logic
  - `main_gui.py` - Entry point for the application
  - `cvamp/gui.py` - GUI implementation using Tkinter
  - `cvamp/manager.py` - Core instance management logic
  - `cvamp/instance.py` - Base class for browser instances
  - `cvamp/sites.py` - Site-specific implementations for Twitch, YouTube, Kick, and Chzzk
  - `cvamp/proxy.py` - Proxy management and configuration
  - `cvamp/utils.py` - Utility functions and enums
  - `cvamp/logger_config.py` - Logging configuration

## Supported Platforms
- Twitch: Full support for viewer amplification
- YouTube: Full support for viewer amplification
- Kick: Full support for viewer amplification
- Chzzk: Support for viewer amplification

## Core Features
- GUI interface with color-coded status indicators:
  - ⬛ - Instance is spawned
  - 🟨 - Instance is buffering
  - 🟩 - Instance is actively watching
- Interactive controls: Left-click to refresh, Right-click to destroy, Ctrl+Left-click to screenshot
- Proxy support through proxy_list.txt file
- Automatic quality selection (lowest possible resolution)
- Headless and headful operation modes
- Auto-restart functionality
- Performance monitoring (CPU and RAM usage)

## Configuration
- Proxies are configured in `proxy/proxy_list.txt`
- Supported formats:
  - `ip:port:username:password` for authenticated proxies
  - `ip:port` for simple proxies
- Configuration constants are set in `main_gui.py`:
  - SPAWNER_THREAD_COUNT: Number of threads for spawning instances
  - CLOSER_THREAD_COUNT: Number of threads for destroying instances
  - HEADLESS: Whether to run Chrome in headless mode
  - AUTO_RESTART: Whether to automatically restart instances
  - SPAWN_INTERVAL_SECONDS: Delay between spawning instances

## Building and Running

### Prerequisites
- Python 3.11.x
- Chrome browser installed on the system
- HTTP proxies (provided by user)

### Setup
1. Install dependencies using Poetry:
   ```bash
   poetry install
   ```
2. Install Playwright browsers:
   ```bash
   poetry run playwright install chromium
   ```
3. Set up proxy list in `proxy/proxy_list.txt`

### Running
```bash
poetry run python main_gui.py
```

### Development
The project uses Poetry for dependency management and follows standard Python development practices. Code formatting is handled by Black, and linting by Pylint.

### Building Executable
The project can be built as a single executable using PyInstaller:
```bash
poetry run pyinstaller main_gui.py --onefile --add-data "cvamp_logo.ico;." --add-data "pyproject.toml;."
```

## Key Technologies
- Python 3.11+
- Playwright for browser automation
- Tkinter for GUI
- Poetry for dependency management
- Psutil for system monitoring
- PyInstaller for executable packaging

## Important Notes
- This tool is for educational purposes only
- Using this tool may violate streaming platform Terms of Service
- Users must provide their own private HTTP proxies
- Heavy CPU and bandwidth usage expected with multiple instances
- Tested primarily on Windows 10 with experimental support for Linux and macOS