"""
Run WebSocket Proxy Server for Best-Option
Handles real-time market data streaming
"""
import asyncio
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from websocket_proxy.server import WebSocketProxy
from utils.logging import get_logger

logger = get_logger("websocket_server")


async def main():
    """Main entry point for WebSocket server"""
    print("=" * 60)
    print("Best-Option WebSocket Proxy Server")
    print("=" * 60)
    print()
    
    # Configuration
    host = os.getenv("WEBSOCKET_HOST", "127.0.0.1")
    port = int(os.getenv("WEBSOCKET_PORT", "8765"))
    
    print(f"Host: {host}")
    print(f"Port: {port}")
    print()
    print("Starting server...")
    print()
    
    # Create and start proxy
    proxy = WebSocketProxy(host=host, port=port)
    
    try:
        await proxy.start()
    except KeyboardInterrupt:
        print()
        print("Shutting down...")
        await proxy.stop()
        print("Server stopped")
    except Exception as e:
        logger.exception(f"Server error: {e}")
        await proxy.stop()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nServer stopped by user")
