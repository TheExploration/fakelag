#!/usr/bin/env python3
"""
Example: Testing a simple UDP echo service with FakeLag

This example demonstrates how to:
1. Run a simple echo server
2. Test it through FakeLag with different network conditions
"""

import socket
import time
import sys


def run_echo_client(server_host, server_port, num_messages=5):
    """Send test messages to an echo server and measure round-trip times"""
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(3.0)
    
    print(f"\nConnecting to {server_host}:{server_port}")
    print(f"Sending {num_messages} test messages...\n")
    
    rtts = []
    successful = 0
    
    for i in range(num_messages):
        message = f"Message {i+1} - {time.time()}".encode()
        
        try:
            # Send message and measure round-trip time
            start_time = time.time()
            sock.sendto(message, (server_host, server_port))
            
            response, _ = sock.recvfrom(4096)
            end_time = time.time()
            
            rtt_ms = (end_time - start_time) * 1000
            rtts.append(rtt_ms)
            successful += 1
            
            print(f"Message {i+1}: RTT = {rtt_ms:.2f}ms ✓")
            
        except socket.timeout:
            print(f"Message {i+1}: Timeout ✗ (packet lost)")
        except Exception as e:
            print(f"Message {i+1}: Error - {e}")
        
        time.sleep(0.2)  # Small delay between messages
    
    sock.close()
    
    # Print statistics
    print("\n" + "="*50)
    print("Statistics:")
    print(f"  Messages sent: {num_messages}")
    print(f"  Successful: {successful} ({successful*100/num_messages:.1f}%)")
    print(f"  Lost: {num_messages - successful} ({(num_messages-successful)*100/num_messages:.1f}%)")
    
    if rtts:
        print(f"  Average RTT: {sum(rtts)/len(rtts):.2f}ms")
        print(f"  Min RTT: {min(rtts):.2f}ms")
        print(f"  Max RTT: {max(rtts):.2f}ms")
    
    print("="*50)


def main():
    """Main example function"""
    
    if len(sys.argv) < 2:
        print("Usage: python3 echo_test.py <server:port>")
        print("\nExample workflow:")
        print("  1. Terminal 1 - Start echo server:")
        print("     nc -u -l 7777")
        print()
        print("  2. Terminal 2 - Start FakeLag proxy:")
        print("     python3 ../fakelag.py -p 7778 -r localhost:7777 -l 100 -j 20 -d 5")
        print()
        print("  3. Terminal 3 - Run this test client:")
        print("     python3 echo_test.py localhost:7778")
        sys.exit(1)
    
    # Parse server address
    try:
        server_str = sys.argv[1]
        host, port = server_str.rsplit(':', 1)
        port = int(port)
    except ValueError:
        print("Error: Server must be in format 'host:port'")
        sys.exit(1)
    
    run_echo_client(host, port)


if __name__ == '__main__':
    main()
