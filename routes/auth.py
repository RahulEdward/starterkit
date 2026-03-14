"""
Authentication Routes
User registration and login endpoints
"""
import asyncio
import os
from threading import Thread

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr

from broker.angelone.api.auth_api import authenticate_broker as authenticate_angelone
from broker.angelone.database.master_contract_db import master_contract_download as angelone_master_contract_download
from broker.fyers.api.auth_api import authenticate_broker as authenticate_fyers
from broker.fyers.database.master_contract_db import master_contract_download as fyers_master_contract_download
from database.auth_db import upsert_broker_auth
from database.master_contract_status_db import init_broker_status, update_status
from database.user_db import add_user, authenticate_user, get_user_by_email, get_user_by_broker
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
    broker_api_key: str = None  # For AngelOne and Fyers App ID
    broker_api_secret: str = None  # For Fyers Secret ID
    redirect_url: str = None  # For Fyers OAuth redirect  # For AngelOne and Fyers App ID
    broker_api_secret: str = None  # For Fyers Secret ID
    redirect_url: str = None  # For Fyers OAuth redirect


class RegisterResponse(BaseModel):
    status: str
    message: str
    user_id: int = None


class LoginRequest(BaseModel):
    broker: str
    client_id: str = None  # Required for AngelOne
    pin: str = None  # Required for AngelOne
    totp: str = None  # Required for AngelOne
    request_token: str = None  # Required for Fyers OAuth flow
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
    
    if data.broker == "fyers":
        if not data.broker_api_key:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="App ID (API Key) is required for Fyers broker"
            )
        if not data.broker_api_secret:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Secret ID (API Secret) is required for Fyers broker"
            )
        if not data.redirect_url:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Redirect URL is required for Fyers broker"
            )
    
    if data.broker == "fyers":
        if not data.broker_api_key:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="App ID is required for Fyers broker"
            )
        if not data.broker_api_secret:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Secret ID is required for Fyers broker"
            )
        if not data.redirect_url:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Redirect URL is required for Fyers broker"
            )
    
    # Create user
    user = add_user(
        name=data.name,
        email=data.email,
        password=data.password,
        broker=data.broker,
        broker_api_key=data.broker_api_key,
        broker_api_secret=data.broker_api_secret,
        redirect_url=data.redirect_url
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
        # Validate required fields for AngelOne
        if not data.client_id or not data.pin or not data.totp:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="client_id, pin, and totp are required for AngelOne"
            )
        
        # Get broker API key from user's database record
        broker_api_key = user.broker_api_key
        if not broker_api_key:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Broker API key not found. Please contact support."
            )
        
        auth_token, feed_token, error = authenticate_angelone(
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
    
    elif data.broker == "fyers":
        # Validate required fields for Fyers
        if not data.request_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="request_token is required for Fyers OAuth flow"
            )
        
        # Get Fyers credentials from user's database record
        broker_api_key = user.broker_api_key  # App ID
        broker_api_secret = user.broker_api_secret  # Secret ID
        
        if not broker_api_key or not broker_api_secret:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Fyers credentials not found. Please register again."
            )
        
        # Authenticate with Fyers using request_token
        # Note: Fyers auth_api needs to be updated to accept api_key and api_secret as parameters
        access_token, response_data = authenticate_fyers(
            request_token=data.request_token,
            api_key=broker_api_key,
            api_secret=broker_api_secret
        )
        
        if not access_token:
            error_msg = response_data.get("message", "Authentication failed") if response_data else "Authentication failed"
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Fyers authentication failed: {error_msg}"
            )
        
        # Extract tokens from response
        refresh_token = response_data.get("data", {}).get("refresh_token")
        
        # Store broker auth tokens
        upsert_broker_auth(
            user_id=user.id,
            broker=data.broker,
            broker_user_id=user.email,  # Fyers uses email as user identifier
            auth_token=access_token,
            feed_token=refresh_token  # Store refresh_token as feed_token
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
            auth_token=access_token,
            feed_token=refresh_token
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
            angelone_master_contract_download()
        elif broker == "fyers":
            fyers_master_contract_download()
        else:
            raise ValueError(f"Master contract download not implemented for {broker}")
        
        # Count symbols for this broker
        from database.symbol import SymToken, db_session
        symbol_count = db_session.query(SymToken).filter_by(broker=broker).count()
        logger.info(f"Total symbols for {broker}: {symbol_count}")
        
        # Update status to success with symbol count
        update_status(broker, "success", "Master contract downloaded successfully", total_symbols=symbol_count)
        logger.info(f"Master contract download completed for {broker}")
        
        # Reload symbol cache after download
        logger.info(f"Reloading symbol cache for {broker}")
        from database.symbol_db import load_cache_for_broker
        if load_cache_for_broker(broker):
            logger.info(f"Symbol cache reloaded successfully for {broker}")
        else:
            logger.warning(f"Failed to reload symbol cache for {broker}")
        
    except Exception as e:
        logger.error(f"Master contract download failed for {broker}: {str(e)}")
        update_status(broker, "error", f"Download failed: {str(e)}")



@router.get("/user")
async def get_user_info(email: str = None, broker: str = None):
    """Get user information by email or broker"""
    if email:
        user = get_user_by_email(email)
    elif broker:
        user = get_user_by_broker(broker)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either email or broker must be provided"
        )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "broker": user.broker,
        "broker_api_key": user.broker_api_key,
        "redirect_url": user.redirect_url
    }


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
                "id": "fyers",
                "name": "Fyers",
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


@router.get("/user-by-broker")
async def get_user_by_broker_endpoint(broker: str):
    """Get user credentials by broker for OAuth flow"""
    from database.user_db import get_user_by_broker
    
    user = get_user_by_broker(broker)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No user found for broker {broker}"
        )
    
    return {
        "broker_api_key": user.broker_api_key,
        "broker_api_secret": user.broker_api_secret,
        "redirect_url": user.redirect_url
    }
