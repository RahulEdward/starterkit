# WebSocket Market Data Testing Guide

## Architecture Overview

Best-Option uses a **common WebSocket proxy** that works with any broker:

```
Client (Browser) <--WebSocket--> WebSocket Proxy <--ZeroMQ--> Broker Adapter <--API--> Broker
```

- **Client**: Uses Best-Option universal symbol format (e.g., "SBIN", "NIFTY")
- **WebSocket Proxy**: Converts symbols and routes data
- **Broker Adapter**: Connects to broker's WebSocket API
- **ZeroMQ**: High-performance message queue for internal communication

## Quick Start

### 1. Start Backend (if not running)
```bash
python app.py
```

### 2. Start WebSocket Proxy Server
```bash
python start_websocket.py
```

You should see:
```
============================================================
Best-Option WebSocket Proxy Server
============================================================
Starting WebSocket proxy...
ZeroMQ listener started
WebSocket server started on 127.0.0.1:8765
```

### 3. Open Test Page
Open `test_websocket.html` in your browser (double-click or drag to browser)

### 4. Test Connection

1. **Enter User ID**: Use `1` (or your user ID from database)
2. **Click "Connect"**: Should show "Connected - User 1 (fyers)"
3. **Enter Symbol**: Try "SBIN" (State Bank of India)
4. **Select Exchange**: NSE
5. **Select Mode**: LTP (Last Traded Price)
6. **Click "Subscribe"**: Should show subscription confirmation

## Testing Scenarios

### Test 1: Basic Connection
- Connect with User ID
- Check authentication message in log
- Status should show "Connected"

### Test 2: Subscribe to Single Symbol
- Subscribe to "SBIN" on NSE
- Should see subscription confirmation
- Live data will appear when broker adapter is running

### Test 3: Multiple Subscriptions
- Subscribe to multiple symbols:
  - SBIN (NSE)
  - RELIANCE (NSE)
  - NIFTY (NSE_INDEX)
- Each should show in separate ticker card

### Test 4: Unsubscribe
- Unsubscribe from a symbol
- Ticker card should disappear

## Message Format

### Client → Server

**Authenticate:**
```json
{
  "action": "authenticate",
  "user_id": 1
}
```

**Subscribe:**
```json
{
  "action": "subscribe",
  "symbol": "SBIN",
  "exchange": "NSE",
  "mode": "LTP"
}
```

**Unsubscribe:**
```json
{
  "action": "unsubscribe",
  "symbol": "SBIN",
  "exchange": "NSE",
  "mode": "LTP"
}
```

### Server → Client

**Authenticated:**
```json
{
  "type": "authenticated",
  "status": "success",
  "user_id": 1,
  "broker": "fyers"
}
```

**Subscribed:**
```json
{
  "type": "subscribed",
  "status": "success",
  "symbol": "SBIN",
  "exchange": "NSE",
  "mode": "LTP"
}
```

**Market Data:**
```json
{
  "symbol": "SBIN",
  "exchange": "NSE",
  "ltp": 625.50,
  "change": 1.25,
  "volume": 1234567,
  "timestamp": "2024-03-14T10:30:00"
}
```

## Next Steps: Broker Adapter Integration

To get live market data, you need to:

1. **Create Broker Adapter** (Fyers or AngelOne)
2. **Connect to Broker's WebSocket API**
3. **Publish data to ZeroMQ** (port 5555)
4. **WebSocket Proxy will route to clients**

Example broker adapter structure:
```python
from websocket_proxy.base_adapter import BaseBrokerWebSocketAdapter

class FyersWebSocketAdapter(BaseBrokerWebSocketAdapter):
    async def connect_to_broker(self):
        # Connect to Fyers WebSocket
        pass
    
    async def subscribe_symbols(self, symbols):
        # Subscribe to symbols on Fyers
        pass
    
    async def handle_broker_message(self, message):
        # Convert Fyers format to Best-Option format
        # Publish to ZeroMQ
        pass
```

## Troubleshooting

### WebSocket won't connect
- Check if `start_websocket.py` is running
- Check port 8765 is not in use
- Check firewall settings

### Authentication fails
- Verify User ID exists in database
- Check backend logs for errors

### No market data
- Broker adapter not running yet (this is expected)
- Check ZeroMQ connection (port 5555)
- Check broker adapter logs

## Architecture Benefits

✅ **Broker Agnostic**: Same client code works with any broker
✅ **Universal Symbols**: Use Best-Option format everywhere
✅ **High Performance**: ZeroMQ for fast message routing
✅ **Scalable**: Can handle thousands of concurrent connections
✅ **Easy Testing**: Test without broker connection

## Files

- `test_websocket.html` - Test page for WebSocket
- `start_websocket.py` - Start WebSocket proxy server
- `websocket_proxy/server.py` - WebSocket proxy implementation
- `websocket_proxy/base_adapter.py` - Base class for broker adapters
- `websocket_proxy/mapping.py` - Symbol mapping utilities
