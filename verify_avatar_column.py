"""
Verification script to check if avatar_url column exists
"""

import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

def verify_avatar_column():
    """Verify avatar_url column exists in users table"""
    
    database_url = os.getenv('DATABASE_URL')
    
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    
    engine = create_engine(database_url)
    
    with engine.connect() as conn:
        # Get column information
        query = text("""
            SELECT 
                column_name, 
                data_type, 
                character_maximum_length,
                is_nullable
            FROM information_schema.columns 
            WHERE table_name='users' 
            ORDER BY ordinal_position
        """)
        
        result = conn.execute(query)
        columns = result.fetchall()
        
        print("\n" + "=" * 80)
        print("USERS TABLE SCHEMA")
        print("=" * 80)
        print(f"{'Column Name':<30} {'Data Type':<20} {'Max Length':<12} {'Nullable'}")
        print("-" * 80)
        
        avatar_found = False
        for col in columns:
            col_name, data_type, max_length, nullable = col
            max_len_str = str(max_length) if max_length else 'N/A'
            print(f"{col_name:<30} {data_type:<20} {max_len_str:<12} {nullable}")
            
            if col_name == 'avatar_url':
                avatar_found = True
        
        print("=" * 80)
        
        if avatar_found:
            print("\n✓ SUCCESS: avatar_url column exists in users table")
        else:
            print("\n✗ ERROR: avatar_url column NOT found in users table")
            print("  Run: python add_avatar_url_column.py")
        
        print()

if __name__ == '__main__':
    verify_avatar_column()
