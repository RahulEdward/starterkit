"""
Mock Broker Adapter for Testing WebSocket Proxy
Simulates live market data without actual broker connection
"""
import asyncio
import json
import random
import time

import zmq
import zmq.asyncio

from utils.logging import get_logger

logger = get_logger("mock_broker")


class MockBrokerAdapter:
    """Mock broker adapter that generates fake market data"""
    
    def __init__(self):
        """Initialize mock broker adapter"""
        self.context = zmq.asyncio.Context()
        self.socket = self.context.socket(zmq.PUB)
        self.socket.bind("tcp://*:5555")
        self.running = False
        
        # Simulated symbols with base prices
        self.symbols = {
            ("RELIANCE", "NSE"): 2450.50,
            ("TCS", "NSE"): 3650.75,
            ("INFY", "NSE"): 1450.25,
            ("HDFCBANK", "NSE"): 1650.00,
            ("SBIN", "NSE"): 625.50,
            ("NIFTY", "NSE_INDEX"): 21850.00,
            ("BANKNIFTY", "NSE_INDEX"): 46500.00,
        }
        
        logger.info("Mock broker adapter initialized")
    
    async def start(self):
        """Start generating mock market data"""
        self.running = True
        logger.info("Mock broker adapter started")
        
        print("=" * 60)
        print("Mock Broker Adapter - Generating Market Data")
        print("=" * 60)
        print()
        print("Publishing data for:")
        for (symbol, exchange), price in self.symbols.items():
            print(f"  - {symbol} ({exchange}): ₹{price}")
        print()
        print("Press Ctrl+C to stop")
        print("-" * 60)
        
        try:
            while self.running:
                # Generate data for each symbol
                for (symbol, exchange), base_price in self.symbols.items():
                    # Simulate price movement (+/- 0.5%)
                    change_pct = random.uniform(-0.005, 0.005)
                    ltp = round(base_price * (1 + change_pct), 2)
                    
                    # Create market data
                    market_data = {
                        "symbol": symbol,
                        "exchange": exchange,
                        "ltp": ltp,
                        "change": round(ltp - base_price, 2),
                        "change_pct": round(change_pct * 100, 2),
                        "volume": random.randint(100000, 1000000),
                        "timestamp": int(time.time() * 1000)
                    }
                    
                    # Publish to ZeroMQ
                    # Topic format: SYMBOL_EXCHANGE_MODE
                    topic = f"{symbol}_{exchange}_LTP"
                    await self.socket.send_multipart([
                        topic.encode("utf-8"),
                        json.dumps(market_data).encode("utf-8")
                    ])
                    
                    print(f"[{time.strftime('%H:%M:%S')}] {symbol}: ₹{ltp} ({market_data['change_pct']:+.2f}%)")
                
                # Wait before next update
                await asyncio.sleep(1)
                
        except KeyboardInterrupt:
            print()
            print("Stopping mock broker adapter...")
        finally:
            await self.stop()
    
    async def stop(self):
        """Stop the mock broker adapter"""
        self.running = False
        if self.socket:
            self.socket.close()
        if self.context:
            self.context.term()
        logger.info("Mock broker adapter stopped")


async def main():
    """Main entry point"""
    adapter = MockBrokerAdapter()
    try:
        await adapter.start()
    except KeyboardInterrupt:
        print("\nStopped by user")


if __name__ == "__main__":
    asyncio.run(main())
