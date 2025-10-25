# Classroom Assistant Backend

A Flask-based REST API backend for the Classroom Assistant mobile application, providing AI-powered lecture processing, task management, and user management.

## 🏗️ Architecture

- **Framework**: Flask (Python)
- **Database**: Neon PostgreSQL
- **Storage**: Supabase Storage
- **AI Services**: 
  - RapidAPI (Speech-to-Text)
  - Gemini API (Text processing, task extraction)
- **Authentication**: Custom user management

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- PostgreSQL database (Neon recommended)
- Supabase account
- RapidAPI account
- Google AI Studio account (for Gemini API)

### Installation

1. **Clone and navigate to backend directory**
   ```bash
   cd backend
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp env_example.txt .env
   ```
   
   Edit `.env` file with your credentials:
   ```env
   # Database Configuration
   DATABASE_URL=postgresql://username:password@host:port/database_name
   
   # Supabase Configuration
   SUPABASE_URL=your_supabase_url
   SUPABASE_KEY=your_supabase_anon_key
   SUPABASE_SERVICE_KEY=your_supabase_service_key
   
   # RapidAPI Configuration
   RAPIDAPI_KEY=your_rapidapi_key
   RAPIDAPI_HOST=your_rapidapi_host
   
   # Gemini API Configuration
   GEMINI_API_KEY=your_gemini_api_key
   
   # Flask Configuration
   FLASK_ENV=development
   FLASK_DEBUG=True
   SECRET_KEY=your_secret_key_here
   
   # CORS Configuration
   CORS_ORIGINS=http://localhost:3000,http://localhost:8081
   ```

4. **Initialize the database**
   ```bash
   python init_db.py
   ```

5. **Run the application**
   ```bash
   python app.py
   ```

The API will be available at `http://localhost:5000`

## 📚 API Documentation

### Authentication Endpoints

#### Register User
```http
POST /api/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "name": "John Doe",
  "role": "teacher", // or "student"
  "password": "secure_password",
  "student_id": "STU001", // for students
  "major": "Computer Science", // for students
  "year": "Junior", // for students
  "department": "Computer Science", // for teachers
  "bio": "Brief bio",
  "phone": "+1-555-0123"
}
```

#### Login User
```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "secure_password"
}
```

#### Get User Profile
```http
GET /api/auth/profile/{user_id}
```

#### Update Profile
```http
PUT /api/auth/profile/{user_id}
Content-Type: application/json

{
  "name": "Updated Name",
  "bio": "Updated bio",
  "phone": "+1-555-9999"
}
```

### Lecture Management

#### Get Lectures
```http
GET /api/lectures?teacher_id={id}&subject={subject}&limit=20&offset=0
```

#### Create Lecture
```http
POST /api/lectures
Content-Type: application/json

{
  "title": "Introduction to AI",
  "subject": "Artificial Intelligence",
  "teacher_id": "teacher_uuid",
  "audio_url": "https://storage.url/audio.mp3",
  "audio_duration": 3600
}
```

#### Upload Audio
```http
POST /api/lectures/{lecture_id}/upload-audio
Content-Type: application/json

{
  "audio_url": "https://storage.url/audio.mp3",
  "audio_duration": 3600
}
```

#### Process Lecture (AI)
```http
POST /api/lectures/{lecture_id}/process
```

### Task Management

#### Get Tasks
```http
GET /api/tasks?user_id={id}&status=pending&priority=high&limit=20&offset=0
```

#### Create Task
```http
POST /api/tasks
Content-Type: application/json

{
  "title": "Complete Assignment 1",
  "description": "Implement linear regression algorithm",
  "lecture_id": "lecture_uuid",
  "assigned_to_id": "student_uuid",
  "priority": "high",
  "due_date": "2024-12-15T23:59:59Z"
}
```

#### Update Task Status
```http
PUT /api/tasks/{task_id}/status
Content-Type: application/json

{
  "status": "completed"
}
```

#### Approve Task
```http
POST /api/tasks/{task_id}/approve
```

### AI Services

#### Transcribe Audio
```http
POST /api/ai/transcribe
Content-Type: application/json

{
  "audio_url": "https://storage.url/audio.mp3"
}
```

#### Summarize Text
```http
POST /api/ai/summarize
Content-Type: application/json

{
  "text": "Long text to summarize..."
}
```

#### Extract Tasks
```http
POST /api/ai/extract-tasks
Content-Type: application/json

{
  "text": "Lecture transcript with tasks mentioned..."
}
```

#### Process Lecture (Full AI Pipeline)
```http
POST /api/ai/process-lecture/{lecture_id}
```

### Notifications

#### Get Notifications
```http
GET /api/notifications?user_id={id}&type=task_assigned&is_read=false&limit=20&offset=0
```

#### Create Notification
```http
POST /api/notifications
Content-Type: application/json

{
  "user_id": "user_uuid",
  "type": "task_assigned",
  "title": "New Task Assigned",
  "message": "You have been assigned a new task",
  "data": {"task_id": "task_uuid"}
}
```

#### Mark as Read
```http
PUT /api/notifications/{notification_id}/read
```

## 🗄️ Database Schema

### Users Table
- `id` (UUID, Primary Key)
- `email` (String, Unique)
- `name` (String)
- `role` (Enum: teacher/student)
- `student_id` (String, for students)
- `major` (String, for students)
- `year` (String, for students)
- `department` (String, for teachers)
- `bio` (Text)
- `phone` (String)
- `notifications_enabled` (Boolean)
- `email_notifications` (Boolean)
- `dark_mode` (Boolean)
- `created_at` (DateTime)
- `updated_at` (DateTime)

### Lectures Table
- `id` (UUID, Primary Key)
- `title` (String)
- `subject` (String)
- `teacher_id` (UUID, Foreign Key)
- `audio_url` (String)
- `audio_duration` (Integer)
- `transcript` (Text)
- `summary` (Text)
- `key_points` (JSON)
- `tags` (JSON)
- `is_processed` (Boolean)
- `created_at` (DateTime)
- `updated_at` (DateTime)

### Tasks Table
- `id` (UUID, Primary Key)
- `title` (String)
- `description` (Text)
- `lecture_id` (UUID, Foreign Key)
- `assigned_to_id` (UUID, Foreign Key)
- `status` (Enum: pending/completed/approved)
- `priority` (Enum: high/medium/low)
- `due_date` (DateTime)
- `is_ai_generated` (Boolean)
- `created_at` (DateTime)
- `updated_at` (DateTime)

### Notifications Table
- `id` (UUID, Primary Key)
- `user_id` (UUID, Foreign Key)
- `type` (Enum: task_assigned/task_due/lecture_uploaded/task_approved)
- `title` (String)
- `message` (Text)
- `data` (JSON)
- `is_read` (Boolean)
- `created_at` (DateTime)

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `DATABASE_URL` | PostgreSQL connection string | Yes |
| `SUPABASE_URL` | Supabase project URL | Yes |
| `SUPABASE_KEY` | Supabase anonymous key | Yes |
| `SUPABASE_SERVICE_KEY` | Supabase service key | Yes |
| `RAPIDAPI_KEY` | RapidAPI key for STT | Yes |
| `RAPIDAPI_HOST` | RapidAPI host for STT | Yes |
| `GEMINI_API_KEY` | Google Gemini API key | Yes |
| `SECRET_KEY` | Flask secret key | Yes |
| `CORS_ORIGINS` | Allowed CORS origins | No |

### Supabase Storage Buckets

Create the following buckets in your Supabase project:

1. **`lectures`** - For audio files
2. **`images`** - For profile pictures and other images

## 🧪 Testing

### Health Check
```bash
curl http://localhost:5000/api/health
```

### Test AI Services
```bash
curl http://localhost:5000/api/ai/health
```

## 🚀 Deployment

### Using Gunicorn
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Using Docker
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

## 📝 Development

### Database Migrations
```bash
# Initialize migrations
flask db init

# Create migration
flask db migrate -m "Description"

# Apply migration
flask db upgrade
```

### Running Tests
```bash
python -m pytest tests/
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.
