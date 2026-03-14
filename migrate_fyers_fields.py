"""
Database Migration Script
Adds Fyers-specific fields to users table
"""
import os
import sqlite3

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./best_option.db")

def migrate_database():
    """Add new columns to users table for Fyers support"""
    
    # Extract database path from URL
    db_path = DATABASE_URL.replace("sqlite:///", "").replace("sqlite://", "")
    
    print(f"Migrating database: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(users)")
        columns = [col[1] for col in cursor.fetchall()]
        
        migrations = []
        
        # Add broker_api_secret column if it doesn't exist
        if 'broker_api_secret' not in columns:
            cursor.execute("ALTER TABLE users ADD COLUMN broker_api_secret VARCHAR(500)")
            migrations.append("broker_api_secret")
            print("✅ Added column: broker_api_secret")
        else:
            print("⏭️  Column already exists: broker_api_secret")
        
        # Add redirect_url column if it doesn't exist
        if 'redirect_url' not in columns:
            cursor.execute("ALTER TABLE users ADD COLUMN redirect_url VARCHAR(500)")
            migrations.append("redirect_url")
            print("✅ Added column: redirect_url")
        else:
            print("⏭️  Column already exists: redirect_url")
        
        conn.commit()
        
        if migrations:
            print(f"\n✅ Migration completed successfully! Added {len(migrations)} column(s).")
        else:
            print("\n✅ Database is already up to date. No migration needed.")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        raise

if __name__ == "__main__":
    print("=" * 60)
    print("Fyers Fields Migration")
    print("=" * 60)
    migrate_database()
