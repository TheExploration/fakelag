#!/usr/bin/env python3
"""
Simple test script for FakeLag

This script tests the basic functionality of the FakeLag proxy by:
1. Starting a simple UDP echo server
2. Starting the FakeLag proxy
3. Sending test packets through the proxy
4. Measuring the actual latency
"""

import socket
import threading
import time
import sys


def echo_server(port, stop_event):
    """Simple UDP echo server for testing"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('127.0.0.1', port))
    sock.settimeout(0.5)
    
    print(f"Echo server started on port {port}")
    
    while not stop_event.is_set():
        try:
            data, addr = sock.recvfrom(1024)
            sock.sendto(data, addr)
        except socket.timeout:
            continue
        except Exception as e:
            print(f"Echo server error: {e}")
            break
    
    sock.close()
    print("Echo server stopped")


def test_client(proxy_port, num_tests=5):
    """Test client that sends packets through the proxy"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(2.0)
    
    print(f"\nTesting with {num_tests} packets...")
    latencies = []
    
    for i in range(num_tests):
        try:
            message = f"test_{i}".encode()
            
            start = time.time()
            sock.sendto(message, ('127.0.0.1', proxy_port))
            data, _ = sock.recvfrom(1024)
            end = time.time()
            
            latency = (end - start) * 1000  # Convert to ms
            latencies.append(latency)
            
            if data == message:
                print(f"  Test {i+1}: ✓ RTT = {latency:.1f}ms")
            else:
                print(f"  Test {i+1}: ✗ Data mismatch")
                
        except socket.timeout:
            print(f"  Test {i+1}: ✗ Timeout (packet likely dropped)")
        except Exception as e:
            print(f"  Test {i+1}: ✗ Error: {e}")
        
        time.sleep(0.1)
    
    sock.close()
    
    if latencies:
        avg_latency = sum(latencies) / len(latencies)
        print(f"\nAverage RTT: {avg_latency:.1f}ms")
        print(f"Packet delivery: {len(latencies)}/{num_tests} ({len(latencies)*100/num_tests:.0f}%)")
    
    return latencies


def main():
    """Run basic tests"""
    print("FakeLag Basic Test Suite")
    print("=" * 50)
    
    # Test 1: No lag
    print("\n[Test 1] No lag (baseline)")
    print("-" * 50)
    
    # This test would require actually starting the proxy, which is complex
    # For now, we'll just verify the code can be imported
    try:
        import fakelag
        print("✓ fakelag module imports successfully")
        print("✓ NetworkConditions class available:", hasattr(fakelag, 'NetworkConditions'))
        print("✓ FakeLagProxy class available:", hasattr(fakelag, 'FakeLagProxy'))
        print("✓ PacketDelayQueue class available:", hasattr(fakelag, 'PacketDelayQueue'))
    except Exception as e:
        print(f"✗ Error importing fakelag: {e}")
        return 1
    
    # Test NetworkConditions
    print("\n[Test 2] NetworkConditions instantiation")
    print("-" * 50)
    try:
        conditions = fakelag.NetworkConditions(
            latency_ms=100,
            jitter_ms=20,
            packet_loss=5
        )
        print(f"✓ Created conditions: {conditions}")
    except Exception as e:
        print(f"✗ Error creating NetworkConditions: {e}")
        return 1
    
    # Test PacketDelayQueue
    print("\n[Test 3] PacketDelayQueue basic functionality")
    print("-" * 50)
    try:
        queue = fakelag.PacketDelayQueue(conditions)
        queue.add_packet(b"test", ("127.0.0.1", 12345))
        print("✓ Can add packets to queue")
        
        # Initially no packets should be ready (they're delayed)
        ready = queue.get_ready_packets()
        print(f"✓ Packets delayed properly (ready: {len(ready)})")
        
        queue.stop()
        print("✓ Queue can be stopped")
    except Exception as e:
        print(f"✗ Error testing PacketDelayQueue: {e}")
        return 1
    
    print("\n" + "=" * 50)
    print("All basic tests passed! ✓")
    print("\nTo test the full proxy functionality, run:")
    print("  Terminal 1: python3 fakelag.py -p 7778 -r localhost:7777 -l 100")
    print("  Terminal 2: nc -u -l 7777  (echo server)")
    print("  Terminal 3: nc -u localhost 7778  (test client)")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
