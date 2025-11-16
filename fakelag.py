#!/usr/bin/env python3
"""
FakeLag - Network lag simulator for online coop testing

This tool simulates network conditions like latency, packet loss, and jitter
to test online cooperative games under various network conditions.
"""

import socket
import time
import threading
import random
import argparse
import sys
from collections import deque
from dataclasses import dataclass
from typing import Optional


@dataclass
class NetworkConditions:
    """Configuration for network simulation parameters"""
    latency_ms: float = 0  # Base latency in milliseconds
    jitter_ms: float = 0   # Variance in latency (±jitter_ms)
    packet_loss: float = 0  # Packet loss percentage (0-100)


class PacketDelayQueue:
    """Queue that delays packets based on network conditions"""
    
    def __init__(self, conditions: NetworkConditions):
        self.conditions = conditions
        self.queue = deque()
        self.lock = threading.Lock()
        self.running = True
        
    def add_packet(self, data: bytes, destination: tuple):
        """Add a packet to the delay queue"""
        # Simulate packet loss
        if random.random() * 100 < self.conditions.packet_loss:
            return  # Drop the packet
            
        # Calculate delay with jitter
        delay = self.conditions.latency_ms / 1000.0
        if self.conditions.jitter_ms > 0:
            jitter = random.uniform(-self.conditions.jitter_ms, self.conditions.jitter_ms) / 1000.0
            delay = max(0, delay + jitter)
            
        send_time = time.time() + delay
        
        with self.lock:
            self.queue.append((send_time, data, destination))
    
    def get_ready_packets(self):
        """Get all packets that are ready to be sent"""
        ready = []
        current_time = time.time()
        
        with self.lock:
            while self.queue and self.queue[0][0] <= current_time:
                _, data, destination = self.queue.popleft()
                ready.append((data, destination))
                
        return ready
    
    def stop(self):
        """Stop the delay queue"""
        self.running = False


class FakeLagProxy:
    """Network proxy that simulates lag conditions"""
    
    def __init__(self, local_port: int, remote_host: str, remote_port: int, 
                 conditions: NetworkConditions):
        self.local_port = local_port
        self.remote_host = remote_host
        self.remote_port = remote_port
        self.conditions = conditions
        self.running = False
        
        # Create delay queues for both directions
        self.client_to_server_queue = PacketDelayQueue(conditions)
        self.server_to_client_queue = PacketDelayQueue(conditions)
        
        # Track client sessions (map from local client address to unique session ID)
        self.client_sessions = {}
        self.session_counter = 0
        self.sessions_lock = threading.Lock()
        
    def start(self):
        """Start the proxy server"""
        self.running = True
        
        # Create listening socket for clients
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind(('0.0.0.0', self.local_port))
        self.server_socket.settimeout(0.1)
        
        # Create socket for communication with remote server
        self.remote_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.remote_socket.settimeout(0.1)
        # Bind to a local port so we can receive responses
        self.remote_socket.bind(('0.0.0.0', 0))
        
        print(f"FakeLag proxy started on port {self.local_port}")
        print(f"Forwarding to {self.remote_host}:{self.remote_port}")
        print(f"Conditions: {self.conditions.latency_ms}ms latency, "
              f"{self.conditions.jitter_ms}ms jitter, {self.conditions.packet_loss}% loss")
        
        # Start background threads
        threading.Thread(target=self._receive_from_clients, daemon=True).start()
        threading.Thread(target=self._receive_from_server, daemon=True).start()
        threading.Thread(target=self._process_client_to_server, daemon=True).start()
        threading.Thread(target=self._process_server_to_client, daemon=True).start()
        
        # Keep main thread alive
        try:
            while self.running:
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("\nShutting down...")
        finally:
            self.stop()
    
    def _get_or_create_session(self, client_addr):
        """Get or create a session ID for a client address"""
        with self.sessions_lock:
            if client_addr not in self.client_sessions:
                self.session_counter += 1
                self.client_sessions[client_addr] = self.session_counter
            return self.client_sessions[client_addr]
    
    def _get_client_by_session(self, session_id):
        """Get client address by session ID"""
        with self.sessions_lock:
            for client_addr, sid in self.client_sessions.items():
                if sid == session_id:
                    return client_addr
        return None
    
    def _receive_from_clients(self):
        """Receive packets from clients"""
        while self.running:
            try:
                data, client_addr = self.server_socket.recvfrom(65535)
                session_id = self._get_or_create_session(client_addr)
                
                # Add packet to delay queue with session info
                # Destination includes session ID for routing responses back
                self.client_to_server_queue.add_packet(
                    data, (self.remote_host, self.remote_port, session_id)
                )
                
            except socket.timeout:
                continue
            except Exception as e:
                if self.running:
                    print(f"Error receiving from client: {e}")
    
    def _receive_from_server(self):
        """Receive packets from the remote server"""
        # We need to track which client each request came from
        # Since UDP is connectionless, we'll use a simple approach:
        # Assume the most recent client to send a packet is the one receiving responses
        while self.running:
            try:
                data, _ = self.remote_socket.recvfrom(65535)
                
                # Get the most recent session (this is a simplification)
                # In a real proxy, you'd need more sophisticated session tracking
                if self.client_sessions:
                    # Get the last client that sent something
                    # This works for simple request-response patterns
                    last_client = list(self.client_sessions.keys())[-1]
                    self.server_to_client_queue.add_packet(data, last_client)
                
            except socket.timeout:
                continue
            except Exception as e:
                if self.running:
                    print(f"Error receiving from server: {e}")
    
    def _process_client_to_server(self):
        """Process packets from client to server"""
        while self.running:
            for data, destination_info in self.client_to_server_queue.get_ready_packets():
                try:
                    remote_host, remote_port, _session_id = destination_info
                    self.remote_socket.sendto(data, (remote_host, remote_port))
                except Exception as e:
                    print(f"Error sending to server: {e}")
            
            time.sleep(0.001)
    
    def _process_server_to_client(self):
        """Process packets from server to client"""
        while self.running:
            for data, client_addr in self.server_to_client_queue.get_ready_packets():
                try:
                    self.server_socket.sendto(data, client_addr)
                except Exception as e:
                    print(f"Error sending to client: {e}")
            
            time.sleep(0.001)
    
    def stop(self):
        """Stop the proxy server"""
        self.running = False
        self.client_to_server_queue.stop()
        self.server_to_client_queue.stop()
        if hasattr(self, 'server_socket'):
            self.server_socket.close()
        if hasattr(self, 'remote_socket'):
            self.remote_socket.close()


def main():
    """Main entry point for the fakelag tool"""
    parser = argparse.ArgumentParser(
        description='FakeLag - Network lag simulator for online coop testing',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument(
        '-p', '--port',
        type=int,
        required=True,
        help='Local port to listen on'
    )
    
    parser.add_argument(
        '-r', '--remote',
        type=str,
        required=True,
        help='Remote host to forward to (host:port)'
    )
    
    parser.add_argument(
        '-l', '--latency',
        type=float,
        default=0,
        help='Base latency in milliseconds'
    )
    
    parser.add_argument(
        '-j', '--jitter',
        type=float,
        default=0,
        help='Latency variance (jitter) in milliseconds'
    )
    
    parser.add_argument(
        '-d', '--drop',
        type=float,
        default=0,
        help='Packet loss percentage (0-100)'
    )
    
    args = parser.parse_args()
    
    # Parse remote host:port
    try:
        remote_host, remote_port = args.remote.rsplit(':', 1)
        remote_port = int(remote_port)
    except ValueError:
        print("Error: Remote must be in format 'host:port'")
        sys.exit(1)
    
    # Validate parameters
    if args.latency < 0:
        print("Error: Latency must be non-negative")
        sys.exit(1)
    
    if args.jitter < 0:
        print("Error: Jitter must be non-negative")
        sys.exit(1)
    
    if not 0 <= args.drop <= 100:
        print("Error: Packet loss must be between 0 and 100")
        sys.exit(1)
    
    # Create network conditions
    conditions = NetworkConditions(
        latency_ms=args.latency,
        jitter_ms=args.jitter,
        packet_loss=args.drop
    )
    
    # Start proxy
    proxy = FakeLagProxy(
        local_port=args.port,
        remote_host=remote_host,
        remote_port=remote_port,
        conditions=conditions
    )
    
    proxy.start()


if __name__ == '__main__':
    main()
