"""
Database Initialization Script
"""
from collections.models import Base
from db.connection import engine

def init_database():
    """Create all database tables"""
    Base.metadata.create_all(bind=engine)
    print("Database initialized successfully")

if __name__ == "__main__":
    init_database()
