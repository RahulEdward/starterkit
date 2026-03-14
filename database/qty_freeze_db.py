"""
Quantity Freeze Database
Manages position size limits per symbol
"""
from utils.logging import get_logger

logger = get_logger(__name__)


def get_freeze_qty_for_option(symbol: str, exchange: str) -> int:
    """
    Get freeze quantity for an option symbol
    
    Args:
        symbol: Option symbol
        exchange: Exchange code
    
    Returns:
        Freeze quantity (0 if not found)
    """
    # TODO: Implement freeze quantity lookup
    # For now, return default values
    freeze_limits = {
        'NIFTY': 1800,
        'BANKNIFTY': 900,
        'FINNIFTY': 1800,
        'MIDCPNIFTY': 2800,
    }
    
    # Extract underlying from symbol
    for underlying, limit in freeze_limits.items():
        if symbol.startswith(underlying):
            return limit
    
    return 0  # No freeze limit
