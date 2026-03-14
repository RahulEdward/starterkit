# Authentication & Token Management

## Token Types (Like OpenAlgo)

### 1. Auth Token (JWT)
- **Purpose**: Main authentication token from broker
- **Source**: Broker API after successful login
- **Storage**: `broker_auth.auth_token` table
- **Usage**: All API calls to broker

### 2. Feed Token
- **Purpose**: WebSocket streaming authentication
- **Source**: AngelOne provides this during login
- **Storage**: `broker_auth.feed_token` table
- **Usage**: Real-time market data streaming
- **Note**: Not all brokers provide this (AngelOne does)

### 3. Broker User ID
- **Purpose**: Broker's client ID/user ID
- **Source**: Provided during login (client_id field)
- **Storage**: `broker_auth.broker_user_id` table
- **Usage**: Reference for broker-specific operations

## Database Schema

```sql
CREATE TABLE broker_auth (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,           -- Our internal user ID
    broker VARCHAR(50) NOT NULL,        -- angelone, zerodha, etc.
    broker_user_id VARCHAR(100),        -- Broker's client ID
    auth_token TEXT,                    -- JWT token from broker
    feed_token TEXT,                    -- WebSocket feed token
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME,
    updated_at DATETIME
);
```

## Login Flow

1. User enters: email, broker, client_id, pin, totp
2. Backend calls broker API: `authenticate_broker(client_id, pin, totp, api_key)`
3. Broker returns: `auth_token`, `feed_token` (AngelOne)
4. Store in database:
   - `auth_token` → For API calls
   - `feed_token` → For WebSocket
   - `broker_user_id` → client_id
5. Return to frontend: user data + tokens

## Symbol Management (Next Phase)

OpenAlgo uses a sophisticated symbol caching system:
- Master contract database per broker
- In-memory cache for 100,000+ symbols
- Symbol format conversion (OpenAlgo ↔ Broker)
- Token lookup for trading

To be integrated in next phase.
