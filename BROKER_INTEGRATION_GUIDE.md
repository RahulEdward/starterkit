# Broker Integration Guide for Best-Option

## 📚 Table of Contents
1. [Architecture Overview](#architecture-overview)
2. [Codebase Structure](#codebase-structure)
3. [How to Add a New Broker](#how-to-add-a-new-broker)
4. [Symbol Management](#symbol-management)
5. [WebSocket Integration](#websocket-integration)
6. [Testing](#testing)

---

## 🏗️ Architecture Overview

Best-Option is a **broker-agnostic** options trading platform. It uses:
- **Universal Symbol Format**: Same symbols work across all brokers
- **Plugin Architecture**: Each broker is a separate plugin
- **Shared Database**: All brokers use same `symtoken` table with `broker` column
- **Common WebSocket Proxy**: Single WebSocket server for all brokers

### Data Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLIENT (React)                          │
│  - Uses Best-Option universal symbols (e.g., "SBIN", "NIFTY")  │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    BACKEND (FastAPI)                            │
│  - Symbol Search: Filters by logged-in user's broker           │
│  - Master Contract: Downloads broker-specific symbols          │
│  - Authentication: Stores broker credentials per user          │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                  BROKER PLUGINS (Modular)                       │
│  ├─ broker/angelone/                                            │
│  │   ├─ api/          (REST API integration)                   │
│  │   ├─ database/     (Master contract download)               │
│  │   ├─ mapping/      (Data transformation)                    │
│  │   └─ streaming/    (WebSocket adapter)                      │
│  └─ broker/fyers/                                               │
│      └─ (same structure)                                        │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    SHARED DATABASE                              │
│  - symtoken table: broker | symbol | brsymbol | token | ...    │
│  - users table: broker credentials per user                    │
│  - master_contract_status: download status per broker          │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📁 Codebase Structure

```
best-options/
├── app.py                          # Main FastAPI application
├── routes/                         # API endpoints
│   ├── auth.py                     # Login, registration
│   ├── search.py                   # Symbol search (broker-filtered)
│   └── master_contract.py          # Master contract status
├── database/                       # Shared database models
│   ├── symbol.py                   # SymToken model (shared table)
│   ├── symbol_db.py                # Symbol cache & search
│   ├── user_db.py                  # User authentication
│   ├── auth_db.py                  # Broker auth tokens
│   └── master_contract_status_db.py # Download status per broker
├── broker/                         # Broker plugins
│   ├── base.py                     # Base broker interface
│   ├── angelone/                   # AngelOne plugin
│   │   ├── plugin.json             # Broker metadata
│   │   ├── api/                    # REST API integration
│   │   │   ├── auth_api.py         # Login/authentication
│   │   │   ├── order_api.py        # Place/modify orders
│   │   │   ├── data.py             # Market data
│   │   │   └── funds.py            # Account funds
│   │   ├── database/               # Master contract
│   │   │   └── master_contract_db.py # Download & process symbols
│   │   ├── mapping/                # Data transformation
│   │   │   ├── transform_data.py   # Broker → Best-Option format
│   │   │   └── order_data.py       # Order format conversion
│   │   └── streaming/              # WebSocket adapter
│   │       └── angel_adapter.py    # Live market data
│   └── fyers/                      # Fyers plugin (same structure)
├── websocket_proxy/                # Common WebSocket infrastructure
│   ├── server.py                   # WebSocket proxy server
│   ├── base_adapter.py             # Base class for broker adapters
│   └── mapping.py                  # Symbol/exchange mapping
└── frontend/                       # React frontend
    └── src/pages/
        ├── Login.jsx               # Broker selection & login
        └── Dashboard.jsx           # Symbol search & live data
```


---

## Database Schema

### 1. Users Table (`users`)
Stores user accounts with broker information.

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(120) UNIQUE,
    password_hash VARCHAR(255),
    broker VARCHAR(50),              -- 'angelone', 'fyers', 'zerodha'
    broker_api_key VARCHAR(500),     -- Broker API key / App ID
    broker_api_secret VARCHAR(500),  -- Broker API secret (for OAuth)
    redirect_url VARCHAR(500),       -- OAuth redirect URL
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME
);
```

### 2. Broker Auth Table (`broker_auth`)
Stores broker authentication tokens per user.

```sql
CREATE TABLE broker_auth (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    broker VARCHAR(50),
    broker_user_id VARCHAR(100),     -- Broker's client ID
    auth_token TEXT,                 -- Access token
    feed_token TEXT,                 -- WebSocket token / Refresh token
    created_at DATETIME,
    updated_at DATETIME
);
```

### 3. Symbol Token Table (`symtoken`)
**CRITICAL**: Shared table for ALL brokers with broker column for isolation.

```sql
CREATE TABLE symtoken (
    id INTEGER PRIMARY KEY,
    broker VARCHAR(20) NOT NULL,     -- 'angelone', 'fyers', etc.
    symbol VARCHAR(50) NOT NULL,     -- Best-Option universal format
    brsymbol VARCHAR(50) NOT NULL,   -- Broker-specific format
    name VARCHAR(200),
    exchange VARCHAR(20) NOT NULL,   -- NSE, NFO, BSE, BFO, MCX, CDS
    brexchange VARCHAR(20),          -- Broker exchange code
    token VARCHAR(50) NOT NULL,      -- Broker token/instrument ID
    expiry VARCHAR(20),              -- DD-MMM-YY format
    strike FLOAT,
    lotsize INTEGER,
    instrumenttype VARCHAR(10),      -- EQ, FUT, CE, PE
    tick_size FLOAT,
    
    INDEX idx_broker_symbol_exchange (broker, symbol, exchange),
    INDEX idx_broker_token_exchange (broker, token, exchange)
);
```

### 4. Master Contract Status Table (`master_contract_status`)
Tracks download status per broker.

```sql
CREATE TABLE master_contract_status (
    broker VARCHAR(50) PRIMARY KEY,
    status VARCHAR(20),              -- pending, downloading, success, error
    message VARCHAR(500),
    last_updated DATETIME,
    total_symbols INTEGER,
    is_ready BOOLEAN DEFAULT FALSE
);
```


---

## 🔧 How to Add a New Broker

### Step 1: Create Broker Directory Structure

```bash
mkdir -p broker/newbroker/{api,database,mapping,streaming}
touch broker/newbroker/__init__.py
touch broker/newbroker/plugin.json
```

### Step 2: Create `plugin.json`

```json
{
  "name": "newbroker",
  "display_name": "New Broker",
  "version": "1.0.0",
  "description": "New Broker integration for Best-Option",
  "auth_type": "oauth2",
  "requires_api_key": true,
  "requires_api_secret": true,
  "requires_redirect_url": true,
  "exchanges": ["NSE", "NFO", "BSE", "BFO", "MCX", "CDS"],
  "features": {
    "market_data": true,
    "order_placement": true,
    "portfolio": true,
    "websocket": true
  }
}
```

### Step 3: Implement Authentication (`api/auth_api.py`)

```python
"""
New Broker Authentication API
"""
from utils.logging import get_logger

logger = get_logger(__name__)


def authenticate_broker(client_id, pin, totp, api_key):
    """
    Authenticate with New Broker
    
    Args:
        client_id: Broker client ID
        pin: Broker PIN
        totp: 6-digit TOTP code
        api_key: API key from user registration
    
    Returns:
        tuple: (auth_token, feed_token, error_message)
    """
    try:
        # TODO: Implement broker-specific authentication
        # Example:
        # response = requests.post(
        #     "https://api.newbroker.com/auth/login",
        #     json={
        #         "client_id": client_id,
        #         "pin": pin,
        #         "totp": totp,
        #         "api_key": api_key
        #     }
        # )
        # 
        # if response.status_code == 200:
        #     data = response.json()
        #     return data["auth_token"], data["feed_token"], None
        # else:
        #     return None, None, response.json().get("message")
        
        return None, None, "Not implemented"
        
    except Exception as e:
        logger.exception(f"Authentication error: {e}")
        return None, None, str(e)
```

### Step 4: Implement Master Contract Download (`database/master_contract_db.py`)

```python
"""
New Broker Master Contract Database
Downloads and processes symbol master contract
"""
import pandas as pd
import requests
from database.symbol import SymToken, db_session
from utils.logging import get_logger

logger = get_logger(__name__)


def master_contract_download():
    """Download and process master contract from New Broker"""
    logger.info("Downloading New Broker Master Contract")
    broker = "newbroker"
    
    try:
        # Step 1: Download master contract
        url = "https://api.newbroker.com/master-contract"
        response = requests.get(url)
        data = response.json()
        
        # Step 2: Convert to DataFrame
        df = pd.DataFrame(data)
        
        # Step 3: Process and normalize symbols
        df = process_symbols(df)
        
        # Step 4: Delete old symbols for this broker
        delete_symtoken_table(broker)
        
        # Step 5: Insert new symbols
        copy_from_dataframe(df, broker)
        
        logger.info("Master contract download completed")
        return True
        
    except Exception as e:
        logger.exception(f"Master contract download failed: {e}")
        raise


def process_symbols(df):
    """
    Process broker symbols to Best-Option format
    
    CRITICAL: Convert broker-specific symbols to universal format
    
    Example transformations:
    - Broker: "SBIN-EQ" → Best-Option: "SBIN"
    - Broker: "NIFTY24MAR2422000CE" → Best-Option: "NIFTY24MAR2422000CE"
    """
    # Add broker column
    df["broker"] = "newbroker"
    
    # Map broker columns to Best-Option schema
    df = df.rename(columns={
        "broker_symbol": "brsymbol",
        "broker_token": "token",
        "broker_exchange": "brexchange",
        # ... map other columns
    })
    
    # Normalize symbols (remove broker-specific suffixes)
    df["symbol"] = df["brsymbol"].str.replace("-EQ|-BE", "", regex=True)
    
    # Set exchange
    df["exchange"] = "NSE"  # Map broker exchange to Best-Option exchange
    
    return df


def delete_symtoken_table(broker="newbroker"):
    """Delete only this broker's symbols"""
    logger.info(f"Deleting {broker} symbols")
    deleted_count = SymToken.query.filter_by(broker=broker).delete()
    db_session.commit()
    logger.info(f"Deleted {deleted_count} symbols")


def copy_from_dataframe(df, broker="newbroker"):
    """Insert symbols into database"""
    logger.info(f"Inserting {len(df)} symbols for {broker}")
    
    # Add broker column
    df["broker"] = broker
    
    # Convert to dict
    data_dict = df.to_dict(orient="records")
    
    # Bulk insert
    db_session.bulk_insert_mappings(SymToken, data_dict)
    db_session.commit()
    
    logger.info(f"Inserted {len(data_dict)} symbols")
```


---

## Symbol Management

### Universal Symbol Format (Best-Option Standard)

All brokers MUST convert their symbols to this format:

**Equity:**
- Format: `SYMBOL`
- Example: `RELIANCE`, `TCS`, `SBIN`

**Index:**
- Format: `INDEXNAME`
- Example: `NIFTY`, `BANKNIFTY`, `SENSEX`

**Futures:**
- Format: `SYMBOL[DDMMMYY]FUT`
- Example: `NIFTY28MAR24FUT`, `RELIANCE30APR24FUT`

**Options:**
- Format: `SYMBOL[DDMMMYY][STRIKE][CE/PE]`
- Example: `NIFTY28MAR2422000CE`, `BANKNIFTY24APR2448000PE`

### Symbol Conversion Flow

```
Broker Symbol → process_broker_csv() → Universal Format → Database
                                                              ↓
Client Request → get_symbol_token() → Broker Token → Broker API
```

### Key Functions

**1. Symbol Storage** (`broker/{broker}/database/master_contract_db.py`):
```python
def copy_from_dataframe(df, broker="brokername"):
    """
    Insert symbols into shared symtoken table
    MUST add broker column to all rows
    """
    df["broker"] = broker  # CRITICAL: Add broker identifier
    data_dict = df.to_dict(orient="records")
    db_session.bulk_insert_mappings(SymToken, data_dict)
    db_session.commit()
```

**2. Symbol Deletion** (before reload):
```python
def delete_symtoken_table(broker="brokername"):
    """
    Delete ONLY this broker's symbols
    NEVER delete all symbols!
    """
    deleted_count = SymToken.query.filter_by(broker=broker).delete()
    db_session.commit()
```

**3. Symbol Lookup** (`database/symbol_db.py`):
```python
def get_symbol_token(symbol, exchange, broker):
    """
    Get broker token for Best-Option symbol
    Returns: {"token": "...", "brsymbol": "...", "brexchange": "..."}
    """
    result = SymToken.query.filter_by(
        broker=broker,
        symbol=symbol,
        exchange=exchange
    ).first()
    return result
```


---

## WebSocket Architecture

### Overview

```
Client (Browser)
    ↓ WebSocket (ws://127.0.0.1:8765)
WebSocket Proxy Server (websocket_proxy/server.py)
    ↓ ZeroMQ (tcp://127.0.0.1:5555)
Broker Adapter (broker/{broker}/streaming/{broker}_adapter.py)
    ↓ Broker WebSocket API
Broker Server
```

### Components

**1. WebSocket Proxy Server** (`websocket_proxy/server.py`)
- Handles client connections
- Manages subscriptions
- Routes data from ZeroMQ to clients
- **Already built - no changes needed**

**2. Base Broker Adapter** (`websocket_proxy/base_adapter.py`)
- Abstract base class for all broker adapters
- Provides ZeroMQ publishing
- **Inherit from this class**

**3. Broker-Specific Adapter** (`broker/{broker}/streaming/{broker}_adapter.py`)
- Connects to broker's WebSocket API
- Subscribes to symbols
- Converts broker format → Best-Option format
- Publishes to ZeroMQ
- **You need to implement this**

### Message Flow

**Client → Proxy:**
```json
{
  "action": "subscribe",
  "symbol": "RELIANCE",
  "exchange": "NSE",
  "mode": "LTP"
}
```

**Proxy → Broker Adapter:**
- Proxy looks up broker token using `get_symbol_token()`
- Converts "RELIANCE" → broker token (e.g., "2885")
- Broker adapter subscribes to token on broker's WebSocket

**Broker → Adapter → Proxy → Client:**
```json
{
  "symbol": "RELIANCE",
  "exchange": "NSE",
  "ltp": 2450.50,
  "change": 5.25,
  "volume": 1234567,
  "timestamp": 1710412345678
}
```

### ZeroMQ Topic Format

**Topic:** `{SYMBOL}_{EXCHANGE}_{MODE}`
**Examples:**
- `RELIANCE_NSE_LTP`
- `NIFTY_NSE_INDEX_QUOTE`
- `SBIN_NSE_LTP`


### Step 5: Add to Authentication Route (`routes/auth.py`)

```python
# In routes/auth.py, add to login function:

elif data.broker == "newbroker":
    # Validate required fields
    if not data.client_id or not data.pin or not data.totp:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="client_id, pin, and totp are required"
        )
    
    # Get API key from user database
    broker_api_key = user.broker_api_key
    if not broker_api_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Broker API key not found"
        )
    
    # Import broker auth function
    from broker.newbroker.api.auth_api import authenticate_broker as authenticate_newbroker
    
    # Authenticate
    auth_token, feed_token, error = authenticate_newbroker(
        client_id=data.client_id,
        pin=data.pin,
        totp=data.totp,
        api_key=broker_api_key
    )
    
    if error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: {error}"
        )
    
    # Store tokens
    upsert_broker_auth(
        user_id=user.id,
        broker=data.broker,
        broker_user_id=data.client_id,
        auth_token=auth_token,
        feed_token=feed_token
    )
    
    # Initialize master contract status
    init_broker_status(data.broker)
    
    # Start master contract download in background
    from broker.newbroker.database.master_contract_db import master_contract_download as newbroker_download
    thread = Thread(target=async_master_contract_download, args=(data.broker,), daemon=True)
    thread.start()
    
    return LoginResponse(
        status="success",
        message="Login successful",
        user=user.to_dict(),
        auth_token=auth_token,
        feed_token=feed_token
    )
```

### Step 6: Update `async_master_contract_download` function

```python
# In routes/auth.py, add to async_master_contract_download:

elif broker == "newbroker":
    from broker.newbroker.database.master_contract_db import master_contract_download as newbroker_download
    newbroker_download()
```

### Step 7: Add to Frontend Login (`frontend/src/pages/Login.jsx`)

```javascript
// Add to broker options:
<option value="newbroker">New Broker</option>

// Add to broker-specific fields:
{selectedBroker === 'newbroker' && (
  <>
    <input
      type="text"
      placeholder="API Key"
      value={apiKey}
      onChange={(e) => setApiKey(e.target.value)}
      required
    />
    <input
      type="password"
      placeholder="Client ID"
      value={clientId}
      onChange={(e) => setClientId(e.target.value)}
      required
    />
    <input
      type="password"
      placeholder="PIN"
      value={pin}
      onChange={(e) => setPin(e.target.value)}
      required
    />
    <input
      type="text"
      placeholder="TOTP"
      value={totp}
      onChange={(e) => setTotp(e.target.value)}
      required
    />
  </>
)}
```

---

## 📊 Symbol Management

### Universal Symbol Format

Best-Option uses a **universal symbol format** that works across all brokers:

| Type | Format | Example |
|------|--------|---------|
| Equity | `SYMBOL` | `SBIN`, `RELIANCE` |
| Index | `INDEXNAME` | `NIFTY`, `BANKNIFTY` |
| Futures | `SYMBOL[DDMMMYY]FUT` | `NIFTY28MAR24FUT` |
| Options | `SYMBOL[DDMMMYY][STRIKE][CE/PE]` | `NIFTY28MAR2422000CE` |

### Symbol Conversion Flow

```
1. User searches "SBIN" in frontend
2. Backend searches symtoken table with broker filter
3. Returns both formats:
   - symbol: "SBIN" (universal)
   - brsymbol: "SBIN-EQ" (broker-specific)
4. For orders/WebSocket, convert to broker format
5. For display, always use universal format
```

### Database Schema

```sql
CREATE TABLE symtoken (
    id INTEGER PRIMARY KEY,
    broker VARCHAR(20) NOT NULL,        -- "angelone", "fyers", "newbroker"
    symbol VARCHAR(50) NOT NULL,        -- Best-Option universal format
    brsymbol VARCHAR(50) NOT NULL,      -- Broker-specific format
    name VARCHAR(200),                  -- Full name
    exchange VARCHAR(20) NOT NULL,      -- NSE, NFO, BSE, etc.
    brexchange VARCHAR(20),             -- Broker exchange code
    token VARCHAR(50) NOT NULL,         -- Broker token/instrument ID
    expiry VARCHAR(20),                 -- Expiry date (DD-MMM-YY)
    strike FLOAT,                       -- Strike price
    lotsize INTEGER,                    -- Lot size
    instrumenttype VARCHAR(10),         -- EQ, FUT, CE, PE
    tick_size FLOAT                     -- Minimum price movement
);

CREATE INDEX idx_broker_symbol_exchange ON symtoken(broker, symbol, exchange);
```

### Symbol Search Implementation

```python
# In database/symbol_db.py

def search_symbols_in_cache(query: str, exchange: str = None, broker: str = None, limit: int = 50):
    """
    Search symbols with broker filter
    
    CRITICAL: Always filter by broker to show only user's broker symbols
    """
    from database.symbol import SymToken, db_session
    
    search_query = db_session.query(SymToken)
    
    # Filter by broker (IMPORTANT!)
    if broker:
        search_query = search_query.filter(SymToken.broker == broker)
    
    # Search in symbol, brsymbol, name
    search_query = search_query.filter(
        (SymToken.symbol.like(f"%{query}%")) |
        (SymToken.brsymbol.like(f"%{query}%")) |
        (SymToken.name.like(f"%{query}%"))
    )
    
    # Filter by exchange
    if exchange:
        search_query = search_query.filter(SymToken.exchange == exchange.upper())
    
    results = search_query.limit(limit).all()
    
    return [
        {
            "symbol": r.symbol,      # Universal format
            "brsymbol": r.brsymbol,  # Broker format
            "name": r.name,
            "exchange": r.exchange,
            "token": r.token,
            # ... other fields
        }
        for r in results
    ]
```


---

## 🔌 WebSocket Integration

### Architecture

```
Client Browser
    ↓ ws://127.0.0.1:8765
WebSocket Proxy (websocket_proxy/server.py) - Already Built ✅
    ↓ ZeroMQ (tcp://127.0.0.1:5555)
Broker Adapter (broker/newbroker/streaming/newbroker_adapter.py) - You Create
    ↓ Broker WebSocket API
Broker Server
```

### Step 1: Create WebSocket Adapter

Create `broker/newbroker/streaming/newbroker_adapter.py`:

```python
"""
New Broker WebSocket Adapter
Connects to broker's WebSocket and publishes to ZeroMQ
"""
import json
import asyncio
from websocket_proxy.base_adapter import BaseBrokerWebSocketAdapter
from database.symbol_db import get_symbol_token
from utils.logging import get_logger

logger = get_logger(__name__)


class NewBrokerWebSocketAdapter(BaseBrokerWebSocketAdapter):
    """WebSocket adapter for New Broker"""
    
    def __init__(self):
        super().__init__()
        self.ws = None
        self.subscriptions = {}
    
    def initialize(self, broker_name, user_id, auth_data=None):
        """Initialize with user credentials"""
        self.broker_name = broker_name
        self.user_id = user_id
        self.auth_token = auth_data.get("auth_token")
        self.feed_token = auth_data.get("feed_token")
        logger.info(f"Initialized {broker_name} adapter for user {user_id}")
    
    async def connect(self):
        """Connect to broker's WebSocket"""
        try:
            # TODO: Connect to broker WebSocket
            # Example:
            # import websockets
            # self.ws = await websockets.connect(
            #     "wss://api.newbroker.com/ws",
            #     extra_headers={"Authorization": f"Bearer {self.auth_token}"}
            # )
            
            self.connected = True
            logger.info("Connected to New Broker WebSocket")
            
            # Start listening for messages
            asyncio.create_task(self.listen())
            
        except Exception as e:
            logger.exception(f"Connection error: {e}")
            self.connected = False
    
    async def disconnect(self):
        """Disconnect from broker WebSocket"""
        self.connected = False
        if self.ws:
            await self.ws.close()
        logger.info("Disconnected from New Broker WebSocket")
    
    async def subscribe(self, symbol, exchange, mode=2):
        """
        Subscribe to market data
        
        Args:
            symbol: Best-Option universal symbol (e.g., "SBIN")
            exchange: Exchange code (e.g., "NSE")
            mode: Data mode (1=LTP, 2=Quote, 3=Snap Quote)
        """
        try:
            # Get broker token from database
            token_data = get_symbol_token(symbol, exchange, self.broker_name)
            if not token_data:
                logger.error(f"Symbol not found: {symbol}-{exchange}")
                return
            
            broker_token = token_data["token"]
            
            # Subscribe to broker WebSocket
            # TODO: Send subscription message to broker
            # Example:
            # subscribe_msg = {
            #     "action": "subscribe",
            #     "tokens": [broker_token],
            #     "mode": mode
            # }
            # await self.ws.send(json.dumps(subscribe_msg))
            
            # Store subscription
            self.subscriptions[broker_token] = {
                "symbol": symbol,
                "exchange": exchange,
                "mode": mode
            }
            
            logger.info(f"Subscribed to {symbol} (token: {broker_token})")
            
        except Exception as e:
            logger.exception(f"Subscribe error: {e}")
    
    async def unsubscribe(self, symbol, exchange, mode=2):
        """Unsubscribe from market data"""
        try:
            token_data = get_symbol_token(symbol, exchange, self.broker_name)
            if not token_data:
                return
            
            broker_token = token_data["token"]
            
            # TODO: Send unsubscribe message to broker
            
            # Remove from subscriptions
            if broker_token in self.subscriptions:
                del self.subscriptions[broker_token]
            
            logger.info(f"Unsubscribed from {symbol}")
            
        except Exception as e:
            logger.exception(f"Unsubscribe error: {e}")
    
    async def listen(self):
        """Listen for messages from broker WebSocket"""
        try:
            while self.connected:
                # TODO: Receive message from broker
                # Example:
                # message = await self.ws.recv()
                # data = json.loads(message)
                # await self.process_message(data)
                
                await asyncio.sleep(0.1)
                
        except Exception as e:
            logger.exception(f"Listen error: {e}")
            self.connected = False
    
    async def process_message(self, data):
        """
        Process message from broker and publish to ZeroMQ
        
        CRITICAL: Convert broker format to Best-Option format
        """
        try:
            # Extract broker token from message
            broker_token = data.get("token")
            
            if broker_token not in self.subscriptions:
                return
            
            sub = self.subscriptions[broker_token]
            
            # Convert to Best-Option format
            market_data = {
                "symbol": sub["symbol"],
                "exchange": sub["exchange"],
                "ltp": data.get("last_price", 0),
                "change": data.get("change", 0),
                "change_pct": data.get("change_percent", 0),
                "volume": data.get("volume", 0),
                "timestamp": data.get("timestamp", 0)
            }
            
            # Publish to ZeroMQ
            topic = f"{sub['symbol']}_{sub['exchange']}_LTP"
            self.publish_market_data(topic, market_data)
            
        except Exception as e:
            logger.exception(f"Process message error: {e}")
```

### Step 2: Test WebSocket

1. Start WebSocket proxy:
```bash
python start_websocket.py
```

2. Start broker adapter:
```python
from broker.newbroker.streaming.newbroker_adapter import NewBrokerWebSocketAdapter

adapter = NewBrokerWebSocketAdapter()
adapter.initialize("newbroker", user_id=1, auth_data={
    "auth_token": "...",
    "feed_token": "..."
})
await adapter.connect()
await adapter.subscribe("SBIN", "NSE", mode=1)
```

3. Open `test_websocket.html` in browser and test

---

## 🧪 Testing

### Test Master Contract Download

```python
from broker.newbroker.database.master_contract_db import master_contract_download

# Download symbols
master_contract_download()

# Verify in database
from database.symbol import SymToken
count = SymToken.query.filter_by(broker="newbroker").count()
print(f"Total symbols: {count}")
```

### Test Symbol Search

```python
from database.symbol_db import search_symbols_in_cache

results = search_symbols_in_cache("SBIN", broker="newbroker")
print(results)
```

### Test Authentication

```python
from broker.newbroker.api.auth_api import authenticate_broker

auth_token, feed_token, error = authenticate_broker(
    client_id="CLIENT123",
    pin="1234",
    totp="123456",
    api_key="YOUR_API_KEY"
)

if error:
    print(f"Error: {error}")
else:
    print(f"Success! Token: {auth_token}")
```

---

## 🤖 AI Assistant Instructions

**To integrate a new broker, provide:**

1. **Broker Name**: e.g., "zerodha", "upstox", "5paisa"
2. **API Documentation**: Links to broker's API docs
3. **Authentication Method**: OAuth2, API Key, or Direct Login
4. **Master Contract URL**: Where to download symbol list
5. **WebSocket URL**: For live market data (if available)

**Example Prompt:**

```
Please integrate Zerodha broker into Best-Option.

Broker Details:
- Name: zerodha
- Display Name: Zerodha Kite
- Auth Type: OAuth2
- API Docs: https://kite.trade/docs/connect/v3/
- Master Contract: https://api.kite.trade/instruments
- WebSocket: wss://ws.kite.trade/
- Exchanges: NSE, NFO, BSE, BFO, MCX, CDS

Please read BROKER_INTEGRATION_GUIDE.md and create all necessary files.
```

**AI will create:**
- ✅ `broker/zerodha/` directory structure
- ✅ `plugin.json` with broker metadata
- ✅ `api/auth_api.py` for authentication
- ✅ `database/master_contract_db.py` for symbol download
- ✅ `streaming/zerodha_adapter.py` for WebSocket
- ✅ Update `routes/auth.py` with Zerodha login
- ✅ Update frontend with Zerodha option

---

## 📝 Checklist for New Broker

- [ ] Create broker directory structure
- [ ] Add `plugin.json`
- [ ] Implement `api/auth_api.py`
- [ ] Implement `database/master_contract_db.py`
- [ ] Add broker to `routes/auth.py`
- [ ] Add broker to frontend `Login.jsx`
- [ ] Test authentication
- [ ] Test master contract download
- [ ] Test symbol search
- [ ] Implement WebSocket adapter (optional)
- [ ] Test live market data (optional)
- [ ] Update `README.md` with new broker

---

## 🎯 Key Points

1. **Always use `broker` column** in symtoken table
2. **Delete only broker's symbols** before reload
3. **Convert to universal format** in master contract processing
4. **Filter by broker** in all symbol searches
5. **Use ZeroMQ** for WebSocket communication
6. **Follow existing broker structure** (angelone/fyers as reference)

---

## 📚 Reference Files

- **AngelOne Implementation**: `broker/angelone/` (complete example)
- **Fyers Implementation**: `broker/fyers/` (OAuth2 example)
- **WebSocket Proxy**: `websocket_proxy/server.py` (already built)
- **Symbol Database**: `database/symbol.py` (shared schema)
- **Authentication**: `routes/auth.py` (login flow)

---

**Questions? Check existing broker implementations or ask AI to read this guide!** 🚀

---

## 🔌 WebSocket Integration

### Architecture

```
Client Browser
    ↓ ws://127.0.0.1:8765
WebSocket Proxy (websocket_proxy/server.py)
    ↓ ZeroMQ tcp://127.0.0.1:5555
Broker Adapter (broker/newbroker/streaming/newbroker_adapter.py)
    ↓ Broker WebSocket API
Broker Server
```

### Step 1: Create WebSocket Adapter

Create `broker/newbroker/streaming/newbroker_adapter.py`:

```python
"""
New Broker WebSocket Adapter
Connects to broker's WebSocket and publishes to ZeroMQ
"""
import json
import asyncio
from websocket_proxy.base_adapter import BaseBrokerWebSocketAdapter
from database.symbol_db import get_symbol_token
from utils.logging import get_logger

logger = get_logger(__name__)


class NewBrokerWebSocketAdapter(BaseBrokerWebSocketAdapter):
    """WebSocket adapter for New Broker"""
    
    def __init__(self):
        super().__init__()
        self.ws = None
        self.subscriptions = {}
    
    def initialize(self, broker_name, user_id, auth_data=None):
        """Initialize with broker credentials"""
        self.broker_name = broker_name
        self.user_id = user_id
        self.auth_token = auth_data.get("auth_token")
        self.feed_token = auth_data.get("feed_token")
        logger.info(f"Initialized {broker_name} adapter for user {user_id}")
    
    async def connect(self):
        """Connect to broker's WebSocket"""
        try:
            # TODO: Connect to broker WebSocket
            # Example:
            # import websockets
            # self.ws = await websockets.connect(
            #     "wss://api.newbroker.com/ws",
            #     extra_headers={
            #         "Authorization": f"Bearer {self.auth_token}"
            #     }
            # )
            
            self.connected = True
            logger.info("Connected to New Broker WebSocket")
            
            # Start listening for messages
            asyncio.create_task(self.listen())
            
        except Exception as e:
            logger.exception(f"Connection error: {e}")
            self.connected = False
    
    async def subscribe(self, symbol, exchange, mode=2):
        """
        Subscribe to market data
        
        Args:
            symbol: Best-Option universal symbol (e.g., "SBIN")
            exchange: Exchange code (e.g., "NSE")
            mode: Data mode (1=LTP, 2=Quote, 3=Snap)
        """
        try:
            # Convert Best-Option symbol to broker token
            token_data = get_symbol_token(symbol, exchange, self.broker_name)
            
            if not token_data:
                logger.error(f"Symbol not found: {symbol}-{exchange}")
                return
            
            broker_token = token_data["token"]
            
            # Subscribe to broker WebSocket
            # TODO: Send subscription message to broker
            # Example:
            # subscribe_msg = {
            #     "action": "subscribe",
            #     "tokens": [broker_token],
            #     "mode": mode
            # }
            # await self.ws.send(json.dumps(subscribe_msg))
            
            # Store subscription
            self.subscriptions[broker_token] = {
                "symbol": symbol,
                "exchange": exchange,
                "mode": mode
            }
            
            logger.info(f"Subscribed to {symbol} (token: {broker_token})")
            
        except Exception as e:
            logger.exception(f"Subscribe error: {e}")
    
    async def unsubscribe(self, symbol, exchange, mode=2):
        """Unsubscribe from market data"""
        try:
            token_data = get_symbol_token(symbol, exchange, self.broker_name)
            if not token_data:
                return
            
            broker_token = token_data["token"]
            
            # TODO: Send unsubscribe message to broker
            
            # Remove from subscriptions
            if broker_token in self.subscriptions:
                del self.subscriptions[broker_token]
            
            logger.info(f"Unsubscribed from {symbol}")
            
        except Exception as e:
            logger.exception(f"Unsubscribe error: {e}")
    
    async def listen(self):
        """Listen for messages from broker WebSocket"""
        try:
            while self.connected:
                # TODO: Receive message from broker
                # Example:
                # message = await self.ws.recv()
                # data = json.loads(message)
                # await self.process_message(data)
                
                await asyncio.sleep(0.1)
                
        except Exception as e:
            logger.exception(f"Listen error: {e}")
            self.connected = False
    
    async def process_message(self, data):
        """
        Process message from broker and publish to ZeroMQ
        
        CRITICAL: Convert broker format to Best-Option format
        """
        try:
            # Extract broker token from message
            broker_token = data.get("token")
            
            if broker_token not in self.subscriptions:
                return
            
            sub = self.subscriptions[broker_token]
            
            # Convert broker data to Best-Option format
            market_data = {
                "symbol": sub["symbol"],
                "exchange": sub["exchange"],
                "ltp": data.get("last_price", 0),
                "change": data.get("change", 0),
                "change_pct": data.get("change_percent", 0),
                "volume": data.get("volume", 0),
                "timestamp": data.get("timestamp", 0)
            }
            
            # Publish to ZeroMQ
            # Topic format: SYMBOL_EXCHANGE_MODE
            topic = f"{sub['symbol']}_{sub['exchange']}_LTP"
            self.publish_market_data(topic, market_data)
            
        except Exception as e:
            logger.exception(f"Process message error: {e}")
    
    async def disconnect(self):
        """Disconnect from broker WebSocket"""
        self.connected = False
        if self.ws:
            await self.ws.close()
        logger.info("Disconnected from New Broker WebSocket")
```

### Step 2: Test WebSocket

1. Start WebSocket proxy:
```bash
python start_websocket.py
```

2. Open test page:
```bash
# Open test_websocket.html in browser
```

3. Connect and subscribe to symbols

---

## 🧪 Testing

### Test Master Contract Download

```python
# Test script
from broker.newbroker.database.master_contract_db import master_contract_download

# Download symbols
master_contract_download()

# Verify in database
from database.symbol import SymToken, db_session
count = SymToken.query.filter_by(broker="newbroker").count()
print(f"Total symbols: {count}")
```

### Test Symbol Search

```python
from database.symbol_db import search_symbols_in_cache

# Search symbols
results = search_symbols_in_cache("SBIN", broker="newbroker")
print(results)
```

### Test WebSocket

1. Start proxy: `python start_websocket.py`
2. Open `test_websocket.html`
3. Connect with user ID
4. Subscribe to symbols
5. Check logs for data

---

## 📝 Quick Reference for AI

### To Add New Broker "XYZ":

**1. Tell AI:**
```
"Add broker XYZ to Best-Option. Read BROKER_INTEGRATION_GUIDE.md and implement:
1. Authentication API
2. Master contract download with symbol conversion
3. WebSocket adapter for live data
4. Update routes/auth.py to include XYZ
5. Update frontend Login.jsx to show XYZ option"
```

**2. Provide Broker Details:**
- Broker name: `xyz`
- Auth type: `oauth2` or `credentials`
- API documentation URL
- Master contract download URL
- WebSocket endpoint URL
- Symbol format examples

**3. AI Will:**
- Create `broker/xyz/` directory structure
- Implement all required files
- Add to authentication flow
- Add to frontend
- Create symbol conversion logic
- Implement WebSocket adapter

### Key Files to Modify:

1. **New Files:**
   - `broker/xyz/api/auth_api.py`
   - `broker/xyz/database/master_contract_db.py`
   - `broker/xyz/streaming/xyz_adapter.py`

2. **Existing Files:**
   - `routes/auth.py` (add broker case)
   - `frontend/src/pages/Login.jsx` (add broker option)
   - `frontend/src/pages/Register.jsx` (add broker option)

### Critical Rules:

✅ **DO:**
- Always add `broker` column to symbols
- Filter symbols by broker in search
- Delete only broker's symbols before reload
- Use universal symbol format
- Inherit from `BaseBrokerWebSocketAdapter`

❌ **DON'T:**
- Delete all symbols (use `filter_by(broker=...)`)
- Mix broker-specific and universal formats
- Hardcode broker names in shared code
- Skip symbol conversion

---

## 🎯 Example: Adding Zerodha

```bash
# AI Command:
"Add Zerodha broker to Best-Option. Read BROKER_INTEGRATION_GUIDE.md.

Broker details:
- Name: zerodha
- Auth: OAuth2 (Kite Connect)
- API Key required: Yes
- Master contract: https://api.kite.trade/instruments
- WebSocket: wss://ws.kite.trade
- Symbol format: NSE:SBIN, NFO:NIFTY24MAR2422000CE

Implement:
1. OAuth2 authentication
2. Master contract download (CSV format)
3. Symbol conversion (NSE:SBIN → SBIN)
4. WebSocket adapter
5. Add to login flow"
```

AI will create complete integration following this guide!

---

## 📚 Additional Resources

- **OpenAlgo Reference**: Check `openalgo/` folder for examples
- **AngelOne Implementation**: `broker/angelone/` (complete example)
- **Fyers Implementation**: `broker/fyers/` (OAuth2 example)
- **WebSocket Test**: `test_websocket.html`
- **Database Schema**: `database/symbol.py`

---

**Last Updated**: 2024-03-14
**Version**: 1.0.0
