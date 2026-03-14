# WebSocket Live Market Data Testing

This guide explains how to test the WebSocket proxy for live market data streaming.

## Architecture

```
┌─────────────────┐         ┌──────────────────┐         ┌─────────────────┐
│  Broker WebSocket│ ──────> │  WebSocket Proxy │ ──────> │  Client (Web)   │
│  (AngelOne/Fyers)│  ZeroMQ │  (Best-Option)   │  WS     │  (Dashboard)    │
└─────────────────┘         └──────────────────┘         └─────────────────┘
```

**Flow:**
1. Broker adapter connects to broker's WebSocket API
2. Receives live market data from broker
3. Publishes to ZeroMQ (internal message bus)
4. WebSocket proxy subscribes to ZeroMQ
5. Forwards data to connected web clients

**Symbol Conversion:**
- Client uses Best-Option universal symbols (e.g., "RELIANCE", "NIFTY")
- Proxy converts to broker-specific tokens automatically
- Broker receives data with broker tokens
- Proxy converts back to universal format for client

## Testing Steps

### Step 1: Start Mock Broker Adapter (Terminal 1)

This simulates a broker sending live market data:

```bash
python test_mock_broker_adapter.py
```

You should see:
```
Mock Broker Adapter - Generating Market Data
Publishing data for:
  - RELIANCE (NSE): ₹2450.50
  - TCS (NSE): ₹3650.75
  ...
```

### Step 2: Start WebSocket Proxy Server (Terminal 2)

This is the main proxy that clients connect to:

```bash
python run_websocket_server.py
```

You should see:
```
Best-Option WebSocket Proxy Server
Host: 127.0.0.1
Port: 8765
Starting server...
WebSocket server started on 127.0.0.1:8765
```

### Step 3: Run Test Client (Terminal 3)

This simulates a web client connecting and subscribing:

```bash
python test_websocket_client.py
```

You should see:
```
Best-Option WebSocket Test Client
✓ Connected to ws://127.0.0.1:8765

Step 1: Authenticating...
Response: {"type": "authenticated", "status": "success", ...}

Step 2: Subscribing to RELIANCE-NSE...
Response: {"type": "subscribed", "status": "success", ...}

Step 3: Listening for market data (10 seconds)...
[1] {
  "symbol": "RELIANCE",
  "exchange": "NSE",
  "ltp": 2451.25,
  "change": 0.75,
  "change_pct": 0.03,
  ...
}
```

## WebSocket API Reference

### 1. Authentication

```json
{
  "action": "authenticate",
  "user_id": 1
}
```

Response:
```json
{
  "type": "authenticated",
  "status": "success",
  "user_id": 1,
  "broker": "fyers"
}
```

### 2. Subscribe to Symbol

```json
{
  "action": "subscribe",
  "symbol": "RELIANCE",
  "exchange": "NSE",
  "mode": "LTP"
}
```

Response:
```json
{
  "type": "subscribed",
  "status": "success",
  "symbol": "RELIANCE",
  "exchange": "NSE",
  "mode": "LTP"
}
```

### 3. Market Data (Received automatically)

```json
{
  "symbol": "RELIANCE",
  "exchange": "NSE",
  "ltp": 2450.50,
  "change": 5.25,
  "change_pct": 0.21,
  "volume": 1250000,
  "timestamp": 1710412345678
}
```

### 4. Unsubscribe

```json
{
  "action": "unsubscribe",
  "symbol": "RELIANCE",
  "exchange": "NSE",
  "mode": "LTP"
}
```

### 5. Ping/Pong (Keep-alive)

```json
{
  "action": "ping",
  "timestamp": 1710412345678
}
```

Response:
```json
{
  "type": "pong",
  "timestamp": 1710412345678
}
```

## Integration with Frontend

To integrate with your React dashboard:

```javascript
// Connect to WebSocket
const ws = new WebSocket('ws://127.0.0.1:8765');

// Authenticate
ws.onopen = () => {
  ws.send(JSON.stringify({
    action: 'authenticate',
    user_id: user.id
  }));
};

// Handle messages
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  
  if (data.type === 'authenticated') {
    // Subscribe to symbols
    ws.send(JSON.stringify({
      action: 'subscribe',
      symbol: 'RELIANCE',
      exchange: 'NSE',
      mode: 'LTP'
    }));
  } else if (data.symbol) {
    // Market data received
    console.log(`${data.symbol}: ₹${data.ltp}`);
    updatePrice(data.symbol, data.ltp);
  }
};
```

## Next Steps

1. **Implement Real Broker Adapters:**
   - `broker/angelone/streaming/angel_adapter.py` - AngelOne WebSocket
   - `broker/fyers/streaming/fyers_adapter.py` - Fyers WebSocket

2. **Add to Main App:**
   - Start WebSocket proxy when backend starts
   - Auto-start broker adapter when user logs in

3. **Frontend Integration:**
   - Add WebSocket connection to Dashboard
   - Display live prices in symbol search results
   - Create live price ticker component

## Troubleshooting

**Connection Refused:**
- Make sure WebSocket server is running on port 8765
- Check firewall settings

**No Data Received:**
- Verify mock broker adapter is running
- Check ZeroMQ port (default: 5555)
- Ensure symbols match exactly

**Authentication Failed:**
- Verify user_id exists in database
- Check database connection

## Configuration

Environment variables (optional):

```bash
# WebSocket Server
WEBSOCKET_HOST=127.0.0.1
WEBSOCKET_PORT=8765

# ZeroMQ
ZMQ_HOST=127.0.0.1
ZMQ_PORT=5555

# Broker WebSocket
MAX_SYMBOLS_PER_WEBSOCKET=1000
MAX_WEBSOCKET_CONNECTIONS=3
```
