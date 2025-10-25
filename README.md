# 🎓 Classroom Assistant Backend

A production-ready Flask backend for the Classroom Assistant application, providing AI-powered lecture processing, user management, and task automation.

## 🚀 Features

- **User Authentication** - Firebase integration with role-based access
- **Lecture Management** - Create, process, and manage lectures
- **AI Processing** - Speech-to-text transcription and AI summarization
- **Task Management** - Automated task generation from lectures
- **Notification System** - Real-time notifications for users
- **File Storage** - Supabase cloud storage for audio files
- **RESTful API** - Complete REST API with proper error handling

## 🏗️ Architecture

```
backend/
├── app.py                 # Main Flask application
├── config.py             # Configuration management
├── database.py           # Database connection
├── models.py             # SQLAlchemy models
├── requirements.txt      # Python dependencies
├── Dockerfile           # Production Docker container
├── routes/              # API route handlers
│   ├── auth_working.py  # Authentication endpoints
│   ├── lectures.py      # Lecture management
│   ├── tasks.py         # Task management
│   ├── notifications.py # Notification system
│   └── ai.py            # AI processing endpoints
└── services/            # External service integrations
    ├── gemini_service.py      # Google Gemini AI
    ├── speech_to_text.py      # RapidAPI transcription
    └── supabase_storage.py    # Supabase cloud storage
```

## 🛠️ Technology Stack

- **Framework**: Flask 2.3.3
- **Database**: PostgreSQL with SQLAlchemy
- **Authentication**: Firebase Auth
- **AI Services**: Google Gemini 2.0 Flash
- **Storage**: Supabase Cloud Storage
- **Transcription**: RapidAPI Speech-to-Text
- **Deployment**: Docker + Gunicorn
- **Database Migrations**: Flask-Migrate

## 🚀 Quick Start

### Development

```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp env.production.example .env
# Edit .env with your configuration

# Run the application
python app.py
```

### Production with Docker

```bash
# Build and run with Docker
docker build -t classroom-assistant-backend .
docker run -d --name classroom-backend --env-file .env -p 5000:5000 classroom-assistant-backend

# Or use Docker Compose
docker-compose up -d
```

## 📋 API Endpoints

### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `GET /api/auth/user/firebase/<uid>` - Get user by Firebase UID
- `PUT /api/auth/user/update/<uid>` - Update user profile

### Lectures
- `GET /api/lectures/` - List lectures
- `POST /api/lectures/` - Create lecture
- `GET /api/lectures/<id>` - Get lecture details
- `PUT /api/lectures/<id>` - Update lecture
- `DELETE /api/lectures/<id>` - Delete lecture
- `POST /api/lectures/<id>/upload-audio` - Upload audio file
- `POST /api/lectures/<id>/process` - Process with AI

### Tasks
- `GET /api/tasks/` - List tasks
- `POST /api/tasks/` - Create task
- `PUT /api/tasks/<id>` - Update task
- `DELETE /api/tasks/<id>` - Delete task

### Notifications
- `GET /api/notifications/` - List notifications
- `POST /api/notifications/` - Create notification
- `PUT /api/notifications/<id>/read` - Mark as read

### AI Processing
- `POST /api/ai/transcribe` - Transcribe audio
- `POST /api/ai/summarize` - Summarize text
- `POST /api/ai/generate-tasks` - Generate tasks from lecture

## 🔧 Configuration

### Environment Variables

```env
# Database
DATABASE_URL=postgresql://user:pass@host:5432/db

# Supabase
SUPABASE_URL=https://project.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-key

# APIs
RAPIDAPI_KEY=your-rapidapi-key
GEMINI_API_KEY=your-gemini-key

# Flask
SECRET_KEY=your-secret-key
CORS_ORIGINS=https://your-frontend.com
```

## 🐳 Docker Deployment

The application is containerized for easy deployment:

```bash
# Build image
docker build -t classroom-assistant-backend .

# Run container
docker run -d --name classroom-backend --env-file .env -p 5000:5000 classroom-assistant-backend

# Health check
curl http://localhost:5000/api/health
```

## 📊 Database Schema

### Users
- Firebase UID integration
- Role-based access (teacher/student)
- Profile management

### Lectures
- Audio file storage
- AI-generated transcripts
- Summaries and key points
- Processing status

### Tasks
- Automated generation from lectures
- Assignment and tracking
- Priority and status management

### Notifications
- Real-time user notifications
- Email and push notifications
- Read status tracking

## 🔒 Security

- Firebase authentication
- Role-based access control
- CORS configuration
- Environment variable security
- Database SSL connections
- Input validation and sanitization

## 📈 Performance

- Database connection pooling
- Gunicorn WSGI server
- Request rate limiting
- Health checks and monitoring
- Optimized Docker layers

## 🆘 Troubleshooting

### Common Issues

1. **Database Connection**: Check DATABASE_URL format
2. **API Keys**: Verify all external service keys
3. **CORS Issues**: Update CORS_ORIGINS configuration
4. **File Upload**: Check Supabase storage configuration

### Health Checks

- `GET /` - Basic health check
- `GET /api/health` - Detailed system status

## 📞 Support

For issues and questions:
1. Check container logs: `docker logs classroom-backend`
2. Verify environment variables
3. Test individual API endpoints
4. Check external service connectivity

## 🎯 Production Checklist

- [ ] Environment variables configured
- [ ] Database migrations run
- [ ] External services tested
- [ ] CORS origins updated
- [ ] SSL certificates configured
- [ ] Monitoring setup
- [ ] Backup strategy implemented