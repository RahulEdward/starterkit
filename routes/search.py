"""
Symbol Search Routes
Search symbols with universal and broker-specific formats
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from database.symbol_db import search_symbols_in_cache
from utils.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/search", tags=["Search"])


@router.get("/symbols")
async def search_symbols(
    query: str = Query(..., min_length=1, description="Search query"),
    exchange: Optional[str] = Query(None, description="Exchange filter (NSE, NFO, BSE, etc.)")
):
    """
    Search symbols - shows both universal format and broker-specific format
    
    Returns:
    - symbol: Best-Option universal format
    - brsymbol: Broker-specific format (AngelOne)
    - exchange: Exchange name
    - token: Instrument token
    - Other details: expiry, strike, lotsize, etc.
    """
    try:
        if not query or not query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        query = query.strip().upper()
        logger.info(f"Searching symbols: query='{query}', exchange={exchange}")
        
        # Search in database
        results = search_symbols_in_cache(query, exchange, limit=50)
        
        if not results:
            return {
                "status": "success",
                "message": "No matching symbols found",
                "data": []
            }
        
        logger.info(f"Found {len(results)} results for query: {query}")
        
        return {
            "status": "success",
            "message": f"Found {len(results)} matching symbols",
            "data": results
        }
        
    except Exception as e:
        logger.error(f"Error searching symbols: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")
