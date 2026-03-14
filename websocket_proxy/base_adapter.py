"""
Base WebSocket Adapter for Broker Integration
"""
import json
import os
import random
import socket
import threading
from abc import ABC, abstractmethod

import zmq

from utils.logging import get_logger

logger = get_logger(__name__)

# Configuration
MAX_SYMBOLS_PER_WEBSOCKET = int(os.getenv("MAX_SYMBOLS_PER_WEBSOCKET", "1000"))
MAX_WEBSOCKET_CONNECTIONS = int(os.getenv("MAX_WEBSOCKET_CONNECTIONS", "3"))


def is_port_available(port):
    """Check if a port is available for use"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.settimeout(1.0)
            s.bind(("127.0.0.1", port))
            return True
    except OSError:
        return False


def find_free_zmq_port(start_port=5556, max_attempts=50):
    """Find an available port starting from start_port"""
    for _ in range(max_attempts):
        if is_port_available(start_port):
            return start_port
        start_port = min(start_port + 1, 65000)
    return None


class BaseBrokerWebSocketAdapter(ABC):
    """
    Base class for all broker-specific WebSocket adapters
    """

    # Class variables to track bound ports
    _bound_ports = set()
    _port_lock = threading.Lock()
    _shared_context = None
    _context_lock = threading.Lock()

    def __init__(self):
        """Initialize the base broker adapter"""
        self.logger = get_logger("broker_adapter")
        self.logger.info("BaseBrokerWebSocketAdapter initializing")

        try:
            # Initialize ZeroMQ context and socket
            self._initialize_shared_context()
            self.socket = self._create_socket()
            self.zmq_port = self._bind_to_available_port()
            os.environ["ZMQ_PORT"] = str(self.zmq_port)
            self.logger.info(f"BaseBrokerWebSocketAdapter initialized on port {self.zmq_port}")

            # Initialize instance variables
            self.subscriptions = {}
            self.connected = False

        except Exception as e:
            self.logger.exception(f"Error in BaseBrokerWebSocketAdapter init: {e}")
            raise

    def _initialize_shared_context(self):
        """Initialize shared ZeroMQ context if not already created"""
        with self._context_lock:
            if not BaseBrokerWebSocketAdapter._shared_context:
                self.logger.info("Creating shared ZMQ context")
                BaseBrokerWebSocketAdapter._shared_context = zmq.Context()
        self.context = BaseBrokerWebSocketAdapter._shared_context

    def _create_socket(self):
        """Create and configure ZeroMQ socket"""
        with self._context_lock:
            socket = self.context.socket(zmq.PUB)
            socket.setsockopt(zmq.LINGER, 1000)
            socket.setsockopt(zmq.SNDHWM, 1000)
            return socket

    def _bind_to_available_port(self):
        """Find an available port and bind the socket to it"""
        with self._port_lock:
            # Try default port first
            default_port = int(os.getenv("ZMQ_PORT", "5555"))

            if default_port not in self._bound_ports and is_port_available(default_port):
                try:
                    self.socket.bind(f"tcp://*:{default_port}")
                    self._bound_ports.add(default_port)
                    self.logger.info(f"Bound to default port {default_port}")
                    return default_port
                except zmq.ZMQError as e:
                    self.logger.warning(f"Failed to bind to default port {default_port}: {e}")

            # Find random available port
            for attempt in range(5):
                port = find_free_zmq_port(start_port=5556 + random.randint(0, 1000))
                if not port:
                    continue

                try:
                    self.socket.bind(f"tcp://*:{port}")
                    self._bound_ports.add(port)
                    self.logger.info(f"Successfully bound to port {port}")
                    return port
                except zmq.ZMQError as e:
                    self.logger.warning(f"Failed to bind to port {port}: {e}")
                    continue

            raise RuntimeError("Could not bind to any available ZMQ port")

    @abstractmethod
    def initialize(self, broker_name, user_id, auth_data=None):
        """Initialize connection with broker WebSocket API"""
        pass

    @abstractmethod
    def subscribe(self, symbol, exchange, mode=2):
        """Subscribe to market data"""
        pass

    @abstractmethod
    def unsubscribe(self, symbol, exchange, mode=2):
        """Unsubscribe from market data"""
        pass

    @abstractmethod
    def connect(self):
        """Establish connection to the broker's WebSocket"""
        pass

    @abstractmethod
    def disconnect(self):
        """Disconnect from the broker's WebSocket"""
        pass

    def cleanup_zmq(self):
        """Properly clean up ZeroMQ resources"""
        try:
            if hasattr(self, "zmq_port") and self.zmq_port:
                with self._port_lock:
                    self._bound_ports.discard(self.zmq_port)
                    self.logger.info(f"Released port {self.zmq_port}")

            if hasattr(self, "socket") and self.socket:
                self.socket.close(linger=0)
                self.socket = None
                self.logger.info("ZeroMQ socket closed")

        except Exception as e:
            self.logger.exception(f"Error cleaning up ZeroMQ resources: {e}")

    def __del__(self):
        """Destructor to ensure ZeroMQ resources are properly cleaned up"""
        try:
            self.cleanup_zmq()
        except Exception:
            pass

    def publish_market_data(self, topic, data):
        """Publish market data to ZeroMQ subscribers"""
        try:
            if self.socket:
                self.socket.send_multipart(
                    [topic.encode("utf-8"), json.dumps(data).encode("utf-8")]
                )
        except Exception as e:
            self.logger.exception(f"Error publishing market data: {e}")

    def _create_success_response(self, message, **kwargs):
        """Create a standard success response"""
        response = {"status": "success", "message": message}
        response.update(kwargs)
        return response

    def _create_error_response(self, code, message):
        """Create a standard error response"""
        return {"status": "error", "code": code, "message": message}
