# KanMind Backend - Django REST API

A full-featured Kanban board API built with Django REST Framework, featuring token-based authentication, board management, task tracking, and commenting system.

## 🚀 Features

- **Token Authentication** - Secure API access with Bearer tokens
- **User Management** - Registration, login, and email verification
- **Board Management** - Create, update, and manage boards with members
- **Task System** - Full CRUD operations with assignee and reviewer support
- **Comments** - Task-level commenting system
- **Permission Control** - Role-based access (Owner/Member)

## 📋 Prerequisites

- Python 3.8+
- pip
- Virtual environment (recommended)

## 🛠️ Installation

### 1. Clone and Setup

```bash
# Navigate to project directory
cd kanmind-backend-final

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Configuration

Create `.env` file in project root:

```env
SECRET_KEY='your-secret-key-here'
DEBUG=True
```

Generate a secure secret key:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 3. Database Setup

```bash
# Create database tables
python manage.py migrate

# Create superuser (admin)
python manage.py createsuperuser
```

### 4. Run Development Server

```bash
python manage.py runserver
```

API will be available at: `http://127.0.0.1:8000/`

## 📚 API Documentation

### Authentication Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/registration/` | Register new user |
| POST | `/api/login/` | Login and get token |
| GET | `/api/email-check/` | Check if email exists |

### Board Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/boards/` | List all boards | ✅ |
| POST | `/api/boards/` | Create board | ✅ |
| GET | `/api/boards/{id}/` | Board details | ✅ |
| PATCH | `/api/boards/{id}/` | Update board | ✅ |
| DELETE | `/api/boards/{id}/` | Delete board | ✅ (Owner) |

### Task Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/tasks/` | Create task | ✅ |
| PATCH | `/api/tasks/{id}/` | Update task | ✅ |
| DELETE | `/api/tasks/{id}/` | Delete task | ✅ |
| GET | `/api/tasks/assigned-to-me/` | My assigned tasks | ✅ |
| GET | `/api/tasks/reviewing/` | Tasks I'm reviewing | ✅ |

### Comment Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/tasks/{task_id}/comments/` | List comments | ✅ |
| POST | `/api/tasks/{task_id}/comments/` | Create comment | ✅ |
| DELETE | `/api/tasks/{task_id}/comments/{id}/` | Delete comment | ✅ (Author) |

## 🔑 Authentication

All protected endpoints require a Bearer token in the Authorization header:

```
Authorization: Bearer <your-token-here>
```

### Example: Registration

**Request:**
```bash
POST /api/registration/
Content-Type: application/json

{
    "fullname": "John Doe",
    "email": "john@example.com",
    "password": "SecurePass123!",
    "repeated_password": "SecurePass123!"
}
```

**Response:**
```json
{
    "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b",
    "fullname": "John Doe",
    "email": "john@example.com",
    "user_id": 1
}
```

### Example: Create Board

**Request:**
```bash
POST /api/boards/
Authorization: Bearer 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
Content-Type: application/json

{
    "title": "My Project",
    "members": [2, 3, 4]
}
```

**Response:**
```json
{
    "id": 1,
    "title": "My Project",
    "member_count": 3,
    "ticket_count": 0,
    "tasks_to_do_count": 0,
    "tasks_high_prio_count": 0,
    "owner_id": 1
}
```

## 📁 Project Structure

```
kanmind-backend-final/
├── core/                   # Project settings
│   ├── settings.py        # Main configuration
│   └── urls.py            # URL routing
├── auth_app/              # Authentication
│   ├── api/
│   │   ├── serializers.py
│   │   ├── views.py
│   │   └── urls.py
│   ├── authentication.py  # Custom token auth
│   └── models.py          # User model
├── kanban_app/            # Kanban features
│   ├── api/
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── permissions.py
│   └── models.py          # Board, Task, Comment
├── manage.py
└── requirements.txt
```

## 🔧 Configuration

### CORS Settings

By default, the API allows requests from:
- `http://127.0.0.1:5500`
- `http://localhost:5500`

To modify, edit `CORS_ALLOWED_ORIGINS` in `core/settings.py`.

### Database

Default: SQLite (`db.sqlite3`)

To use PostgreSQL or MySQL, update `DATABASES` in `settings.py`.

## 🧪 Testing

### Using Postman

1. Import the provided Postman collection
2. Set environment variable: `base_url = http://127.0.0.1:8000/api`
3. Register a user to get a token
4. Token is automatically saved to `{{token}}` variable
5. Run the collection tests

### Using curl

```bash
# Register
curl -X POST http://127.0.0.1:8000/api/registration/ \
  -H "Content-Type: application/json" \
  -d '{"fullname":"Test User","email":"test@example.com","password":"Test123!","repeated_password":"Test123!"}'

# Create Board (replace TOKEN)
curl -X POST http://127.0.0.1:8000/api/boards/ \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"My Board","members":[]}'
```

## 📝 Task Status & Priority

### Status Values
- `to-do`
- `in-progress`
- `review`
- `done`

### Priority Values
- `low`
- `medium`
- `high`

## 🚨 Common Issues

### 401 Unauthorized
- Ensure token is included in Authorization header
- Token format: `Bearer <token>`
- Check if token is valid in database

### 403 Forbidden
- User lacks permission (not owner/member)
- Check board membership

### 404 Not Found
- Resource doesn't exist
- Check URL and IDs

## 📄 License

This project is part of a coding bootcamp assignment.
