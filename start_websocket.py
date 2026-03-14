"""
Start WebSocket Proxy Server for Best-Option
Run this to enable real-time market data streaming
"""
import asyncio
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from websocket_proxy.server import WebSocketProxy
from utils.logging import get_logger

logger = get_logger(__name__)


async def main():
    """Start the WebSocket proxy server"""
    logger.info("=" * 60)
    logger.info("Best-Option WebSocket Proxy Server")
    logger.info("=" * 60)
    
    # Create and start the proxy
    proxy = WebSocketProxy(host="127.0.0.1", port=8765)
    
    try:
        logger.info("Starting WebSocket proxy...")
        await proxy.start()
    except KeyboardInterrupt:
        logger.info("\nShutting down...")
        await proxy.stop()
    except Exception as e:
        logger.exception(f"Fatal error: {e}")
        await proxy.stop()
        sys.exit(1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nShutdown complete")
