"""
Master Contract Status Routes
"""
from fastapi import APIRouter, HTTPException
from database.master_contract_status_db import get_status, check_if_ready

router = APIRouter(prefix="/api/master-contract", tags=["Master Contract"])


@router.get("/status")
async def get_master_contract_status(broker: str = "angelone"):
    """
    Get the current master contract download status
    
    Returns status indicator for dashboard
    """
    try:
        status = get_status(broker)
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ready")
async def check_master_contract_ready(broker: str = "angelone"):
    """
    Check if master contracts are ready for trading
    """
    try:
        is_ready = check_if_ready(broker)
        return {
            "ready": is_ready,
            "message": "Master contracts are ready" if is_ready else "Master contracts not ready"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
