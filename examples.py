#!/usr/bin/env python3
"""
Example usage of FakeLag for testing scenarios.

This script demonstrates how to use FakeLag for various network conditions.
"""

import subprocess
import sys
import time


def print_section(title):
    """Print a section header."""
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60 + "\n")


def example_basic():
    """Example: Basic latency simulation."""
    print_section("Example 1: Basic 100ms Latency")
    print("Command:")
    print("  python3 fakelag.py --local-port 7777 \\")
    print("                      --target-host gameserver.example.com \\")
    print("                      --target-port 7777 \\")
    print("                      --latency 100")
    print("\nThis will:")
    print("  - Listen on local port 7777")
    print("  - Forward to gameserver.example.com:7777")
    print("  - Add 100ms of latency to all traffic")


def example_jitter():
    """Example: Latency with jitter."""
    print_section("Example 2: Latency with Jitter")
    print("Command:")
    print("  python3 fakelag.py --local-port 7777 \\")
    print("                      --target-host gameserver.example.com \\")
    print("                      --target-port 7777 \\")
    print("                      --latency 100 \\")
    print("                      --jitter 20")
    print("\nThis will:")
    print("  - Add 100ms base latency")
    print("  - Add random jitter between -20ms and +20ms")
    print("  - Resulting latency: 80-120ms")


def example_packet_loss():
    """Example: Packet loss simulation."""
    print_section("Example 3: Packet Loss")
    print("Command:")
    print("  python3 fakelag.py --local-port 7777 \\")
    print("                      --target-host gameserver.example.com \\")
    print("                      --target-port 7777 \\")
    print("                      --latency 100 \\")
    print("                      --packet-loss 0.05")
    print("\nThis will:")
    print("  - Add 100ms latency")
    print("  - Drop 5% of packets randomly")


def example_poor_wifi():
    """Example: Simulate poor WiFi."""
    print_section("Example 4: Poor WiFi Simulation")
    print("Command:")
    print("  python3 fakelag.py --local-port 7777 \\")
    print("                      --target-host gameserver.example.com \\")
    print("                      --target-port 7777 \\")
    print("                      --latency 150 \\")
    print("                      --jitter 30 \\")
    print("                      --packet-loss 0.02")
    print("\nThis simulates:")
    print("  - Typical poor WiFi connection")
    print("  - 150ms base latency with ±30ms jitter (120-180ms)")
    print("  - 2% packet loss")


def example_mobile():
    """Example: Simulate mobile network."""
    print_section("Example 5: Mobile 4G Network")
    print("Command:")
    print("  python3 fakelag.py --local-port 7777 \\")
    print("                      --target-host gameserver.example.com \\")
    print("                      --target-port 7777 \\")
    print("                      --latency 80 \\")
    print("                      --jitter 15")
    print("\nThis simulates:")
    print("  - Typical 4G mobile connection")
    print("  - 80ms base latency with ±15ms jitter (65-95ms)")


def example_extreme():
    """Example: Extreme conditions."""
    print_section("Example 6: Extreme Conditions")
    print("Command:")
    print("  python3 fakelag.py --local-port 7777 \\")
    print("                      --target-host gameserver.example.com \\")
    print("                      --target-port 7777 \\")
    print("                      --latency 300 \\")
    print("                      --jitter 50 \\")
    print("                      --packet-loss 0.10")
    print("\nThis simulates:")
    print("  - Extreme network conditions")
    print("  - 300ms base latency with ±50ms jitter (250-350ms)")
    print("  - 10% packet loss")


def main():
    """Run all examples."""
    print("\n" + "="*60)
    print(" FakeLag Usage Examples")
    print("="*60)
    
    example_basic()
    example_jitter()
    example_packet_loss()
    example_poor_wifi()
    example_mobile()
    example_extreme()
    
    print("\n" + "="*60)
    print(" Common Use Cases")
    print("="*60 + "\n")
    
    print("1. Testing game netcode under various conditions")
    print("2. QA testing of multiplayer features")
    print("3. Debugging synchronization issues")
    print("4. Performance testing with realistic network conditions")
    print("5. Validating timeout and retry logic")
    
    print("\n" + "="*60)
    print(" Tips")
    print("="*60 + "\n")
    
    print("- Start with low latency (50-100ms) and gradually increase")
    print("- Test with jitter to simulate real-world conditions")
    print("- Use packet loss sparingly (1-5% is typical)")
    print("- Test both directions (client->server and server->client)")
    print("- Monitor your application's behavior with different settings")
    
    print("\n" + "="*60)
    print("\nFor more information, see README.md")
    print()


if __name__ == '__main__':
    main()
