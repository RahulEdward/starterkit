"""
Trading Strategies Routes
"""
from fastapi import APIRouter

router = APIRouter(prefix="/api/strategies", tags=["Strategies"])

@router.get("/")
async def get_strategies():
    """Get all available strategies"""
    return {"strategies": ["Straddle", "Strangle", "Iron Condor"], "message": "Strategies list"}

@router.post("/{strategy_name}/execute")
async def execute_strategy(strategy_name: str):
    """Execute a trading strategy"""
    return {"strategy": strategy_name, "message": "Strategy execution started"}
