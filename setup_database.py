#!/usr/bin/env python3
"""
Comprehensive database setup script for Classroom Assistant Backend
This script handles complete database setup including table creation and sample data
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

def setup_database():
    """Complete database setup"""
    print("Setting up Classroom Assistant Database...")
    print("=" * 50)
    
    # Create Flask app
    app = create_app()
    
    # Initialize SQLAlchemy
    db = SQLAlchemy(app)
    migrate = Migrate(app, db)
    
    # Import models to register them with SQLAlchemy
    from models import User, Lecture, Task, Notification, UserRole, TaskStatus, TaskPriority, NotificationType
    
    # Initialize models with the db instance
    User.__init__ = lambda self, **kwargs: db.Model.__init__(self, **kwargs)
    Lecture.__init__ = lambda self, **kwargs: db.Model.__init__(self, **kwargs)
    Task.__init__ = lambda self, **kwargs: db.Model.__init__(self, **kwargs)
    Notification.__init__ = lambda self, **kwargs: db.Model.__init__(self, **kwargs)
    
    try:
        with app.app_context():
            print("Step 1: Creating database tables...")
            
            # Create all tables
            db.create_all()
            
            print("Database tables created successfully!")
            print("\nCreated tables:")
            print("- users (id, email, name, role, student_id, major, year, department, bio, phone, notifications_enabled, email_notifications, dark_mode, created_at, updated_at)")
            print("- lectures (id, title, subject, teacher_id, audio_url, audio_duration, transcript, summary, key_points, tags, is_processed, created_at, updated_at)")
            print("- tasks (id, title, description, lecture_id, assigned_to_id, status, priority, due_date, is_ai_generated, created_at, updated_at)")
            print("- notifications (id, user_id, type, title, message, data, is_read, created_at)")
            
            # Test database connection
            print("\nStep 2: Testing database connection...")
            user_count = User.query.count()
            print(f"Database connection successful! (Current users: {user_count})")
            
            # Check if sample data exists
            if user_count == 0:
                print("\nStep 3: Creating sample data...")
                create_sample_data(db, User, Lecture, Task, Notification, UserRole, TaskStatus, TaskPriority, NotificationType)
            else:
                print("\nStep 3: Sample data already exists. Skipping...")
            
            print("\n" + "=" * 50)
            print("Database setup completed successfully!")
            print("\nDatabase is ready for use with:")
            print("All tables created")
            print("Sample data inserted")
            print("Database connection verified")
            
            return True
            
    except Exception as e:
        print(f"Error setting up database: {str(e)}")
        return False

def create_sample_data(db, User, Lecture, Task, Notification, UserRole, TaskStatus, TaskPriority, NotificationType):
    """Create sample data for testing"""
    try:
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
            transcript="Welcome to Introduction to Machine Learning. Today we'll cover the basics of supervised learning, including linear regression and classification algorithms. We'll start with understanding what machine learning is and how it differs from traditional programming approaches.",
            summary="This lecture introduces the fundamental concepts of machine learning, covering supervised learning techniques and their applications in real-world scenarios.",
            key_points=[
                "Supervised learning uses labeled training data",
                "Linear regression predicts continuous values",
                "Classification algorithms categorize data into classes",
                "Feature selection is crucial for model performance",
                "Cross-validation helps prevent overfitting"
            ],
            tags=["machine-learning", "supervised-learning", "regression", "classification"],
            is_processed=True
        )
        db.session.add(lecture)
        
        # Create sample tasks
        task1 = Task(
            title="Complete Linear Regression Assignment",
            description="Implement linear regression from scratch using Python. Submit code and results analysis. Include visualizations of your results.",
            lecture_id=lecture.id,
            assigned_to_id=student.id,
            status=TaskStatus.PENDING,
            priority=TaskPriority.HIGH,
            is_ai_generated=True
        )
        db.session.add(task1)
        
        task2 = Task(
            title="Read Chapter 3: Classification",
            description="Read and summarize the key concepts from Chapter 3 of the textbook. Focus on decision trees and random forests.",
            lecture_id=lecture.id,
            assigned_to_id=student.id,
            status=TaskStatus.PENDING,
            priority=TaskPriority.MEDIUM,
            is_ai_generated=True
        )
        db.session.add(task2)
        
        task3 = Task(
            title="Implement Decision Tree Classifier",
            description="Create a decision tree classifier using scikit-learn. Test it on the provided dataset and submit your code.",
            lecture_id=lecture.id,
            assigned_to_id=student.id,
            status=TaskStatus.PENDING,
            priority=TaskPriority.HIGH,
            is_ai_generated=False
        )
        db.session.add(task3)
        
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
        
        notification3 = Notification(
            user_id=student.id,
            type=NotificationType.TASK_DUE,
            title="Assignment Due Soon",
            message="Your Linear Regression assignment is due in 2 days. Don't forget to submit it!",
            data={"task_id": task1.id, "due_date": "2024-12-15"}
        )
        db.session.add(notification3)
        
        db.session.commit()
        
        print("Sample data created successfully!")
        print(f"   - Created 1 teacher: {teacher.name} ({teacher.email})")
        print(f"   - Created 1 student: {student.name} ({student.email})")
        print(f"   - Created 1 lecture: {lecture.title}")
        print(f"   - Created 3 tasks")
        print(f"   - Created 3 notifications")
        
        return True
        
    except Exception as e:
        print(f"Error creating sample data: {str(e)}")
        db.session.rollback()
        return False

def test_database_operations():
    """Test basic database operations"""
    print("\nTesting database operations...")
    
    app = create_app()
    db = SQLAlchemy(app)
    
    from models import User, Lecture, Task, Notification
    
    try:
        with app.app_context():
            # Test queries
            users = User.query.all()
            lectures = Lecture.query.all()
            tasks = Task.query.all()
            notifications = Notification.query.all()
            
            print(f"Database operations successful!")
            print(f"   - Users: {len(users)}")
            print(f"   - Lectures: {len(lectures)}")
            print(f"   - Tasks: {len(tasks)}")
            print(f"   - Notifications: {len(notifications)}")
            
            # Test relationships
            if lectures:
                lecture = lectures[0]
                print(f"   - Lecture '{lecture.title}' has {len(lecture.tasks)} tasks")
            
            if users:
                teacher = next((u for u in users if u.role.value == 'teacher'), None)
                if teacher:
                    print(f"   - Teacher '{teacher.name}' has {len(teacher.lectures)} lectures")
            
            return True
            
    except Exception as e:
        print(f"Error testing database operations: {str(e)}")
        return False

def main():
    """Main function to set up the database"""
    print("Classroom Assistant Database Setup")
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
    
    # Setup database
    if not setup_database():
        print("\nDatabase setup failed!")
        sys.exit(1)
    
    # Test database operations
    if not test_database_operations():
        print("\nDatabase operations test failed!")
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("Database setup completed successfully!")
    print("\nNext steps:")
    print("1. Set up your environment variables in .env file")
    print("2. Run: python app.py")
    print("3. Test the API endpoints")
    print("4. Connect your frontend to the backend")
    print("\nAPI Endpoints available:")
    print("- GET  /api/health")
    print("- POST /api/auth/register")
    print("- GET  /api/lectures")
    print("- POST /api/tasks")
    print("- GET  /api/notifications")

if __name__ == '__main__':
    main()
