"""
Market Data Routes
"""
from fastapi import APIRouter

router = APIRouter(prefix="/api/market", tags=["Market Data"])

@router.get("/quotes/{symbol}")
async def get_quote(symbol: str):
    return {"symbol": symbol, "message": "Quote endpoint"}

@router.get("/option-chain/{symbol}")
async def get_option_chain(symbol: str):
    return {"symbol": symbol, "message": "Option chain endpoint"}
