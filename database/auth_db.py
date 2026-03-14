"""
Authentication Token Database
Stores broker authentication tokens and session data
"""
import os
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.pool import NullPool

# Database connection
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./best_option.db")

# Engine setup
if "sqlite" in DATABASE_URL:
    engine = create_engine(
        DATABASE_URL,
        poolclass=NullPool,
        connect_args={"check_same_thread": False}
    )
else:
    engine = create_engine(
        DATABASE_URL,
        pool_size=50,
        max_overflow=100,
        pool_timeout=10
    )

db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()


class BrokerAuth(Base):
    """Broker authentication tokens"""
    __tablename__ = "broker_auth"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, index=True)  # Our internal user ID
    broker = Column(String(50), nullable=False)
    broker_user_id = Column(String(100), nullable=True)  # Broker's client ID/user ID
    auth_token = Column(Text, nullable=True)  # JWT token from broker
    feed_token = Column(Text, nullable=True)  # Feed token for WebSocket streaming
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


def init_db():
    """Initialize auth database"""
    Base.metadata.create_all(bind=engine)
    print("Auth database initialized successfully")


def upsert_broker_auth(user_id: int, broker: str, broker_user_id: str, 
                       auth_token: str, feed_token: str = None):
    """
    Store or update broker authentication tokens
    
    Args:
        user_id: Our internal user ID
        broker: Broker name (angelone, zerodha, etc.)
        broker_user_id: Broker's client ID/user ID
        auth_token: JWT token from broker
        feed_token: Feed token for WebSocket (optional, AngelOne provides this)
    """
    auth_obj = BrokerAuth.query.filter_by(user_id=user_id, broker=broker).first()
    
    if auth_obj:
        auth_obj.broker_user_id = broker_user_id
        auth_obj.auth_token = auth_token
        auth_obj.feed_token = feed_token
        auth_obj.is_active = True
        auth_obj.updated_at = datetime.utcnow()
    else:
        auth_obj = BrokerAuth(
            user_id=user_id,
            broker=broker,
            broker_user_id=broker_user_id,
            auth_token=auth_token,
            feed_token=feed_token
        )
        db_session.add(auth_obj)
    
    db_session.commit()
    return auth_obj


def get_broker_auth(user_id: int, broker: str):
    """Get broker authentication tokens"""
    return BrokerAuth.query.filter_by(
        user_id=user_id, 
        broker=broker, 
        is_active=True
    ).first()


def revoke_broker_auth(user_id: int, broker: str):
    """Revoke broker authentication"""
    auth_obj = BrokerAuth.query.filter_by(user_id=user_id, broker=broker).first()
    if auth_obj:
        auth_obj.is_active = False
        db_session.commit()
        return True
    return False
