"""
Pydantic Schemas for Request/Response Validation
"""
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class TradeBase(BaseModel):
    symbol: str
    order_type: str
    quantity: int
    price: float

class TradeCreate(TradeBase):
    pass

class TradeResponse(TradeBase):
    id: int
    timestamp: datetime
    
    class Config:
        from_attributes = True
