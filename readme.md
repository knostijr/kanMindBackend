# KanMind Backend API

Django REST Framework Backend for the KanMind Kanban Board application.

## Features

- User Authentication (Registration, Login with JWT)
- Board Management (CRUD operations)
- Task Management with status tracking
- Comment system for tasks
- User assignment and task reviewing

## Tech Stack

- Python 3.8+
- Django 4.2+
- Django REST Framework
- SQLite Database
- Token Authentication

## Installation

### 1. Clone Repository
```bash
git clone <your-repo-url>
cd kanmind-backend
```

### 2. Create Virtual Environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Configuration

Create `.env` file in project root:
```env
SECRET_KEY='your-secret-key-here'
DEBUG=True
```

Generate a new SECRET_KEY:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 5. Database Setup
```bash
python manage.py migrate
python manage.py createsuperuser
```

### 6. Run Development Server
```bash
python manage.py runserver
```

API will be available at: `http://127.0.0.1:8000/api/`
Admin interface: `http://127.0.0.1:8000/admin/`

## API Endpoints

### Authentication
- `POST /api/registration/` - Register new user
- `POST /api/login/` - Login and receive JWT tokens

### Boards
- `GET /api/boards/` - List all boards
- `POST /api/boards/` - Create board
- `GET /api/boards/{id}/` - Board details
- `PATCH /api/boards/{id}/` - Update board
- `DELETE /api/boards/{id}/` - Delete board
- `GET /api/email-check/?email=<email>` - Check email availability

### Tasks
- `GET /api/tasks/` - List all tasks
- `POST /api/tasks/` - Create task
- `GET /api/tasks/{id}/` - Task details
- `PATCH /api/tasks/{id}/` - Update task
- `DELETE /api/tasks/{id}/` - Delete task
- `GET /api/tasks/assigned-to-me/` - Get assigned tasks
- `GET /api/tasks/reviewing/` - Get review tasks

### Comments
- `GET /api/tasks/{task_id}/comments/` - List comments
- `POST /api/tasks/{task_id}/comments/` - Create comment
- `DELETE /api/tasks/{task_id}/comments/{id}/` - Delete comment

## Testing

Use Postman or similar tool to test endpoints. Import the provided Postman collection.
