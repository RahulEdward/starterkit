"""
Migration script to add broker column to symtoken table
Run this once to update the database schema
"""
import os
import sys

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.symbol import engine, Base, SymToken
from sqlalchemy import inspect
from utils.logging import get_logger

logger = get_logger(__name__)


def check_broker_column_exists():
    """Check if broker column already exists"""
    inspector = inspect(engine)
    columns = [col['name'] for col in inspector.get_columns('symtoken')]
    return 'broker' in columns


def migrate():
    """Add broker column to symtoken table"""
    try:
        # Check if column already exists
        if check_broker_column_exists():
            logger.info("Broker column already exists in symtoken table")
            return True
        
        logger.info("Adding broker column to symtoken table...")
        
        # For SQLite, we need to recreate the table
        # The easiest way is to drop and recreate
        logger.warning("This will delete all existing symbols. They will be re-downloaded on next login.")
        
        # Drop the table
        SymToken.__table__.drop(engine, checkfirst=True)
        logger.info("Dropped old symtoken table")
        
        # Recreate with new schema
        Base.metadata.create_all(engine)
        logger.info("Created new symtoken table with broker column")
        
        logger.info("Migration completed successfully!")
        logger.info("Please login with each broker to re-download master contracts")
        
        return True
        
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("MIGRATION: Add broker column to symtoken table")
    print("=" * 60)
    print()
    print("This migration will:")
    print("1. Drop the existing symtoken table")
    print("2. Recreate it with the new broker column")
    print("3. All symbols will be deleted and need to be re-downloaded")
    print()
    
    response = input("Do you want to continue? (yes/no): ")
    
    if response.lower() in ['yes', 'y']:
        if migrate():
            print("\n✓ Migration completed successfully!")
            print("Please restart the application and login with each broker.")
        else:
            print("\n✗ Migration failed. Check logs for details.")
            sys.exit(1)
    else:
        print("\nMigration cancelled.")
        sys.exit(0)
