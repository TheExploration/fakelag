#!/usr/bin/env python3
"""
Tests for fakelag network latency simulation tool.
"""

import unittest
import socket
import threading
import time
from fakelag import FakeLagProxy, LagConfig


class TestLagConfig(unittest.TestCase):
    """Test LagConfig dataclass."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = LagConfig()
        self.assertEqual(config.latency_ms, 0)
        self.assertEqual(config.jitter_ms, 0)
        self.assertEqual(config.packet_loss, 0.0)
    
    def test_custom_config(self):
        """Test custom configuration values."""
        config = LagConfig(latency_ms=100, jitter_ms=20, packet_loss=0.05)
        self.assertEqual(config.latency_ms, 100)
        self.assertEqual(config.jitter_ms, 20)
        self.assertEqual(config.packet_loss, 0.05)


class TestFakeLagProxy(unittest.TestCase):
    """Test FakeLagProxy functionality."""
    
    def test_should_drop_packet(self):
        """Test packet loss probability."""
        config = LagConfig(packet_loss=0.0)
        proxy = FakeLagProxy(9999, 'localhost', 10000, config)
        
        # With 0% loss, no packets should be dropped
        for _ in range(100):
            self.assertFalse(proxy._should_drop_packet())
        
        # With 100% loss, all packets should be dropped
        proxy.config.packet_loss = 1.0
        for _ in range(100):
            self.assertTrue(proxy._should_drop_packet())
        
        proxy.socket.close()
    
    def test_calculate_delay(self):
        """Test delay calculation."""
        # Test base delay without jitter
        config = LagConfig(latency_ms=100, jitter_ms=0)
        proxy = FakeLagProxy(9999, 'localhost', 10000, config)
        delay = proxy._calculate_delay()
        self.assertAlmostEqual(delay, 0.1, places=5)
        proxy.socket.close()
        
        # Test delay with jitter
        config = LagConfig(latency_ms=100, jitter_ms=20)
        proxy = FakeLagProxy(9999, 'localhost', 10000, config)
        
        # Delay should be in range [80ms, 120ms]
        for _ in range(50):
            delay = proxy._calculate_delay()
            self.assertGreaterEqual(delay, 0.08)
            self.assertLessEqual(delay, 0.12)
        proxy.socket.close()
    
    def test_proxy_initialization(self):
        """Test proxy initialization."""
        config = LagConfig(latency_ms=50, jitter_ms=10, packet_loss=0.01)
        proxy = FakeLagProxy(9998, 'localhost', 10000, config)
        
        self.assertEqual(proxy.local_port, 9998)
        self.assertEqual(proxy.target_host, 'localhost')
        self.assertEqual(proxy.target_port, 10000)
        self.assertEqual(proxy.config.latency_ms, 50)
        self.assertEqual(proxy.config.jitter_ms, 10)
        self.assertEqual(proxy.config.packet_loss, 0.01)
        self.assertFalse(proxy.running)
        proxy.socket.close()


class TestEndToEnd(unittest.TestCase):
    """End-to-end tests for the proxy."""
    
    def test_delay_calculation_consistency(self):
        """Test that delay calculations are consistent."""
        # Test that the delay calculation is working
        config = LagConfig(latency_ms=50, jitter_ms=10)
        proxy = FakeLagProxy(9997, '127.0.0.1', 10000, config)
        
        delays = [proxy._calculate_delay() for _ in range(100)]
        
        # All delays should be positive
        for delay in delays:
            self.assertGreaterEqual(delay, 0)
        
        # Average delay should be close to 50ms
        avg_delay = sum(delays) / len(delays)
        self.assertGreater(avg_delay, 0.04)  # 40ms
        self.assertLess(avg_delay, 0.06)     # 60ms
        
        proxy.socket.close()


if __name__ == '__main__':
    unittest.main()
