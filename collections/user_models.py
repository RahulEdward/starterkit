"""
User and Authentication Database Models
"""
import os
from datetime import datetime

import pyotp
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
ph = PasswordHasher()

# Security: Password pepper from environment
PASSWORD_PEPPER = os.getenv("API_KEY_PEPPER", "")
if not PASSWORD_PEPPER or len(PASSWORD_PEPPER) < 32:
    raise RuntimeError(
        "CRITICAL: API_KEY_PEPPER must be set in .env and be at least 32 characters. "
        'Generate one using: python -c "import secrets; print(secrets.token_hex(32))"'
    )


class User(Base):
    """User account model"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    email = Column(String(120), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    broker = Column(String(50), nullable=False)  # angelone, zerodha, dhan, etc.
    broker_api_key = Column(Text, nullable=True)  # Encrypted broker API key
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Broker authentication tokens (encrypted)
    auth_token = Column(Text, nullable=True)  # JWT token from broker
    feed_token = Column(Text, nullable=True)  # Feed token for WebSocket
    client_id = Column(String(100), nullable=True)  # Broker client ID
    
    # Session management
    last_login = Column(DateTime, nullable=True)
    is_logged_in = Column(Boolean, default=False)
    
    def set_password(self, password: str):
        """Hash password using Argon2 with pepper"""
        peppered_password = password + PASSWORD_PEPPER
        self.password_hash = ph.hash(peppered_password)
    
    def check_password(self, password: str) -> bool:
        """Verify password using Argon2 with pepper"""
        peppered_password = password + PASSWORD_PEPPER
        try:
            ph.verify(self.password_hash, peppered_password)
            # Check if hash needs rehashing
            if ph.check_needs_rehash(self.password_hash):
                self.set_password(password)
            return True
        except VerifyMismatchError:
            return False
    
    def to_dict(self):
        """Convert user to dictionary (exclude sensitive data)"""
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "broker": self.broker,
            "is_active": self.is_active,
            "is_logged_in": self.is_logged_in,
            "last_login": self.last_login.isoformat() if self.last_login else None,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
