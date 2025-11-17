#!/usr/bin/env python3
"""
CLI version of CVAmp for Linux server usage with SOCKS5 proxy support
"""
import argparse
import datetime
import signal
import sys
import threading
import time

from cvamp.manager import InstanceManager


def signal_handler(sig, frame):
    print(f'\nReceived interrupt signal. Shutting down manager gracefully at {datetime.datetime.now()}')
    if hasattr(signal_handler, 'manager'):
        signal_handler.manager.delete_all_instances()
    sys.exit(0)


def main():
    parser = argparse.ArgumentParser(description='CVAmp CLI - Viewer Amplifier with SOCKS5 proxy support')
    parser.add_argument('--browser', type=str, default='chromium', choices=['chromium', 'firefox'],
                        help='Browser type to use (default: chromium)')
    parser.add_argument('--headless', action='store_true', default=True,
                        help='Run in headless mode (default: True)')
    parser.add_argument('--no-headless', action='store_false', dest='headless',
                        help='Run in headed mode')
    parser.add_argument('--auto-restart', action='store_true', default=False,
                        help='Enable auto restart of instances (default: False)')
    parser.add_argument('--proxy-file', type=str, default='proxy_list.txt',
                        help='Proxy list file name (default: proxy_list.txt)')
    parser.add_argument('--spawner-threads', type=int, default=3,
                        help='Number of spawner threads (default: 3)')
    parser.add_argument('--closer-threads', type=int, default=10,
                        help='Number of closer threads (default: 10)')
    parser.add_argument('--spawn-interval', type=int, default=2,
                        help='Interval between spawns in seconds (default: 2)')
    parser.add_argument('--spawn-count', type=int, default=1,
                        help='Number of instances to spawn (default: 1)')
    parser.add_argument('--target-url', type=str, required=True,
                        help='Target URL to watch (required)')
    parser.add_argument('--no-wait', action='store_true', default=False,
                        help='Exit immediately after spawning instances (default: False)')

    args = parser.parse_args()

    print(f"Starting CVAmp CLI with {args.browser} browser, headless={args.headless}")
    print(f"Target URL: {args.target_url}")
    print(f"Proxy file: {args.proxy_file}")
    print(f"Browser: {args.browser}")
    
    # Set up signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    manager = InstanceManager(
        spawn_thread_count=args.spawner_threads,
        delete_thread_count=args.closer_threads,
        headless=args.headless,
        auto_restart=args.auto_restart,
        proxy_file_name=args.proxy_file,
        spawn_interval_seconds=args.spawn_interval,
        browser_type=args.browser,  # Add browser type
    )

    # Store manager reference for signal handler
    signal_handler.manager = manager

    print(f"Available proxies: {len(manager.proxies.proxy_list)}")
    
    # Spawn the requested number of instances
    print(f"Spawning {args.spawn_count} {args.browser} instance(s)...")
    manager.spawn_instances(args.spawn_count, args.target_url)
    
    if args.no_wait:
        print("Launched instances and exiting immediately.")
        return
    
    # Set up periodic status display
    def display_status():
        while True:
            try:
                alive = manager.instances_alive_count
                watching = manager.instances_watching_count
                print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] "
                      f"Alive: {alive}, Watching: {watching}")
                time.sleep(10)  # Update every 10 seconds
            except:
                break  # Exit if manager is destroyed

    status_thread = threading.Thread(target=display_status, daemon=True)
    status_thread.start()

    print("Instances running. Press Ctrl+C to stop.")
    
    try:
        # Keep the main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print(f'\nReceived interrupt signal. Shutting down manager gracefully at {datetime.datetime.now()}')
        manager.delete_all_instances()


if __name__ == "__main__":
    main()