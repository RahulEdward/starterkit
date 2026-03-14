"""
Symbol Master Contract Database
Stores symbol mappings for all brokers
"""
import os
from sqlalchemy import Column, Float, Index, Integer, String, create_engine
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
Base.query = db_session.query_property()


class SymToken(Base):
    """Symbol master contract table"""
    __tablename__ = "symtoken"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    broker = Column(String(20), nullable=False, index=True)  # Broker name (angelone, fyers, etc.)
    symbol = Column(String(50), nullable=False, index=True)  # Best-Option format
    brsymbol = Column(String(50), nullable=False)  # Broker format
    name = Column(String(200))
    exchange = Column(String(20), nullable=False, index=True)
    brexchange = Column(String(20))  # Broker exchange code
    token = Column(String(50), nullable=False, index=True)
    expiry = Column(String(20))
    strike = Column(Float)
    lotsize = Column(Integer)
    instrumenttype = Column(String(10))
    tick_size = Column(Float)
    
    # Composite indexes for fast lookups
    __table_args__ = (
        Index('idx_broker_symbol_exchange', 'broker', 'symbol', 'exchange'),
        Index('idx_broker_token_exchange', 'broker', 'token', 'exchange'),
        Index('idx_broker_brsymbol_exchange', 'broker', 'brsymbol', 'exchange'),
        Index('idx_symbol_exchange', 'symbol', 'exchange'),
        Index('idx_token_exchange', 'token', 'exchange'),
        Index('idx_brsymbol_exchange', 'brsymbol', 'exchange'),
    )


def init_db():
    """Initialize symbol database"""
    Base.metadata.create_all(bind=engine)
    logger.info("Symbol database initialized successfully")


def get_symbol_count():
    """Get total count of symbols"""
    try:
        return SymToken.query.count()
    except Exception as e:
        logger.error(f"Error getting symbol count: {e}")
        return 0


def fno_search_symbols_db(query: str, exchange: str = None, limit: int = 50):
    """
    Search symbols in database
    
    Args:
        query: Search query
        exchange: Filter by exchange (optional)
        limit: Maximum results
    
    Returns:
        List of matching symbols
    """
    try:
        query_obj = SymToken.query.filter(SymToken.symbol.like(f"%{query}%"))
        
        if exchange:
            query_obj = query_obj.filter_by(exchange=exchange)
        
        results = query_obj.limit(limit).all()
        
        return [{
            'symbol': r.symbol,
            'name': r.name,
            'exchange': r.exchange,
            'token': r.token,
            'expiry': r.expiry,
            'strike': r.strike,
            'lotsize': r.lotsize
        } for r in results]
    except Exception as e:
        logger.error(f"Error searching symbols: {e}")
        return []


def get_distinct_expiries(exchange: str, underlying: str = None):
    """Get distinct expiry dates for an exchange/underlying"""
    try:
        query = db_session.query(SymToken.expiry).filter(
            SymToken.exchange == exchange,
            SymToken.expiry.isnot(None)
        ).distinct()
        
        if underlying:
            query = query.filter(SymToken.symbol.like(f"{underlying}%"))
        
        expiries = [r[0] for r in query.all() if r[0]]
        return sorted(expiries)
    except Exception as e:
        logger.error(f"Error getting expiries: {e}")
        return []


def get_distinct_underlyings(exchange: str):
    """Get distinct underlying symbols for an exchange"""
    try:
        # This is a simplified version - in production you'd extract underlyings properly
        symbols = db_session.query(SymToken.symbol).filter(
            SymToken.exchange == exchange
        ).distinct().limit(100).all()
        
        # Extract base symbols (simplified)
        underlyings = set()
        for s in symbols:
            # Extract underlying from symbol (basic logic)
            symbol = s[0]
            if symbol:
                # Take first alphabetic part
                import re
                match = re.match(r'^([A-Z]+)', symbol)
                if match:
                    underlyings.add(match.group(1))
        
        return sorted(list(underlyings))
    except Exception as e:
        logger.error(f"Error getting underlyings: {e}")
        return []
