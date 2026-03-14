"""
Token Database - Symbol and Token Mapping
Uses in-memory cache for fast symbol lookups
"""
from database.symbol_db import (
    get_token,
    get_symbol,
    get_br_symbol,
    get_oa_symbol,
    get_symbol_info,
    get_symbol_count,
    search_symbols,
    clear_cache,
    load_cache_for_broker
)
from utils.logging import get_logger

logger = get_logger(__name__)

# Re-export all functions for backward compatibility
__all__ = [
    'get_token',
    'get_symbol', 
    'get_br_symbol',
    'get_oa_symbol',
    'get_symbol_info',
    'get_symbol_count',
    'search_symbols',
    'clear_cache',
    'load_cache_for_broker'
]
