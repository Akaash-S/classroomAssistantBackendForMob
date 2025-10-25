#!/usr/bin/env python3
"""
Database migration script for Classroom Assistant Backend
This script handles database migrations using Flask-Migrate
"""

import os
import sys
from dotenv import load_dotenv
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, init, migrate, upgrade
from config import config

# Load environment variables
load_dotenv()

def create_app():
    """Create Flask app with database configuration"""
    app = Flask(__name__)
    
    # Configuration
    config_name = os.getenv('FLASK_ENV', 'development')
    app.config.from_object(config[config_name])
    
    return app

def init_migrations():
    """Initialize Flask-Migrate"""
    print("Initializing Flask-Migrate...")
    
    app = create_app()
    db = SQLAlchemy(app)
    migrate = Migrate(app, db)
    
    with app.app_context():
        try:
            init()
            print("✅ Flask-Migrate initialized successfully!")
            return True
        except Exception as e:
            print(f"❌ Error initializing Flask-Migrate: {str(e)}")
            return False

def create_migration(message="Initial migration"):
    """Create a new migration"""
    print(f"Creating migration: {message}")
    
    app = create_app()
    db = SQLAlchemy(app)
    migrate = Migrate(app, db)
    
    # Import models to register them
    from models import User, Lecture, Task, Notification
    
    with app.app_context():
        try:
            migrate(message=message)
            print("✅ Migration created successfully!")
            return True
        except Exception as e:
            print(f"❌ Error creating migration: {str(e)}")
            return False

def apply_migrations():
    """Apply all pending migrations"""
    print("Applying migrations...")
    
    app = create_app()
    db = SQLAlchemy(app)
    migrate = Migrate(app, db)
    
    with app.app_context():
        try:
            upgrade()
            print("✅ Migrations applied successfully!")
            return True
        except Exception as e:
            print(f"❌ Error applying migrations: {str(e)}")
            return False

def main():
    """Main function to handle database migrations"""
    print("Database Migration Tool")
    print("=" * 30)
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python migrate_db.py init          - Initialize Flask-Migrate")
        print("  python migrate_db.py create <msg>  - Create new migration")
        print("  python migrate_db.py upgrade       - Apply migrations")
        print("  python migrate_db.py all <msg>     - Create and apply migration")
        return
    
    command = sys.argv[1]
    
    if command == "init":
        init_migrations()
    elif command == "create":
        message = sys.argv[2] if len(sys.argv) > 2 else "Auto-generated migration"
        create_migration(message)
    elif command == "upgrade":
        apply_migrations()
    elif command == "all":
        message = sys.argv[2] if len(sys.argv) > 2 else "Auto-generated migration"
        if create_migration(message):
            apply_migrations()
    else:
        print(f"Unknown command: {command}")

if __name__ == '__main__':
    main()
