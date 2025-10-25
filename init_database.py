#!/usr/bin/env python3
"""
Database initialization script for Classroom Assistant Backend
This script creates all necessary tables in the Neon PostgreSQL database
"""

import os
import sys
from dotenv import load_dotenv
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
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

def init_database():
    """Initialize the database with all tables"""
    print("Initializing Classroom Assistant Database...")
    print("=" * 50)
    
    # Create Flask app
    app = create_app()
    
    # Initialize SQLAlchemy
    db = SQLAlchemy(app)
    
    # Import models to register them with SQLAlchemy
    from models import User, Lecture, Task, Notification
    
    try:
        with app.app_context():
            print("Creating database tables...")
            
            # Create all tables
            db.create_all()
            
            print("✅ Database tables created successfully!")
            print("\nCreated tables:")
            print("- users")
            print("- lectures") 
            print("- tasks")
            print("- notifications")
            
            # Test database connection
            print("\nTesting database connection...")
            user_count = User.query.count()
            print(f"✅ Database connection successful! (Users: {user_count})")
            
            return True
            
    except Exception as e:
        print(f"❌ Error creating database tables: {str(e)}")
        return False

def create_sample_data():
    """Create sample data for testing"""
    print("\nCreating sample data...")
    
    app = create_app()
    db = SQLAlchemy(app)
    
    from models import User, Lecture, Task, Notification, UserRole, TaskStatus, TaskPriority, NotificationType
    
    try:
        with app.app_context():
            # Check if data already exists
            if User.query.count() > 0:
                print("Sample data already exists. Skipping...")
                return True
            
            # Create sample teacher
            teacher = User(
                email="professor@university.edu",
                name="Dr. Sarah Johnson",
                role=UserRole.TEACHER,
                department="Computer Science",
                bio="Professor of Artificial Intelligence and Machine Learning",
                phone="+1-555-0123"
            )
            db.session.add(teacher)
            
            # Create sample student
            student = User(
                email="student@university.edu",
                name="Alex Smith",
                role=UserRole.STUDENT,
                student_id="STU001",
                major="Computer Science",
                year="Junior",
                bio="Computer Science student interested in AI",
                phone="+1-555-0456"
            )
            db.session.add(student)
            
            db.session.commit()
            
            # Create sample lecture
            lecture = Lecture(
                title="Introduction to Machine Learning",
                subject="Artificial Intelligence",
                teacher_id=teacher.id,
                transcript="Welcome to Introduction to Machine Learning. Today we'll cover the basics of supervised learning, including linear regression and classification algorithms...",
                summary="This lecture introduces the fundamental concepts of machine learning, covering supervised learning techniques and their applications.",
                key_points=[
                    "Supervised learning uses labeled training data",
                    "Linear regression predicts continuous values",
                    "Classification algorithms categorize data into classes",
                    "Feature selection is crucial for model performance"
                ],
                tags=["machine-learning", "supervised-learning", "regression", "classification"],
                is_processed=True
            )
            db.session.add(lecture)
            
            # Create sample tasks
            task1 = Task(
                title="Complete Linear Regression Assignment",
                description="Implement linear regression from scratch using Python. Submit code and results analysis.",
                lecture_id=lecture.id,
                assigned_to_id=student.id,
                status=TaskStatus.PENDING,
                priority=TaskPriority.HIGH,
                is_ai_generated=True
            )
            db.session.add(task1)
            
            task2 = Task(
                title="Read Chapter 3: Classification",
                description="Read and summarize the key concepts from Chapter 3 of the textbook.",
                lecture_id=lecture.id,
                assigned_to_id=student.id,
                status=TaskStatus.PENDING,
                priority=TaskPriority.MEDIUM,
                is_ai_generated=True
            )
            db.session.add(task2)
            
            # Create sample notifications
            notification1 = Notification(
                user_id=student.id,
                type=NotificationType.TASK_ASSIGNED,
                title="New Assignment: Linear Regression",
                message="You have been assigned a new task: Complete Linear Regression Assignment",
                data={"task_id": task1.id, "due_date": "2024-12-15"}
            )
            db.session.add(notification1)
            
            notification2 = Notification(
                user_id=teacher.id,
                type=NotificationType.LECTURE_UPLOADED,
                title="Lecture Processed",
                message="Your lecture 'Introduction to Machine Learning' has been processed and tasks extracted.",
                data={"lecture_id": lecture.id}
            )
            db.session.add(notification2)
            
            db.session.commit()
            
            print("✅ Sample data created successfully!")
            print(f"   - Created 1 teacher: {teacher.name}")
            print(f"   - Created 1 student: {student.name}")
            print(f"   - Created 1 lecture: {lecture.title}")
            print(f"   - Created 2 tasks")
            print(f"   - Created 2 notifications")
            
            return True
            
    except Exception as e:
        print(f"❌ Error creating sample data: {str(e)}")
        db.session.rollback()
        return False

def main():
    """Main function to initialize the database"""
    print("🚀 Classroom Assistant Database Setup")
    print("=" * 50)
    
    # Check if DATABASE_URL is set
    database_url = os.getenv('DATABASE_URL')
    if not database_url or database_url == 'sqlite:///classroom_assistant.db':
        print("⚠️  DATABASE_URL not set or using SQLite")
        print("Please set your Neon PostgreSQL DATABASE_URL in the .env file")
        print("Example: DATABASE_URL=postgresql://username:password@host:port/database_name")
        print("\nContinuing with SQLite for local development...")
    
    # Initialize database
    if not init_database():
        print("\n❌ Database initialization failed!")
        sys.exit(1)
    
    # Create sample data
    create_sample_data()
    
    print("\n" + "=" * 50)
    print("🎉 Database setup completed successfully!")
    print("\nNext steps:")
    print("1. Set up your environment variables in .env file")
    print("2. Run: python app.py")
    print("3. Test the API endpoints")
    print("4. Connect your frontend to the backend")

if __name__ == '__main__':
    main()
