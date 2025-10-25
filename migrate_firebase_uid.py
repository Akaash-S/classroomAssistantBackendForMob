#!/usr/bin/env python3
"""
Migration script to add firebase_uid column to users table
Run this script to update the existing database schema
"""

import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def migrate_database():
    """Add firebase_uid column to users table"""
    try:
        # Get database URL from environment
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            print("Error: DATABASE_URL not found in environment variables")
            return False
        
        # Create database engine
        engine = create_engine(database_url)
        
        with engine.connect() as conn:
            # Check if firebase_uid column already exists
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='users' AND column_name='firebase_uid'
            """))
            
            if result.fetchone():
                print("firebase_uid column already exists. Migration not needed.")
                return True
            
            # Add firebase_uid column
            print("Adding firebase_uid column to users table...")
            conn.execute(text("""
                ALTER TABLE users 
                ADD COLUMN firebase_uid VARCHAR(128) UNIQUE
            """))
            
            # Create index for firebase_uid
            print("Creating index for firebase_uid...")
            conn.execute(text("""
                CREATE INDEX idx_users_firebase_uid ON users(firebase_uid)
            """))
            
            conn.commit()
            print("Migration completed successfully!")
            return True
            
    except Exception as e:
        print(f"Migration failed: {str(e)}")
        return False

if __name__ == '__main__':
    print("Starting Firebase UID migration...")
    if migrate_database():
        print("Migration completed successfully!")
        sys.exit(0)
    else:
        print("Migration failed!")
        sys.exit(1)
