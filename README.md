# FakeLag

A network lag simulator for online cooperative game testing.

## Overview

FakeLag is a UDP proxy tool that simulates various network conditions including latency, jitter, and packet loss. It's designed to help game developers test how their online cooperative games perform under different network conditions.

## Features

- **Latency Simulation**: Add artificial delay to network packets
- **Jitter Simulation**: Add random variance to latency
- **Packet Loss Simulation**: Drop packets randomly to simulate unreliable connections
- **UDP Proxy**: Transparent UDP packet forwarding with configurable conditions
- **Easy to Use**: Simple command-line interface

## Installation

FakeLag requires Python 3.7 or higher and has no external dependencies.

```bash
# Make the script executable
chmod +x fakelag.py
```

## Usage

Basic usage:

```bash
python3 fakelag.py -p LOCAL_PORT -r REMOTE_HOST:REMOTE_PORT [OPTIONS]
```

### Options

- `-p, --port`: Local port to listen on (required)
- `-r, --remote`: Remote host to forward to in format `host:port` (required)
- `-l, --latency`: Base latency in milliseconds (default: 0)
- `-j, --jitter`: Latency variance (jitter) in milliseconds (default: 0)
- `-d, --drop`: Packet loss percentage, 0-100 (default: 0)

### Examples

1. **Simulate 100ms latency**:
   ```bash
   python3 fakelag.py -p 7777 -r gameserver.com:7777 -l 100
   ```

2. **Simulate poor connection (200ms latency, 50ms jitter, 5% packet loss)**:
   ```bash
   python3 fakelag.py -p 7777 -r gameserver.com:7777 -l 200 -j 50 -d 5
   ```

3. **Simulate extreme lag (500ms latency, 100ms jitter, 10% packet loss)**:
   ```bash
   python3 fakelag.py -p 7777 -r gameserver.com:7777 -l 500 -j 100 -d 10
   ```

4. **Test packet loss only**:
   ```bash
   python3 fakelag.py -p 7777 -r gameserver.com:7777 -d 15
   ```

## How It Works

FakeLag creates a UDP proxy server that:
1. Listens on the specified local port
2. Receives packets from game clients
3. Applies the configured network conditions (delay, jitter, packet loss)
4. Forwards packets to the actual game server
5. Applies the same conditions to response packets

Clients should connect to `localhost:LOCAL_PORT` instead of directly to the game server.

## Use Cases

- **Game Development**: Test how your game handles poor network conditions
- **QA Testing**: Reproduce network-related bugs
- **Performance Testing**: Verify game remains playable under various latencies
- **Player Experience**: Understand how different players around the world experience your game

## Notes

- This tool works with UDP traffic only (most online games use UDP)
- Press `Ctrl+C` to stop the proxy
- All network conditions are applied bidirectionally (client↔server)

## Security

**⚠️ Security Notice**: FakeLag binds to all network interfaces (0.0.0.0) to allow testing from different machines on your network. This is intentional but means:

- The proxy will accept connections from any machine that can reach your computer
- Only run FakeLag on trusted networks (your home/office LAN)
- Do not expose the proxy port to the internet
- Consider using a firewall to restrict access if needed
- This tool is meant for development/testing environments, not production

For local-only testing, clients can connect to `localhost:LOCAL_PORT` or `127.0.0.1:LOCAL_PORT`.

## License

This is a simple testing tool for online cooperative games.
