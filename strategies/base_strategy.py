"""
Base Strategy Class
All trading strategies should inherit from this
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Any

class BaseStrategy(ABC):
    """Abstract base class for trading strategies"""
    
    def __init__(self, name: str):
        self.name = name
    
    @abstractmethod
    async def generate_signals(self, market_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate trading signals based on market data"""
        pass
    
    @abstractmethod
    async def execute(self, signals: List[Dict[str, Any]]) -> bool:
        """Execute the strategy based on signals"""
        pass
