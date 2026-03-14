"""
WebSocket Test Client for Best-Option
Tests live market data streaming
"""
import asyncio
import json
import websockets


async def test_websocket():
    """Test WebSocket connection and market data subscription"""
    uri = "ws://127.0.0.1:8765"
    
    print("=" * 60)
    print("Best-Option WebSocket Test Client")
    print("=" * 60)
    print()
    
    try:
        async with websockets.connect(uri) as websocket:
            print(f"✓ Connected to {uri}")
            print()
            
            # Step 1: Authenticate
            print("Step 1: Authenticating...")
            auth_message = {
                "action": "authenticate",
                "user_id": 1  # Replace with your user_id from database
            }
            await websocket.send(json.dumps(auth_message))
            response = await websocket.recv()
            print(f"Response: {response}")
            print()
            
            # Step 2: Subscribe to a symbol
            print("Step 2: Subscribing to RELIANCE-NSE...")
            subscribe_message = {
                "action": "subscribe",
                "symbol": "RELIANCE",
                "exchange": "NSE",
                "mode": "LTP"
            }
            await websocket.send(json.dumps(subscribe_message))
            response = await websocket.recv()
            print(f"Response: {response}")
            print()
            
            # Step 3: Listen for market data
            print("Step 3: Listening for market data (10 seconds)...")
            print("-" * 60)
            
            try:
                for i in range(10):
                    response = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                    data = json.loads(response)
                    print(f"[{i+1}] {json.dumps(data, indent=2)}")
            except asyncio.TimeoutError:
                print("No data received (timeout)")
            
            print("-" * 60)
            print()
            
            # Step 4: Unsubscribe
            print("Step 4: Unsubscribing...")
            unsubscribe_message = {
                "action": "unsubscribe",
                "symbol": "RELIANCE",
                "exchange": "NSE",
                "mode": "LTP"
            }
            await websocket.send(json.dumps(unsubscribe_message))
            response = await websocket.recv()
            print(f"Response: {response}")
            print()
            
            print("✓ Test completed successfully!")
            
    except websockets.exceptions.ConnectionRefused:
        print("✗ Connection refused. Is the WebSocket server running?")
        print()
        print("To start the WebSocket server:")
        print("  python -m websocket_proxy.server")
    except Exception as e:
        print(f"✗ Error: {e}")


if __name__ == "__main__":
    print()
    asyncio.run(test_websocket())
    print()
