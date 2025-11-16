"""
Migration script to add avatar_url column to users table
Run this script to update the database schema
"""

import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def add_avatar_url_column():
    """Add avatar_url column to users table"""
    
    # Get database URL
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        print("ERROR: DATABASE_URL not found in environment variables")
        sys.exit(1)
    
    # Fix postgres:// to postgresql:// for SQLAlchemy
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    
    print(f"Connecting to database...")
    
    try:
        # Create engine
        engine = create_engine(database_url)
        
        # Connect and execute migration
        with engine.connect() as conn:
            # Check if column already exists
            check_query = text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='users' AND column_name='avatar_url'
            """)
            
            result = conn.execute(check_query)
            exists = result.fetchone()
            
            if exists:
                print("✓ Column 'avatar_url' already exists in users table")
                return
            
            # Add the column
            print("Adding 'avatar_url' column to users table...")
            
            alter_query = text("""
                ALTER TABLE users 
                ADD COLUMN avatar_url VARCHAR(500)
            """)
            
            conn.execute(alter_query)
            conn.commit()
            
            print("✓ Successfully added 'avatar_url' column to users table")
            print("✓ Migration completed successfully!")
            
    except Exception as e:
        print(f"ERROR: Migration failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    print("=" * 60)
    print("Database Migration: Add avatar_url column")
    print("=" * 60)
    add_avatar_url_column()
    print("=" * 60)
