"""
Positions & Portfolio Routes
"""
from fastapi import APIRouter

router = APIRouter(prefix="/api/positions", tags=["Positions"])

@router.get("/")
async def get_positions():
    """Get all current positions"""
    return {"positions": [], "message": "Positions endpoint"}

@router.get("/pnl")
async def get_pnl():
    """Get profit and loss summary"""
    return {"pnl": 0, "message": "P&L endpoint"}
