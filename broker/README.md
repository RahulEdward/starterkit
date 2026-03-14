# Broker Integrations

Multi-broker support for Best-Option desktop application.

## Supported Brokers

### AngelOne
- **Status**: ✅ Integrated
- **Features**: Orders, Positions, Market Data, WebSocket Streaming
- **Docs**: [broker/angelone/README.md](angelone/README.md)

## Planned Brokers

- [ ] Zerodha (Kite Connect)
- [ ] Dhan
- [ ] Fyers
- [ ] Upstox

## Adding New Brokers

Each broker integration should follow this structure:

```
broker/
└── broker_name/
    ├── api/                  # API integration
    │   ├── auth_api.py
    │   ├── order_api.py
    │   └── data.py
    ├── mapping/              # Data transformations
    ├── streaming/            # WebSocket handlers
    ├── database/             # DB operations
    ├── plugin.json           # Metadata
    └── README.md             # Documentation
```

## Base Broker Interface

All brokers should implement the base interface defined in `broker/base.py`:

```python
from broker.base import BaseBroker

class MyBroker(BaseBroker):
    async def connect(self) -> bool:
        # Implementation
        pass
    
    async def place_order(self, order_data: dict) -> dict:
        # Implementation
        pass
```

## Credits

Third-party broker integrations adapted for Best-Option desktop application.
