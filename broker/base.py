"""
Base Broker Interface
All broker implementations should inherit from this base class
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Any

class BaseBroker(ABC):
    """Abstract base class for broker integrations"""
    
    @abstractmethod
    async def connect(self) -> bool:
        """Establish connection with broker"""
        pass
    
    @abstractmethod
    async def get_positions(self) -> List[Dict[str, Any]]:
        """Fetch current positions"""
        pass
    
    @abstractmethod
    async def place_order(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """Place a new order"""
        pass
    
    @abstractmethod
    async def get_market_data(self, symbol: str) -> Dict[str, Any]:
        """Get real-time market data for a symbol"""
        pass
