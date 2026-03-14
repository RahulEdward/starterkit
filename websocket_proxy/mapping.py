"""
Symbol and Exchange Mapping for WebSocket Proxy
Converts Best-Option universal symbols to broker-specific tokens
"""
from database.symbol_db import get_symbol_token
from utils.logging import get_logger

logger = get_logger("symbol_mapper")


class SymbolMapper:
    """Maps Best-Option universal symbols to broker-specific tokens"""

    @staticmethod
    def get_token_from_symbol(symbol, exchange):
        """
        Convert Best-Option universal symbol to broker-specific token

        Args:
            symbol (str): Best-Option universal symbol (e.g., 'RELIANCE', 'NIFTY02MAR2630600CE')
            exchange (str): Exchange code (e.g., 'NSE', 'NFO', 'BSE')

        Returns:
            dict: Token data with 'token' and 'brsymbol' or None if not found
        """
        try:
            # Get token from database using Best-Option symbol
            result = get_symbol_token(symbol, exchange)

            if not result:
                logger.error(f"Symbol not found: {symbol}-{exchange}")
                return None

            return {
                "token": result.get("token"),
                "brsymbol": result.get("brsymbol"),
                "brexchange": result.get("brexchange")
            }
        except Exception as e:
            logger.exception(f"Error retrieving symbol: {e}")
            return None


class ExchangeMapper:
    """Maps Best-Option exchange codes to broker-specific exchange types"""

    # AngelOne exchange mapping
    ANGELONE_EXCHANGE_MAP = {
        "NSE": 1,
        "NFO": 2,
        "BSE": 3,
        "BFO": 4,
        "CDS": 5,
        "MCX": 7
    }

    # Fyers exchange mapping
    FYERS_EXCHANGE_MAP = {
        "NSE": 10,
        "NFO": 11,
        "BSE": 12,
        "BFO": 13,
        "CDS": 14,
        "MCX": 15
    }

    @staticmethod
    def get_exchange_type(exchange, broker):
        """
        Convert exchange code to broker-specific exchange type

        Args:
            exchange (str): Exchange code (e.g., 'NSE', 'BSE')
            broker (str): Broker name ('angelone', 'fyers')

        Returns:
            int: Broker-specific exchange type
        """
        if broker == "angelone":
            return ExchangeMapper.ANGELONE_EXCHANGE_MAP.get(exchange, 1)
        elif broker == "fyers":
            return ExchangeMapper.FYERS_EXCHANGE_MAP.get(exchange, 10)
        else:
            logger.warning(f"Unknown broker: {broker}, defaulting to NSE")
            return 1
