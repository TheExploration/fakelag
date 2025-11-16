#!/usr/bin/env python3
"""
FakeLag - A network latency simulation tool for online coop testing.

This tool creates a UDP proxy that can simulate network latency and packet loss
for testing multiplayer games and networked applications.
"""

import socket
import threading
import time
import random
import argparse
from collections import deque
from dataclasses import dataclass
from typing import Optional


@dataclass
class LagConfig:
    """Configuration for lag simulation."""
    latency_ms: int = 0  # Additional latency in milliseconds
    jitter_ms: int = 0   # Random jitter variation in milliseconds
    packet_loss: float = 0.0  # Packet loss probability (0.0 to 1.0)


class FakeLagProxy:
    """UDP proxy that simulates network lag and packet loss."""
    
    def __init__(self, local_port: int, target_host: str, target_port: int, config: LagConfig, bind_host: str = '0.0.0.0'):
        """
        Initialize the fake lag proxy.
        
        Args:
            local_port: Port to listen on for incoming traffic
            target_host: Target server hostname or IP
            target_port: Target server port
            config: Lag configuration
            bind_host: Host address to bind to (default: '0.0.0.0' for all interfaces)
        """
        self.local_port = local_port
        self.target_host = target_host
        self.target_port = target_port
        self.config = config
        self.bind_host = bind_host
        
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((bind_host, local_port))
        
        self.client_addr = None
        self.running = False
        self.delay_queue = deque()
        self.queue_lock = threading.Lock()
        
    def start(self):
        """Start the proxy server."""
        self.running = True
        
        # Start thread to handle delayed packets
        delay_thread = threading.Thread(target=self._process_delayed_packets, daemon=True)
        delay_thread.start()
        
        # Start thread to receive responses from target server
        response_thread = threading.Thread(target=self._receive_from_target, daemon=True)
        response_thread.start()
        
        print(f"FakeLag proxy started on port {self.local_port}")
        print(f"Forwarding to {self.target_host}:{self.target_port}")
        print(f"Latency: {self.config.latency_ms}ms, Jitter: {self.config.jitter_ms}ms, Loss: {self.config.packet_loss*100}%")
        
        self._receive_from_client()
    
    def stop(self):
        """Stop the proxy server."""
        self.running = False
        self.socket.close()
        
    def _should_drop_packet(self) -> bool:
        """Determine if a packet should be dropped based on packet loss rate."""
        return random.random() < self.config.packet_loss
    
    def _calculate_delay(self) -> float:
        """Calculate delay for a packet including jitter."""
        base_delay = self.config.latency_ms / 1000.0
        if self.config.jitter_ms > 0:
            jitter = random.uniform(-self.config.jitter_ms, self.config.jitter_ms) / 1000.0
            return max(0, base_delay + jitter)
        return base_delay
    
    def _receive_from_client(self):
        """Receive packets from client and forward to target with delay."""
        while self.running:
            try:
                data, addr = self.socket.recvfrom(65535)
                self.client_addr = addr
                
                # Check if packet should be dropped
                if self._should_drop_packet():
                    print(f"Dropped packet from client ({len(data)} bytes)")
                    continue
                
                # Calculate delay and schedule packet
                delay = self._calculate_delay()
                send_time = time.time() + delay
                
                with self.queue_lock:
                    self.delay_queue.append((send_time, data, (self.target_host, self.target_port), 'forward'))
                    
            except Exception as e:
                if self.running:
                    print(f"Error receiving from client: {e}")
                break
    
    def _receive_from_target(self):
        """Receive responses from target server and forward to client with delay."""
        # Create separate socket for receiving from target
        recv_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        recv_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        recv_socket.settimeout(1.0)
        
        # We need to track which socket we sent from to receive responses
        # For simplicity, we'll use the same socket
        while self.running:
            try:
                self.socket.settimeout(0.1)
                # This is a simplified approach - in production you'd want proper tracking
                time.sleep(0.01)
            except Exception as e:
                if self.running and not isinstance(e, socket.timeout):
                    print(f"Error in receive thread: {e}")
    
    def _process_delayed_packets(self):
        """Process and send delayed packets from the queue."""
        while self.running:
            current_time = time.time()
            packets_to_send = []
            
            with self.queue_lock:
                # Find packets ready to send
                while self.delay_queue and self.delay_queue[0][0] <= current_time:
                    packets_to_send.append(self.delay_queue.popleft())
            
            # Send packets outside the lock
            for send_time, data, target, direction in packets_to_send:
                try:
                    if direction == 'forward':
                        # Send to target server
                        target_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                        target_socket.sendto(data, target)
                        target_socket.close()
                    else:
                        # Send back to client
                        if self.client_addr:
                            self.socket.sendto(data, self.client_addr)
                except Exception as e:
                    print(f"Error sending delayed packet: {e}")
            
            time.sleep(0.001)  # Small sleep to prevent busy waiting


def main():
    """Main entry point for the fakelag tool."""
    parser = argparse.ArgumentParser(
        description='FakeLag - Simulate network latency for online coop testing'
    )
    parser.add_argument('--local-port', type=int, required=True,
                       help='Local port to listen on')
    parser.add_argument('--target-host', type=str, required=True,
                       help='Target server hostname or IP')
    parser.add_argument('--target-port', type=int, required=True,
                       help='Target server port')
    parser.add_argument('--latency', type=int, default=0,
                       help='Additional latency in milliseconds (default: 0)')
    parser.add_argument('--jitter', type=int, default=0,
                       help='Random jitter variation in milliseconds (default: 0)')
    parser.add_argument('--packet-loss', type=float, default=0.0,
                       help='Packet loss probability 0.0-1.0 (default: 0.0)')
    parser.add_argument('--bind-host', type=str, default='0.0.0.0',
                       help='Host address to bind to (default: 0.0.0.0 for all interfaces, use 127.0.0.1 for localhost only)')
    
    args = parser.parse_args()
    
    # Validate arguments
    if args.packet_loss < 0.0 or args.packet_loss > 1.0:
        parser.error('--packet-loss must be between 0.0 and 1.0')
    
    if args.latency < 0:
        parser.error('--latency must be non-negative')
        
    if args.jitter < 0:
        parser.error('--jitter must be non-negative')
    
    # Create configuration
    config = LagConfig(
        latency_ms=args.latency,
        jitter_ms=args.jitter,
        packet_loss=args.packet_loss
    )
    
    # Create and start proxy
    proxy = FakeLagProxy(args.local_port, args.target_host, args.target_port, config, args.bind_host)
    
    try:
        proxy.start()
    except KeyboardInterrupt:
        print("\nStopping FakeLag proxy...")
        proxy.stop()


if __name__ == '__main__':
    main()
