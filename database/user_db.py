"""
User Database Management
Handles user registration and authentication
"""
import os
from datetime import datetime

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

import pyotp
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from sqlalchemy import Boolean, Column, DateTime, Integer, String, create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.pool import NullPool

# Initialize Argon2 hasher
ph = PasswordHasher()

# Database connection
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./best_option.db")

# Security: Password pepper
PASSWORD_PEPPER = os.getenv("API_KEY_PEPPER", "")
if not PASSWORD_PEPPER or len(PASSWORD_PEPPER) < 32:
    raise RuntimeError(
        "CRITICAL: API_KEY_PEPPER must be set in .env and be at least 32 characters. "
        'Generate one using: python -c "import secrets; print(secrets.token_hex(32))"'
    )

# Engine setup
if "sqlite" in DATABASE_URL:
    engine = create_engine(
        DATABASE_URL, 
        echo=False, 
        poolclass=NullPool, 
        connect_args={"check_same_thread": False}
    )
else:
    engine = create_engine(
        DATABASE_URL, 
        echo=False, 
        pool_size=50, 
        max_overflow=100, 
        pool_timeout=10
    )

db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()


class User(Base):
    """User model for authentication"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    email = Column(String(120), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    broker = Column(String(50), nullable=False)  # angelone, zerodha, dhan
    broker_api_key = Column(String(500), nullable=True)  # Broker API key
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def set_password(self, password: str):
        """Hash password using Argon2 with pepper"""
        peppered_password = password + PASSWORD_PEPPER
        self.password_hash = ph.hash(peppered_password)
    
    def check_password(self, password: str) -> bool:
        """Verify password using Argon2 with pepper"""
        peppered_password = password + PASSWORD_PEPPER
        try:
            ph.verify(self.password_hash, peppered_password)
            if ph.check_needs_rehash(self.password_hash):
                self.set_password(password)
                db_session.commit()
            return True
        except VerifyMismatchError:
            return False


def init_db():
    """Initialize user database"""
    Base.metadata.create_all(bind=engine)
    print("User database initialized successfully")


def add_user(name: str, email: str, password: str, broker: str, broker_api_key: str = None):
    """Add new user to database"""
    try:
        user = User(
            name=name,
            email=email,
            broker=broker,
            broker_api_key=broker_api_key
        )
        user.set_password(password)
        db_session.add(user)
        db_session.commit()
        return user
    except IntegrityError:
        db_session.rollback()
        return None


def authenticate_user(email: str, password: str):
    """Authenticate user with email and password"""
    user = User.query.filter_by(email=email, is_active=True).first()
    if user and user.check_password(password):
        return user
    return None


def get_user_by_email(email: str):
    """Get user by email"""
    return User.query.filter_by(email=email).first()


def get_user_by_id(user_id: int):
    """Get user by ID"""
    return User.query.filter_by(id=user_id).first()


def get_user_by_broker(broker: str):
    """Get first user by broker (for single-user-per-broker setup)"""
    return User.query.filter_by(broker=broker, is_active=True).first()
