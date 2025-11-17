#!/usr/bin/env python3
"""
Add document columns to chat_messages table
"""

import os
import sys
from sqlalchemy import create_engine, text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def add_document_columns():
    """Add document-related columns to chat_messages table"""
    
    # Get database URL from environment
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        logger.error("DATABASE_URL environment variable not set")
        return False
    
    try:
        # Create engine
        engine = create_engine(database_url)
        
        with engine.connect() as conn:
            logger.info("Connected to database")
            
            # Add document columns
            logger.info("Adding document columns to chat_messages table...")
            
            # Check if columns already exist
            check_query = text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'chat_messages' 
                AND column_name IN ('document_url', 'document_name', 'document_size', 'document_type')
            """)
            
            result = conn.execute(check_query)
            existing_columns = [row[0] for row in result]
            
            if len(existing_columns) == 4:
                logger.info("✓ Document columns already exist")
                return True
            
            # Add columns if they don't exist
            if 'document_url' not in existing_columns:
                conn.execute(text("ALTER TABLE chat_messages ADD COLUMN document_url VARCHAR(500)"))
                logger.info("✓ Added document_url column")
            
            if 'document_name' not in existing_columns:
                conn.execute(text("ALTER TABLE chat_messages ADD COLUMN document_name VARCHAR(255)"))
                logger.info("✓ Added document_name column")
            
            if 'document_size' not in existing_columns:
                conn.execute(text("ALTER TABLE chat_messages ADD COLUMN document_size INTEGER"))
                logger.info("✓ Added document_size column")
            
            if 'document_type' not in existing_columns:
                conn.execute(text("ALTER TABLE chat_messages ADD COLUMN document_type VARCHAR(100)"))
                logger.info("✓ Added document_type column")
            
            # Create index for documents
            try:
                conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_chat_messages_document 
                    ON chat_messages(document_url) 
                    WHERE document_url IS NOT NULL
                """))
                logger.info("✓ Created index on document_url")
            except Exception as e:
                logger.warning(f"Could not create index: {str(e)}")
            
            conn.commit()
            logger.info("✓ Migration completed successfully")
            return True
            
    except Exception as e:
        logger.error(f"Migration failed: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False

if __name__ == '__main__':
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    success = add_document_columns()
    sys.exit(0 if success else 1)
