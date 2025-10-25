from database import db
from datetime import datetime
from enum import Enum
import uuid

class UserRole(Enum):
    TEACHER = "teacher"
    STUDENT = "student"

class TaskStatus(Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    APPROVED = "approved"

class TaskPriority(Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class NotificationType(Enum):
    TASK_ASSIGNED = "task_assigned"
    TASK_DUE = "task_due"
    LECTURE_UPLOADED = "lecture_uploaded"
    TASK_APPROVED = "task_approved"

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    firebase_uid = db.Column(db.String(128), unique=True, nullable=False, index=True)  # Firebase UID
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.Enum(UserRole), nullable=False)
    student_id = db.Column(db.String(20), nullable=True)  # For students
    major = db.Column(db.String(100), nullable=True)  # For students
    year = db.Column(db.String(20), nullable=True)  # For students
    department = db.Column(db.String(100), nullable=True)  # For teachers
    bio = db.Column(db.Text, nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    notifications_enabled = db.Column(db.Boolean, default=True)
    email_notifications = db.Column(db.Boolean, default=True)
    dark_mode = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    lectures = db.relationship('Lecture', backref='teacher', lazy=True, foreign_keys='Lecture.teacher_id')
    tasks = db.relationship('Task', backref='assigned_to', lazy=True, foreign_keys='Task.assigned_to_id')
    notifications = db.relationship('Notification', backref='user', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'firebase_uid': self.firebase_uid,
            'email': self.email,
            'name': self.name,
            'role': self.role.value,
            'student_id': self.student_id,
            'major': self.major,
            'year': self.year,
            'department': self.department,
            'bio': self.bio,
            'phone': self.phone,
            'notifications_enabled': self.notifications_enabled,
            'email_notifications': self.email_notifications,
            'dark_mode': self.dark_mode,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Lecture(db.Model):
    __tablename__ = 'lectures'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = db.Column(db.String(200), nullable=False)
    subject = db.Column(db.String(100), nullable=False)
    teacher_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    audio_url = db.Column(db.String(500), nullable=True)  # Supabase storage URL
    audio_duration = db.Column(db.Integer, nullable=True)  # Duration in seconds
    transcript = db.Column(db.Text, nullable=True)
    summary = db.Column(db.Text, nullable=True)
    key_points = db.Column(db.JSON, nullable=True)  # Array of key points
    tags = db.Column(db.JSON, nullable=True)  # Array of tags
    is_processed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    tasks = db.relationship('Task', backref='lecture', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'subject': self.subject,
            'teacher_id': self.teacher_id,
            'teacher_name': self.teacher.name if self.teacher else None,
            'audio_url': self.audio_url,
            'audio_duration': self.audio_duration,
            'transcript': self.transcript,
            'summary': self.summary,
            'key_points': self.key_points,
            'tags': self.tags,
            'is_processed': self.is_processed,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Task(db.Model):
    __tablename__ = 'tasks'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    lecture_id = db.Column(db.String(36), db.ForeignKey('lectures.id'), nullable=True)
    assigned_to_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=True)
    status = db.Column(db.Enum(TaskStatus), default=TaskStatus.PENDING)
    priority = db.Column(db.Enum(TaskPriority), default=TaskPriority.MEDIUM)
    due_date = db.Column(db.DateTime, nullable=True)
    is_ai_generated = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'lecture_id': self.lecture_id,
            'lecture_title': self.lecture.title if self.lecture else None,
            'assigned_to_id': self.assigned_to_id,
            'assigned_to_name': self.assigned_to.name if self.assigned_to else None,
            'status': self.status.value,
            'priority': self.priority.value,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'is_ai_generated': self.is_ai_generated,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Notification(db.Model):
    __tablename__ = 'notifications'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    type = db.Column(db.Enum(NotificationType), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    data = db.Column(db.JSON, nullable=True)  # Additional data for the notification
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'type': self.type.value,
            'title': self.title,
            'message': self.message,
            'data': self.data,
            'is_read': self.is_read,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
