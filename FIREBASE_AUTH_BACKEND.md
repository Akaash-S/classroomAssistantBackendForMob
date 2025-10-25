# Firebase Authentication Backend - Complete Working Implementation

## Overview
This backend provides a complete Firebase authentication integration for the Classroom Assistant application. It handles user registration, login, and profile management using Firebase UIDs instead of traditional password-based authentication.

## Key Features

### ✅ User Registration
- **Endpoint**: `POST /api/auth/register`
- **Authentication**: Uses Firebase UID (no password required)
- **Required Fields**: `firebase_uid`, `email`, `name`, `role`
- **Optional Fields**: `student_id`, `major`, `year`, `department`, `bio`, `phone`
- **Response**: Returns complete user profile data

### ✅ User Login
- **Endpoint**: `POST /api/auth/login`
- **Authentication**: Uses Firebase UID
- **Required Fields**: `firebase_uid`
- **Response**: Returns user profile data

### ✅ User Profile Management
- **Get User**: `GET /api/auth/user/firebase/<firebase_uid>`
- **Update Profile**: `PUT /api/auth/user/update/<firebase_uid>`
- **Get Profile by ID**: `GET /api/auth/profile/<user_id>`

### ✅ Database Integration
- **Database**: PostgreSQL (Neon)
- **Models**: User, Lecture, Task, Notification
- **Migration**: Automatic Firebase UID column addition
- **Relationships**: Proper foreign key relationships

## Database Schema

### Users Table
```sql
CREATE TABLE users (
    id VARCHAR(36) PRIMARY KEY,
    firebase_uid VARCHAR(128) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    role VARCHAR(20) NOT NULL, -- 'teacher' or 'student'
    student_id VARCHAR(20), -- For students
    major VARCHAR(100), -- For students
    year VARCHAR(20), -- For students
    department VARCHAR(100), -- For teachers
    bio TEXT,
    phone VARCHAR(20),
    notifications_enabled BOOLEAN DEFAULT TRUE,
    email_notifications BOOLEAN DEFAULT TRUE,
    dark_mode BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

## API Endpoints

### 1. User Registration
```http
POST /api/auth/register
Content-Type: application/json

{
    "firebase_uid": "firebase_user_uid_here",
    "email": "user@example.com",
    "name": "User Name",
    "role": "student", // or "teacher"
    "student_id": "STU001", // optional
    "major": "Computer Science", // optional
    "year": "2024", // optional
    "department": "Computer Science", // optional for teachers
    "bio": "User bio", // optional
    "phone": "+1234567890" // optional
}
```

**Response (201 Created):**
```json
{
    "status": "success",
    "message": "User registered successfully",
    "user": {
        "id": "uuid-here",
        "firebase_uid": "firebase_user_uid_here",
        "email": "user@example.com",
        "name": "User Name",
        "role": "student",
        "student_id": "STU001",
        "major": "Computer Science",
        "year": "2024",
        "department": null,
        "bio": null,
        "phone": null,
        "notifications_enabled": true,
        "email_notifications": true,
        "dark_mode": false,
        "created_at": "2025-10-25T06:22:35.702725",
        "updated_at": "2025-10-25T06:22:35.702725"
    }
}
```

### 2. User Login
```http
POST /api/auth/login
Content-Type: application/json

{
    "firebase_uid": "firebase_user_uid_here"
}
```

**Response (200 OK):**
```json
{
    "status": "success",
    "message": "Login successful",
    "user": {
        // Complete user object as above
    }
}
```

### 3. Get User by Firebase UID
```http
GET /api/auth/user/firebase/{firebase_uid}
```

**Response (200 OK):**
```json
{
    "status": "success",
    "user": {
        // Complete user object
    }
}
```

### 4. Update User Profile
```http
PUT /api/auth/user/update/{firebase_uid}
Content-Type: application/json

{
    "name": "Updated Name",
    "bio": "Updated bio",
    "phone": "+1234567890",
    "notifications_enabled": false
}
```

**Response (200 OK):**
```json
{
    "status": "success",
    "message": "Profile updated successfully",
    "user": {
        // Updated user object
    }
}
```

## Frontend Integration

### Firebase Authentication Flow
1. **Frontend**: User signs up with Firebase (`createUserWithEmailAndPassword`)
2. **Frontend**: Gets Firebase UID from authenticated user
3. **Frontend**: Calls backend registration endpoint with Firebase UID
4. **Backend**: Creates user profile in PostgreSQL database
5. **Frontend**: Stores user data for future API calls

### Example Frontend Code
```javascript
// After Firebase authentication
const user = firebase.auth().currentUser;
if (user) {
    const registrationData = {
        firebase_uid: user.uid,
        email: user.email,
        name: user.displayName || 'User',
        role: 'student', // or 'teacher'
        // ... other optional fields
    };
    
    const response = await fetch('/api/auth/register', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(registrationData)
    });
    
    const result = await response.json();
    if (result.status === 'success') {
        // User registered successfully
        console.log('User registered:', result.user);
    }
}
```

## Environment Variables

The backend requires the following environment variables (configured in `.env`):

```env
# Database Configuration
DATABASE_URL=postgresql://user:password@host:port/database

# Supabase Configuration (for file storage)
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key
SUPABASE_SERVICE_KEY=your_supabase_service_key

# API Keys
RAPIDAPI_KEY=your_rapidapi_key
GEMINI_API_KEY=your_gemini_api_key

# Flask Configuration
FLASK_ENV=development
SECRET_KEY=your_secret_key

# CORS Configuration
CORS_ORIGINS=http://localhost:3000,http://localhost:8081
```

## Testing

### Test Scripts
- `test_user_model.py` - Tests User model and database operations
- `debug_registration.py` - Tests registration endpoint with detailed output
- `simple_test.py` - Comprehensive API testing

### Running Tests
```bash
# Test User model
python test_user_model.py

# Test registration endpoint
python debug_registration.py

# Run comprehensive tests
python simple_test.py
```

## Error Handling

### Common Error Responses

**400 Bad Request:**
```json
{
    "status": "error",
    "message": "Missing required field: firebase_uid"
}
```

**409 Conflict:**
```json
{
    "status": "error",
    "message": "User with this email or Firebase UID already exists"
}
```

**404 Not Found:**
```json
{
    "status": "error",
    "message": "User not found"
}
```

**500 Internal Server Error:**
```json
{
    "status": "error",
    "message": "Registration failed"
}
```

## Security Features

1. **Firebase Authentication**: All authentication handled by Firebase
2. **CORS Protection**: Configured for specific origins
3. **Input Validation**: Required field validation
4. **Database Constraints**: Unique constraints on email and Firebase UID
5. **Error Handling**: Comprehensive error handling without exposing sensitive data

## Deployment

### Prerequisites
- Python 3.8+
- PostgreSQL database
- Firebase project configured

### Installation
```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp env_example.txt .env
# Edit .env with your configuration

# Run database migration
python migrate_firebase_uid.py

# Start the server
python app.py
```

### Production Deployment
- Use a production WSGI server (Gunicorn)
- Set `FLASK_ENV=production`
- Use a production PostgreSQL database
- Configure proper CORS origins
- Set up SSL/TLS

## File Structure

```
backend/
├── app.py                 # Main Flask application
├── database.py           # SQLAlchemy database instance
├── models.py             # Database models
├── config.py             # Configuration classes
├── routes/
│   └── auth_working.py   # Authentication routes
├── services/             # Business logic services
├── .env                  # Environment variables
├── requirements.txt      # Python dependencies
├── migrate_firebase_uid.py # Database migration
└── test_*.py            # Test scripts
```

## Next Steps

1. **Frontend Integration**: Update frontend to use the new registration endpoint
2. **Additional Endpoints**: Add lecture, task, and notification endpoints
3. **File Upload**: Implement Supabase file storage integration
4. **AI Integration**: Add Gemini AI service integration
5. **Testing**: Add comprehensive unit and integration tests
6. **Documentation**: Add API documentation with Swagger/OpenAPI

## Support

For issues or questions:
1. Check the test scripts for examples
2. Review the error logs
3. Verify environment variables
4. Test database connectivity
5. Check Firebase configuration
