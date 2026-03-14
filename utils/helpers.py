"""
General Helper Functions
"""
from datetime import datetime
from typing import Any

def get_current_timestamp() -> str:
    """Get current timestamp in ISO format"""
    return datetime.utcnow().isoformat()

def format_price(price: float, decimals: int = 2) -> str:
    """Format price with specified decimal places"""
    return f"{price:.{decimals}f}"
