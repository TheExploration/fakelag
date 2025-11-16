# fakelag

A network latency simulation tool for online coop testing.

## Overview

FakeLag is a UDP proxy that simulates network latency, jitter, and packet loss. It's designed for testing multiplayer games and networked applications under various network conditions.

## Features

- **Latency Simulation**: Add configurable delay to network packets
- **Jitter Simulation**: Add random variation to packet timing
- **Packet Loss**: Simulate unreliable network conditions
- **UDP Proxy**: Transparent proxy for UDP-based protocols
- **Easy to Use**: Simple command-line interface

## Installation

### From Source

```bash
git clone https://github.com/TheExploration/fakelag.git
cd fakelag
pip install -e .
```

### Direct Usage

You can also run the script directly without installation:

```bash
python3 fakelag.py --help
```

## Usage

### Basic Usage

Forward local port 7777 to a game server at gameserver.example.com:7777 with 100ms latency:

```bash
fakelag --local-port 7777 --target-host gameserver.example.com --target-port 7777 --latency 100
```

### With Jitter

Add 100ms latency with ±20ms jitter:

```bash
fakelag --local-port 7777 --target-host gameserver.example.com --target-port 7777 --latency 100 --jitter 20
```

### With Packet Loss

Add 100ms latency and 5% packet loss:

```bash
fakelag --local-port 7777 --target-host gameserver.example.com --target-port 7777 --latency 100 --packet-loss 0.05
```

### All Options

```bash
fakelag --local-port LOCAL_PORT \
        --target-host TARGET_HOST \
        --target-port TARGET_PORT \
        [--latency MILLISECONDS] \
        [--jitter MILLISECONDS] \
        [--packet-loss PROBABILITY]
```

## Command-Line Options

- `--local-port`: Port to listen on for incoming client connections (required)
- `--target-host`: Target server hostname or IP address (required)
- `--target-port`: Target server port (required)
- `--latency`: Additional latency in milliseconds (default: 0)
- `--jitter`: Random jitter variation in milliseconds (default: 0)
- `--packet-loss`: Packet loss probability between 0.0 and 1.0 (default: 0.0)
- `--bind-host`: Host address to bind to (default: 0.0.0.0 for all interfaces, use 127.0.0.1 for localhost only)

## Example Scenarios

### Testing Poor WiFi Connection

Simulate a typical poor WiFi connection with 150ms latency, ±30ms jitter, and 2% packet loss:

```bash
fakelag --local-port 7777 --target-host gameserver.com --target-port 7777 \
        --latency 150 --jitter 30 --packet-loss 0.02
```

### Testing Mobile Network

Simulate a 4G mobile connection with 80ms latency and ±15ms jitter:

```bash
fakelag --local-port 7777 --target-host gameserver.com --target-port 7777 \
        --latency 80 --jitter 15
```

### Testing High Packet Loss

Simulate extreme packet loss (10%) for stress testing:

```bash
fakelag --local-port 7777 --target-host gameserver.com --target-port 7777 \
        --latency 100 --packet-loss 0.10
```

## How It Works

1. FakeLag creates a UDP proxy that listens on the specified local port
2. When clients connect to the local port, packets are intercepted
3. Packets are delayed according to the configured latency and jitter
4. Packets may be randomly dropped based on the packet loss rate
5. Delayed packets are forwarded to the target server
6. The same process applies to responses from the server back to clients

## Use Cases

- **Game Development**: Test multiplayer games under various network conditions
- **QA Testing**: Validate behavior with poor connections
- **Network Research**: Study protocol behavior under different conditions
- **Performance Testing**: Identify issues that only appear with latency

## Limitations

- Currently supports UDP traffic only
- Bidirectional traffic simulation is simplified (may need enhancement for production use)
- Not recommended for production traffic routing

## Security Considerations

**Important**: FakeLag binds to all network interfaces (0.0.0.0) by default to accept connections. This means:

- The proxy will accept connections from any network interface on your machine
- If you're on a shared network, other machines may be able to connect to your proxy
- **For security, use a firewall to restrict access to the local port**
- **Only use FakeLag in trusted development/testing environments**
- **For local-only testing, use `--bind-host 127.0.0.1` to bind to localhost only**

Example for localhost-only binding:
```bash
fakelag --local-port 7777 --target-host gameserver.com --target-port 7777 \
        --bind-host 127.0.0.1 --latency 100
```

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## License

MIT License - see LICENSE file for details
