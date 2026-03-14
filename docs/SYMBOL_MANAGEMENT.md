# Symbol Management System

## Overview
Integrated OpenAlgo's symbol management system for handling 100,000+ symbols with O(1) lookup performance.

## Components

### 1. Symbol Database (`database/symbol.py`)
- **SymToken Table**: Master contract storage
  - `symbol`: Best-Option standard format
  - `brsymbol`: Broker-specific format
  - `token`: Broker token/instrument ID
  - `exchange`: Exchange code (NFO, NSE, BSE, etc.)
  - `expiry`, `strike`, `lotsize`: Contract details

### 2. Symbol Cache (`database/symbol_db.py`)
- In-memory cache for fast lookups
- Handles 100,000+ symbols
- O(1) lookup performance
- Auto-loads on broker login

### 3. Token Database (`database/token_db.py`)
- Wrapper for symbol operations
- Functions:
  - `get_token(symbol, exchange)` - Get broker token
  - `get_symbol(token, exchange)` - Get symbol from token
  - `get_br_symbol(symbol, exchange)` - Convert to broker format
  - `get_oa_symbol(brsymbol, exchange)` - Convert to standard format

## Usage

```python
from database.token_db import get_token, get_br_symbol

# Get broker token for a symbol
token = get_token("NIFTY28MAR2420800CE", "NFO")

# Convert to broker format
br_symbol = get_br_symbol("NIFTY28MAR2420800CE", "NFO")
```

## Symbol Formats

### Best-Option Standard Format
- Options: `NIFTY28MAR2420800CE`
- Futures: `NIFTY28MAR24FUT`
- Equity: `SBIN-EQ`

### Broker Formats (AngelOne)
- Options: `NIFTY 28 Mar 2024 20800 CE`
- Futures: `NIFTY 28 Mar 2024 FUT`
- Equity: `SBIN`

## Master Contract Download

Master contracts are downloaded from broker on first login:
1. User logs in with broker
2. Backend downloads master contract
3. Symbols stored in `symtoken` table
4. Cache loaded into memory
5. Ready for trading

## Next Steps

1. Implement master contract download for AngelOne
2. Add symbol search API
3. Integrate with order placement
4. Add WebSocket symbol subscriptions
