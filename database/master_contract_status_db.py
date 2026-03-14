"""
Master Contract Status Database
Tracks download status and readiness for each broker
"""
import json
import os
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.pool import NullPool

from utils.logging import get_logger

logger = get_logger(__name__)

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


class MasterContractStatus(Base):
    """Master contract download status per broker"""
    __tablename__ = "master_contract_status"
    
    broker = Column(String(50), primary_key=True)
    status = Column(String(20), default="pending")  # pending, downloading, success, error
    message = Column(String(500))
    last_updated = Column(DateTime, default=datetime.utcnow)
    total_symbols = Column(Integer, default=0)
    is_ready = Column(Boolean, default=False)
    
    # Smart download tracking
    last_download_time = Column(DateTime, nullable=True)
    exchange_stats = Column(Text, nullable=True)  # JSON: {"NSE": 2500, "NFO": 85000}
    download_duration_seconds = Column(Integer, nullable=True)


def init_db():
    """Initialize master contract status database"""
    try:
        # Try to create tables - will skip if they already exist
        from sqlalchemy import inspect
        inspector = inspect(engine)
        
        if not inspector.has_table("master_contract_status"):
            Base.metadata.create_all(bind=engine)
            logger.info("Master contract status database table created")
        else:
            logger.info("Master contract status database table already exists")
    except Exception as e:
        # If table exists, that's fine - just log and continue
        logger.info(f"Master contract status database initialization: {e}")


def init_broker_status(broker: str):
    """Initialize status for a broker when they login"""
    try:
        existing = db_session.query(MasterContractStatus).filter_by(broker=broker).first()
        
        if existing:
            existing.status = "pending"
            existing.message = "Master contract download pending"
            existing.last_updated = datetime.utcnow()
            existing.is_ready = False
        else:
            status = MasterContractStatus(
                broker=broker,
                status="pending",
                message="Master contract download pending"
            )
            db_session.add(status)
        
        db_session.commit()
        logger.info(f"Initialized master contract status for {broker}")
    except Exception as e:
        logger.error(f"Error initializing status for {broker}: {e}")
        db_session.rollback()


def update_status(broker: str, status: str, message: str, total_symbols: int = None):
    """Update the download status for a broker"""
    try:
        broker_status = db_session.query(MasterContractStatus).filter_by(broker=broker).first()
        
        if broker_status:
            broker_status.status = status
            broker_status.message = message
            broker_status.last_updated = datetime.utcnow()
            
            # If total_symbols not provided, count from database
            if total_symbols is None and status == "success":
                from database.symbol import SymToken
                total_symbols = SymToken.query.filter_by(broker=broker).count()
            
            if total_symbols is not None:
                broker_status.total_symbols = total_symbols
            
            if status == "success":
                broker_status.is_ready = True
                broker_status.last_download_time = datetime.utcnow()
            elif status == "error":
                broker_status.is_ready = False
            
            db_session.commit()
            logger.info(f"Updated status for {broker}: {status} ({total_symbols} symbols)")
        else:
            logger.warning(f"No status record found for {broker}")
    except Exception as e:
        logger.error(f"Error updating status for {broker}: {e}")
        db_session.rollback()


def get_status(broker: str) -> dict:
    """Get the current status for a broker"""
    try:
        broker_status = db_session.query(MasterContractStatus).filter_by(broker=broker).first()
        
        if broker_status:
            return {
                "broker": broker_status.broker,
                "status": broker_status.status,
                "message": broker_status.message,
                "total_symbols": broker_status.total_symbols,
                "is_ready": broker_status.is_ready,
                "last_updated": broker_status.last_updated.isoformat() if broker_status.last_updated else None
            }
        else:
            return {
                "broker": broker,
                "status": "unknown",
                "message": "No status available",
                "total_symbols": 0,
                "is_ready": False
            }
    except Exception as e:
        logger.error(f"Error getting status for {broker}: {e}")
        return {
            "broker": broker,
            "status": "error",
            "message": str(e),
            "total_symbols": 0,
            "is_ready": False
        }


def check_if_ready(broker: str) -> bool:
    """Check if master contracts are ready for a broker"""
    try:
        broker_status = db_session.query(MasterContractStatus).filter_by(broker=broker).first()
        return broker_status.is_ready if broker_status else False
    except Exception as e:
        logger.error(f"Error checking readiness for {broker}: {e}")
        return False
