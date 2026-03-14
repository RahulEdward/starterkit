# AngelOne Broker Integration

AngelOne broker integration for Best-Option desktop application.

## Source
Adapted from open-source AngelOne broker integration reference.

## Structure

```
broker/angelone/
├── api/                      # API integration modules
│   ├── auth_api.py          # Authentication
│   ├── order_api.py         # Order management
│   ├── data.py              # Market data
│   ├── funds.py             # Funds & margin
│   └── margin_api.py        # Margin calculations
├── database/                 # Database operations
│   └── master_contract_db.py
├── mapping/                  # Data transformation
│   ├── transform_data.py    # Order data mapping
│   ├── order_data.py        # Order transformations
│   └── margin_data.py       # Margin data mapping
├── streaming/                # WebSocket streaming
│   ├── angel_adapter.py     # WebSocket adapter
│   ├── angel_mapping.py     # Streaming data mapping
│   └── smartWebSocketV2.py  # AngelOne WebSocket client
└── plugin.json              # Plugin metadata
```

## Features

- Authentication with TOTP
- Order placement, modification, cancellation
- Real-time market data via WebSocket
- Position & holdings management
- Margin & funds information
- Historical data (candlestick charts)

## Configuration

Add to `.env`:
```
BROKER_API_KEY=your_angelone_api_key
```

## Usage

```python
from broker.angelone.api.auth_api import authenticate_broker
from broker.angelone.api.order_api import get_order_book

# Authenticate
auth_token, feed_token, error = authenticate_broker(
    clientcode="YOUR_CLIENT_CODE",
    broker_pin="YOUR_PIN",
    totp_code="TOTP_CODE"
)

# Get orders
orders = get_order_book(auth_token)
```

## API Endpoints

- `auth_api.py` - Login and authentication
- `order_api.py` - Place, modify, cancel orders
- `data.py` - Quotes, historical data, option chain
- `funds.py` - Margin and funds data

## Credits

Broker integration adapted from open-source trading platform reference.
