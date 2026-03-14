"""
Constants for Best-Option
Exchange codes and broker configurations
"""

# Indian F&O Exchanges
FNO_EXCHANGES = {
    "NFO",      # NSE Futures & Options
    "BFO",      # BSE Futures & Options  
    "MCX",      # Multi Commodity Exchange
    "CDS",      # Currency Derivatives
    "BCD",      # BSE Currency Derivatives
}

# Crypto Exchanges
CRYPTO_EXCHANGES = {
    "CRYPTO",
    "DELTAEXCHANGE",
}

# All supported exchanges
ALL_EXCHANGES = FNO_EXCHANGES | CRYPTO_EXCHANGES | {
    "NSE",          # NSE Cash
    "BSE",          # BSE Cash
    "NSE_INDEX",    # NSE Indices
    "BSE_INDEX",    # BSE Indices
}

# Crypto brokers
CRYPTO_BROKERS = {
    "deltaexchange",
}

# Broker list
SUPPORTED_BROKERS = [
    "angelone",
    "zerodha", 
    "dhan",
    "fyers",
    "upstox",
]
