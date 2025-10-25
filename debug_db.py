#!/usr/bin/env python3
"""
Debug script to test database connection and model
"""

import os
import sys
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Load environment variables
load_dotenv()

def test_database_connection():
    """Test database connection"""
    try:
        database_url = os.getenv('DATABASE_URL')
        print(f"Database URL: {database_url[:50]}...")
        
        engine = create_engine(database_url)
        
        with engine.connect() as conn:
            # Test basic connection
            result = conn.execute(text("SELECT 1"))
            print("Database connection successful")
            
            # Check if users table exists
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_name='users'
            """))
            
            if result.fetchone():
                print("Users table exists")
                
                # Check columns in users table
                result = conn.execute(text("""
                    SELECT column_name, data_type 
                    FROM information_schema.columns 
                    WHERE table_name='users'
                    ORDER BY ordinal_position
                """))
                
                print("Users table columns:")
                for row in result:
                    print(f"  {row[0]}: {row[1]}")
                    
            else:
                print("Users table does not exist")
                
    except Exception as e:
        print(f"Database connection failed: {str(e)}")

if __name__ == '__main__':
    test_database_connection()
