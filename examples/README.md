# FakeLag Examples

This directory contains example scripts demonstrating how to use FakeLag for testing.

## Examples

### echo_test.py

A simple UDP echo client that demonstrates testing with FakeLag.

**Usage:**

1. **Terminal 1** - Start a UDP echo server:
   ```bash
   # Using netcat
   nc -u -l 7777
   
   # Or using socat
   socat UDP-LISTEN:7777,fork EXEC:'/bin/cat'
   ```

2. **Terminal 2** - Start FakeLag with desired conditions:
   ```bash
   # Simulate good connection (50ms latency, 10ms jitter)
   python3 fakelag.py -p 7778 -r localhost:7777 -l 50 -j 10
   
   # Or simulate poor connection (200ms latency, 50ms jitter, 5% loss)
   python3 fakelag.py -p 7778 -r localhost:7777 -l 200 -j 50 -d 5
   ```

3. **Terminal 3** - Run the test client:
   ```bash
   python3 examples/echo_test.py localhost:7778
   ```

The test client will send packets through the FakeLag proxy and display statistics about round-trip times and packet loss.

## Common Test Scenarios

### Good Connection
```bash
python3 fakelag.py -p 7778 -r gameserver:7777 -l 30 -j 5
```

### Average Connection
```bash
python3 fakelag.py -p 7778 -r gameserver:7777 -l 80 -j 20 -d 1
```

### Poor Connection
```bash
python3 fakelag.py -p 7778 -r gameserver:7777 -l 200 -j 50 -d 5
```

### Terrible Connection
```bash
python3 fakelag.py -p 7778 -r gameserver:7777 -l 500 -j 100 -d 15
```

### Satellite Connection
```bash
python3 fakelag.py -p 7778 -r gameserver:7777 -l 600 -j 50
```
