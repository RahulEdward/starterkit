"""
WebSocket Proxy for Best-Option
Handles real-time market data streaming from brokers to clients
"""

from .server import WebSocketProxy
from .base_adapter import BaseBrokerWebSocketAdapter

__all__ = ["WebSocketProxy", "BaseBrokerWebSocketAdapter"]
