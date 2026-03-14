"""
Authentication Routes
User registration and login endpoints
"""
import asyncio
from threading import Thread

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr

from broker.angelone.api.auth_api import authenticate_broker
from broker.angelone.database.master_contract_db import master_contract_download
from database.auth_db import upsert_broker_auth
from database.master_contract_status_db import init_broker_status, update_status
from database.user_db import add_user, authenticate_user, get_user_by_email
from utils.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


# Pydantic models for request/response
class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    confirm_password: str
    broker: str
    broker_api_key: str = None


class RegisterResponse(BaseModel):
    status: str
    message: str
    user_id: int = None


class LoginRequest(BaseModel):
    broker: str
    client_id: str
    pin: str
    totp: str
    email: str = None  # Optional - will be fetched from database if not provided


class LoginResponse(BaseModel):
    status: str
    message: str
    user: dict = None
    auth_token: str = None
    feed_token: str = None


@router.post("/register", response_model=RegisterResponse)
async def register(data: RegisterRequest):
    """
    Register new user
    
    - **name**: User's full name
    - **email**: User's email (unique)
    - **password**: Password (min 8 characters)
    - **confirm_password**: Password confirmation
    - **broker**: Broker name (angelone, zerodha, dhan)
    - **broker_api_key**: Broker API key (required for AngelOne)
    """
    # Validate passwords match
    if data.password != data.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Passwords do not match"
        )
    
    # Validate password length
    if len(data.password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters"
        )
    
    # Check if user already exists
    existing_user = get_user_by_email(data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Validate broker-specific requirements
    if data.broker == "angelone" and not data.broker_api_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="API Key is required for AngelOne broker"
        )
    
    # Create user
    user = add_user(
        name=data.name,
        email=data.email,
        password=data.password,
        broker=data.broker,
        broker_api_key=data.broker_api_key
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user"
        )
    
    return RegisterResponse(
        status="success",
        message="Registration successful. Please login.",
        user_id=user.id
    )


@router.post("/login", response_model=LoginResponse)
async def login(data: LoginRequest):
    """
    Login user with broker credentials
    
    - **broker**: Broker name (angelone)
    - **client_id**: Broker client ID
    - **pin**: Broker PIN/password
    - **totp**: 6-digit TOTP code
    - **email**: Optional - if not provided, will find user by broker and client_id
    """
    # Find user - either by email or by broker + client_id
    if data.email:
        user = get_user_by_email(data.email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or broker credentials"
            )
        
        # Verify broker matches
        if user.broker != data.broker:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"User is registered with {user.broker}, not {data.broker}"
            )
    else:
        # Find user by broker (assuming one user per broker for now)
        # In production, you'd need to match by client_id stored in database
        from database.user_db import get_user_by_broker
        user = get_user_by_broker(data.broker)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"No user found for broker {data.broker}. Please register first."
            )
    
    # Authenticate with broker
    if data.broker == "angelone":
        # Get broker API key from user's database record
        broker_api_key = user.broker_api_key
        if not broker_api_key:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Broker API key not found. Please contact support."
            )
        
        auth_token, feed_token, error = authenticate_broker(
            clientcode=data.client_id,
            broker_pin=data.pin,
            totp_code=data.totp,
            api_key=broker_api_key
        )
        
        if error:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Broker authentication failed: {error}"
            )
        
        # Store broker auth tokens (auth_token + feed_token like OpenAlgo)
        upsert_broker_auth(
            user_id=user.id,
            broker=data.broker,
            broker_user_id=data.client_id,  # Broker's client ID
            auth_token=auth_token,
            feed_token=feed_token  # AngelOne provides feed_token for WebSocket
        )
        
        # Initialize master contract status for this broker
        init_broker_status(data.broker)
        
        # Start master contract download in background thread
        logger.info(f"Starting master contract download for {data.broker}")
        thread = Thread(target=async_master_contract_download, args=(data.broker,), daemon=True)
        thread.start()
        
        return LoginResponse(
            status="success",
            message="Login successful",
            user=user.to_dict() if hasattr(user, 'to_dict') else {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "broker": user.broker
            },
            auth_token=auth_token,
            feed_token=feed_token  # Return feed_token to frontend
        )
    
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Broker {data.broker} not yet supported"
        )


def async_master_contract_download(broker: str):
    """
    Background task to download master contract for the broker
    Updates status in database during download
    """
    try:
        logger.info(f"Master contract download started for {broker}")
        update_status(broker, "downloading", "Downloading master contract...")
        
        # Call the broker-specific download function
        if broker == "angelone":
            master_contract_download()
            
        # Update status to success
        update_status(broker, "success", "Master contract downloaded successfully")
        logger.info(f"Master contract download completed for {broker}")
        
    except Exception as e:
        logger.error(f"Master contract download failed for {broker}: {str(e)}")
        update_status(broker, "error", f"Download failed: {str(e)}")



@router.post("/logout")
async def logout(user_id: int):
    """Logout user and revoke tokens"""
    # TODO: Implement session management and token revocation
    return {"status": "success", "message": "Logged out successfully"}


@router.get("/brokers")
async def get_brokers():
    """Get list of supported brokers"""
    return {
        "brokers": [
            {
                "id": "angelone",
                "name": "AngelOne",
                "status": "active",
                "requires_api_key": True
            },
            {
                "id": "zerodha",
                "name": "Zerodha",
                "status": "coming_soon",
                "requires_api_key": True
            },
            {
                "id": "dhan",
                "name": "Dhan",
                "status": "coming_soon",
                "requires_api_key": True
            }
        ]
    }
