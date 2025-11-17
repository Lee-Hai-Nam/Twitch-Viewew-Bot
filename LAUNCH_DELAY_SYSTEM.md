# CVAmp Instance Launch Delay System

## Overview

CVAmp now includes a randomized delay system between instance launches to better distribute resource usage and avoid launching all instances simultaneously.

## Feature Details

- **Delay Range**: 30-60 seconds (randomized per instance)
- **Per-Instance**: Each instance gets its own random delay before launching
- **Automatic**: No additional configuration required
- **Non-blocking**: Does not affect the main thread scheduling

## How It Works

When spawning instances:

1. Main thread schedules instances at intervals defined by `spawn_interval_seconds` (default: 2 seconds)
2. Each instance thread waits for a random delay of 30-60 seconds before initialization
3. This results in staggered instance launches, reducing resource spikes
4. All delays happen in background threads without blocking scheduling

## Benefits

- **Resource Management**: Prevents CPU/memory spikes from launching many instances at once
- **Network Distribution**: Reduces network connection bursts
- **Better Performance**: Smoother operation under heavy instance loads
- **Automatic Operation**: Works without additional configuration

## Configuration

The delay is automatically applied and cannot be disabled. The range (30-60 seconds) is hardcoded but can be modified by editing the `spawn_instance_thread` method in `cvamp/manager.py`.