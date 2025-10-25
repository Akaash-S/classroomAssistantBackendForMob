#!/usr/bin/env python3
"""
Database initialization script for Classroom Assistant Backend
"""

import os
import sys
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Import models to register them with SQLAlchemy
from models import User, Lecture, Task, Notification

def init_database():
    """Initialize the database with tables"""
    try:
        print("Creating database tables...")
        with app.app_context():
            db.create_all()
        print("✅ Database tables created successfully!")
        return True
    except Exception as e:
        print(f"❌ Error creating database tables: {str(e)}")
        return False

def create_sample_data():
    """Create sample data for testing"""
    try:
        print("Creating sample data...")
        with app.app_context():
            # Create sample teacher
            teacher = User(
                email="professor@university.edu",
                name="Dr. Sarah Johnson",
                role="teacher",
                department="Computer Science",
                bio="Professor of Artificial Intelligence and Machine Learning",
                phone="+1-555-0123"
            )
            db.session.add(teacher)
            
            # Create sample student
            student = User(
                email="student@university.edu",
                name="Alex Smith",
                role="student",
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
                priority="high",
                due_date="2024-12-15T23:59:59Z"
            )
            db.session.add(task1)
            
            task2 = Task(
                title="Read Chapter 3: Classification",
                description="Read and summarize the key concepts from Chapter 3 of the textbook.",
                lecture_id=lecture.id,
                assigned_to_id=student.id,
                priority="medium",
                due_date="2024-12-20T23:59:59Z"
            )
            db.session.add(task2)
            
            # Create sample notifications
            notification1 = Notification(
                user_id=student.id,
                type="task_assigned",
                title="New Assignment: Linear Regression",
                message="You have been assigned a new task: Complete Linear Regression Assignment",
                data={"task_id": task1.id, "due_date": "2024-12-15"}
            )
            db.session.add(notification1)
            
            notification2 = Notification(
                user_id=teacher.id,
                type="lecture_uploaded",
                title="Lecture Processed",
                message="Your lecture 'Introduction to Machine Learning' has been processed and tasks extracted.",
                data={"lecture_id": lecture.id}
            )
            db.session.add(notification2)
            
            db.session.commit()
            
        print("✅ Sample data created successfully!")
        return True
    except Exception as e:
        print(f"❌ Error creating sample data: {str(e)}")
        db.session.rollback()
        return False

def main():
    """Main function to initialize the database"""
    print("🚀 Initializing Classroom Assistant Database...")
    print("=" * 50)
    
    # Check if DATABASE_URL is set
    if not os.getenv('DATABASE_URL'):
        print("❌ DATABASE_URL environment variable not set!")
        print("Please set your DATABASE_URL in the .env file")
        sys.exit(1)
    
    # Initialize database
    if not init_database():
        sys.exit(1)
    
    # Create sample data
    create_sample_data()
    
    print("=" * 50)
    print("🎉 Database initialization completed!")
    print("\nNext steps:")
    print("1. Set up your environment variables in .env file")
    print("2. Run: python app.py")
    print("3. Test the API endpoints")

if __name__ == '__main__':
    main()
