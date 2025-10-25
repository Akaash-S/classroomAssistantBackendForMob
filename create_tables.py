#!/usr/bin/env python3
"""
Simple database table creation script
This script creates all necessary tables in the database
"""

import os
import sys
from dotenv import load_dotenv
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
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

def create_tables():
    """Create all database tables"""
    print("Creating Classroom Assistant Database Tables...")
    print("=" * 50)
    
    # Create Flask app
    app = create_app()
    
    # Initialize SQLAlchemy
    db = SQLAlchemy(app)
    
    # Define models inline to avoid import issues
    class User(db.Model):
        __tablename__ = 'users'
        
        id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
        email = db.Column(db.String(120), unique=True, nullable=False, index=True)
        name = db.Column(db.String(100), nullable=False)
        role = db.Column(db.String(20), nullable=False)  # 'teacher' or 'student'
        student_id = db.Column(db.String(20), nullable=True)
        major = db.Column(db.String(100), nullable=True)
        year = db.Column(db.String(20), nullable=True)
        department = db.Column(db.String(100), nullable=True)
        bio = db.Column(db.Text, nullable=True)
        phone = db.Column(db.String(20), nullable=True)
        notifications_enabled = db.Column(db.Boolean, default=True)
        email_notifications = db.Column(db.Boolean, default=True)
        dark_mode = db.Column(db.Boolean, default=False)
        created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
        updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    
    class Lecture(db.Model):
        __tablename__ = 'lectures'
        
        id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
        title = db.Column(db.String(200), nullable=False)
        subject = db.Column(db.String(100), nullable=False)
        teacher_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
        audio_url = db.Column(db.String(500), nullable=True)
        audio_duration = db.Column(db.Integer, nullable=True)
        transcript = db.Column(db.Text, nullable=True)
        summary = db.Column(db.Text, nullable=True)
        key_points = db.Column(db.JSON, nullable=True)
        tags = db.Column(db.JSON, nullable=True)
        is_processed = db.Column(db.Boolean, default=False)
        created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
        updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    
    class Task(db.Model):
        __tablename__ = 'tasks'
        
        id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
        title = db.Column(db.String(200), nullable=False)
        description = db.Column(db.Text, nullable=False)
        lecture_id = db.Column(db.String(36), db.ForeignKey('lectures.id'), nullable=True)
        assigned_to_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=True)
        status = db.Column(db.String(20), default='pending')  # 'pending', 'completed', 'approved'
        priority = db.Column(db.String(20), default='medium')  # 'high', 'medium', 'low'
        due_date = db.Column(db.DateTime, nullable=True)
        is_ai_generated = db.Column(db.Boolean, default=False)
        created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
        updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    
    class Notification(db.Model):
        __tablename__ = 'notifications'
        
        id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
        user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
        type = db.Column(db.String(50), nullable=False)
        title = db.Column(db.String(200), nullable=False)
        message = db.Column(db.Text, nullable=False)
        data = db.Column(db.JSON, nullable=True)
        is_read = db.Column(db.Boolean, default=False)
        created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    
    try:
        with app.app_context():
            print("Creating database tables...")
            
            # Create all tables
            db.create_all()
            
            print("Database tables created successfully!")
            print("\nCreated tables:")
            print("- users")
            print("- lectures")
            print("- tasks")
            print("- notifications")
            
            # Test database connection
            print("\nTesting database connection...")
            user_count = User.query.count()
            print(f"Database connection successful! (Current users: {user_count})")
            
            return True
            
    except Exception as e:
        print(f"Error creating database tables: {str(e)}")
        return False

def main():
    """Main function to create tables"""
    print("Classroom Assistant Database Table Creation")
    print("=" * 50)
    
    # Check if DATABASE_URL is set
    database_url = os.getenv('DATABASE_URL')
    if not database_url or database_url == 'sqlite:///classroom_assistant.db':
        print("WARNING: DATABASE_URL not set or using SQLite")
        print("Please set your Neon PostgreSQL DATABASE_URL in the .env file")
        print("Example: DATABASE_URL=postgresql://username:password@host:port/database_name")
        print("\nContinuing with SQLite for local development...")
    else:
        print(f"Using database: {database_url[:50]}...")
    
    # Create tables
    if not create_tables():
        print("\nDatabase table creation failed!")
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("Database tables created successfully!")
    print("\nNext steps:")
    print("1. Run: python app.py")
    print("2. Test the API endpoints")
    print("3. Connect your frontend to the backend")

if __name__ == '__main__':
    import uuid
    main()
