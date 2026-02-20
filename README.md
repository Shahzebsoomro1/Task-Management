# Task Management System - Production-Ready Full-Stack Application

A complete, production-ready full-stack Task Management System built with **FastAPI**, **PostgreSQL**, **SQLAlchemy**, and **React**. This project demonstrates enterprise-level architecture, security best practices, and modern development patterns.

## Features

✅ **User Management**
- User registration with email validation
- Secure login with JWT authentication
- Role-based access control (Admin, User)
- Password hashing with bcrypt

✅ **Project Management**
- Create, read, update, delete projects
- User-specific project isolation
- Project descriptions and metadata

✅ **Task Management**
- Full CRUD operations for tasks
- Task status management (todo, in_progress, done)
- Task priority levels (low, medium, high)
- Due date tracking
- Task assignment to users
- Filtering by status, priority, and assigned user
- Sorting by due date and priority
- Pagination support

✅ **Comments System**
- Add comments to tasks
- View all comments for a task
- Edit and delete comments (with authorization)
- Timestamped comment tracking

✅ **Security**
- JWT-based authentication
- Password hashing with bcrypt
- Role-based authorization
- Input validation with Pydantic v2
- CORS middleware
- SQL injection prevention with ORM

✅ **Architecture**
- Clean, scalable project structure
- Service layer pattern
- Repository pattern for data access
- Async/await throughout
- Comprehensive error handling
- Database migrations with Alembic

✅ **DevOps**
- Docker containerization
- Docker Compose orchestration
- PostgreSQL database
- Environment-based configuration

## Project Structure

```
project-root/
│
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI application entry point
│   │   ├── core/
│   │   │   ├── config.py           # Configuration and settings
│   │   │   ├── security.py         # JWT and password utilities
│   │   │   └── __init__.py
│   │   ├── db/
│   │   │   ├── base.py             # Base repository class
│   │   │   ├── database.py         # SQLAlchemy declarative base
│   │   │   └── __init__.py
│   │   ├── models/
│   │   │   ├── models.py           # SQLAlchemy models
│   │   │   └── __init__.py
│   │   ├── schemas/
│   │   │   ├── schemas.py          # Pydantic request/response schemas
│   │   │   └── __init__.py
│   │   ├── repositories/
│   │   │   ├── user_repository.py
│   │   │   ├── project_repository.py
│   │   │   ├── task_repository.py
│   │   │   ├── comment_repository.py
│   │   │   └── __init__.py
│   │   ├── services/
│   │   │   ├── user_service.py
│   │   │   ├── project_service.py
│   │   │   ├── task_service.py
│   │   │   ├── comment_service.py
│   │   │   └── __init__.py
│   │   ├── api/
│   │   │   └── v1/
│   │   │       ├── __init__.py     # API v1 router
│   │   │       ├── auth.py         # Authentication endpoints
│   │   │       ├── projects.py     # Project endpoints
│   │   │       ├── tasks.py        # Task endpoints
│   │   │       └── comments.py     # Comment endpoints
│   │   ├── tests/
│   │   │   ├── test_main.py        # Comprehensive test suite
│   │   │   └── __init__.py
│   │   └── __init__.py
│   │
│   ├── alembic/                    # Database migrations
│   │   ├── versions/
│   │   │   ├── 001_initial.py      # Initial migration
│   │   │   └── __init__.py
│   │   ├── env.py                  # Alembic environment
│   │   └── __init__.py
│   │
│   ├── alembic.ini                 # Alembic configuration
│   ├── requirements.txt            # Python dependencies
│   ├── Dockerfile                  # Backend Docker image
│   ├── pytest.ini                  # Pytest configuration
│   └── .gitignore
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   └── ProtectedRoute.jsx  # Route protection HOC
│   │   ├── pages/
│   │   │   ├── Auth.jsx            # Login/Register pages
│   │   │   ├── Auth.css
│   │   │   ├── Projects.jsx        # Projects management page
│   │   │   ├── Projects.css
│   │   │   ├── Tasks.jsx           # Tasks management page
│   │   │   └── Tasks.css
│   │   ├── services/
│   │   │   ├── api.js              # Axios configuration
│   │   │   └── index.js            # API service methods
│   │   ├── App.jsx                 # Main app component
│   │   ├── App.css
│   │   └── main.jsx                # React entry point
│   │
│   ├── index.html                  # HTML template
│   ├── package.json                # Node dependencies
│   ├── vite.config.js              # Vite configuration
│   ├── Dockerfile                  # Frontend Docker image
│   ├── .gitignore
│   └── .env (runtime)
│
├── docker-compose.yml              # Docker Compose orchestration
├── .env.example                    # Environment variables template
└── README.md                       # This file
```

## Technology Stack

### Backend
- **FastAPI 0.104.1** - Modern async web framework
- **PostgreSQL 16** - Relational database
- **SQLAlchemy 2.0.23** - Async ORM
- **Alembic 1.13.0** - Database migrations
- **Pydantic 2.5.0** - Data validation
- **python-jose** - JWT token handling
- **passlib + bcrypt** - Password hashing
- **pytest 7.4.3** - Testing framework

### Frontend
- **React 18.2.0** - UI library
- **React Router 6.18.0** - Client-side routing
- **Axios 1.6.0** - HTTP client
- **Vite 5.0.0** - Build tool

### DevOps
- **Docker** - Containerization
- **Docker Compose** - Service orchestration
- **PostgreSQL** - Database container

## Quick Start

### Prerequisites
- Docker and Docker Compose installed
- Git (optional)

### Running the Project

1. **Clone or download the project**
   ```bash
   cd Task-Mangement
   ```

2. **Create environment file** (optional, defaults are provided)
   ```bash
   cp .env.example .env
   ```

3. **Build and start all services**
   ```bash
   docker-compose up --build
   ```

   This command will:
   - Build the backend Docker image
   - Build the frontend Docker image
   - Start PostgreSQL database
   - Start FastAPI backend (with migrations)
   - Start React frontend
   - Wait for database to be healthy

4. **Access the application**
   - **Frontend**: http://localhost:3000
   - **Backend API**: http://localhost:8000
   - **API Docs (Swagger)**: http://localhost:8000/docs

### First Steps

1. **Register a new account**
   - Go to http://localhost:3000/register
   - Enter your name, email, and password
   - Click "Register"

2. **Login**
   - Use your registered credentials
   - You'll be redirected to the projects page

3. **Create a project**
   - Click "+ New Project"
   - Enter project name and description
   - Click "Create Project"

4. **Manage tasks**
   - Click "View Tasks" on a project
   - Create tasks with title, description, and priority
   - Change task status (To Do → In Progress → Done)
   - Add comments to tasks

## API Documentation

### Authentication Endpoints

#### Register
```bash
POST /api/v1/auth/register
Content-Type: application/json

{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "securepass123",
  "role": "user"
}
```

#### Login
```bash
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "john@example.com",
  "password": "securepass123"
}

Response:
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "user": {...}
}
```

#### Get Current User
```bash
GET /api/v1/auth/me
Authorization: Bearer <token>
```

### Project Endpoints

#### Create Project
```bash
POST /api/v1/projects
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "My Project",
  "description": "Project description"
}
```

#### Get All Projects
```bash
GET /api/v1/projects
Authorization: Bearer <token>
```

#### Get Single Project
```bash
GET /api/v1/projects/{project_id}
Authorization: Bearer <token>
```

#### Update Project
```bash
PUT /api/v1/projects/{project_id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "Updated Project",
  "description": "Updated description"
}
```

#### Delete Project
```bash
DELETE /api/v1/projects/{project_id}
Authorization: Bearer <token>
```

### Task Endpoints

#### Create Task
```bash
POST /api/v1/projects/{project_id}/tasks
Authorization: Bearer <token>
Content-Type: application/json

{
  "title": "Task Title",
  "description": "Task description",
  "priority": "high",
  "due_date": "2024-12-31",
  "assigned_to": "user_id_optional"
}
```

#### Get Project Tasks
```bash
GET /api/v1/projects/{project_id}/tasks
Authorization: Bearer <token>

Query Parameters:
- status: todo|in_progress|done
- assigned_to: user_id
- order_by: due_date|priority|created_at
- order_desc: true|false
- skip: 0
- limit: 100
```

#### Update Task
```bash
PUT /api/v1/projects/{project_id}/tasks/{task_id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "status": "in_progress",
  "priority": "medium"
}
```

#### Delete Task
```bash
DELETE /api/v1/projects/{project_id}/tasks/{task_id}
Authorization: Bearer <token>
```

### Comment Endpoints

#### Create Comment
```bash
POST /api/v1/tasks/{task_id}/comments
Authorization: Bearer <token>
Content-Type: application/json

{
  "content": "Comment text"
}
```

#### Get Task Comments
```bash
GET /api/v1/tasks/{task_id}/comments
Authorization: Bearer <token>
```

#### Update Comment
```bash
PUT /api/v1/tasks/{task_id}/comments/{comment_id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "content": "Updated comment"
}
```

#### Delete Comment
```bash
DELETE /api/v1/tasks/{task_id}/comments/{comment_id}
Authorization: Bearer <token>
```

## Database Schema

### Users Table
```sql
CREATE TABLE users (
  id UUID PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  email VARCHAR(255) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  role ENUM('admin', 'user') DEFAULT 'user',
  created_at TIMESTAMP WITH TIMEZONE NOT NULL
);
CREATE INDEX ix_users_email ON users(email);
```

### Projects Table
```sql
CREATE TABLE projects (
  id UUID PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  description VARCHAR(1000),
  created_by UUID NOT NULL (FK users.id),
  created_at TIMESTAMP WITH TIMEZONE NOT NULL
);
CREATE INDEX ix_projects_created_by ON projects(created_by);
```

### Tasks Table
```sql
CREATE TABLE tasks (
  id UUID PRIMARY KEY,
  title VARCHAR(255) NOT NULL,
  description VARCHAR(2000),
  status ENUM('todo', 'in_progress', 'done') DEFAULT 'todo',
  priority ENUM('low', 'medium', 'high') DEFAULT 'medium',
  due_date DATE,
  project_id UUID NOT NULL (FK projects.id),
  assigned_to UUID (FK users.id),
  created_by UUID NOT NULL (FK users.id),
  created_at TIMESTAMP WITH TIMEZONE NOT NULL
);
CREATE INDEX ix_tasks_project_id ON tasks(project_id);
CREATE INDEX ix_tasks_assigned_to ON tasks(assigned_to);
CREATE INDEX ix_tasks_created_by ON tasks(created_by);
```

### Comments Table
```sql
CREATE TABLE comments (
  id UUID PRIMARY KEY,
  content VARCHAR(2000) NOT NULL,
  task_id UUID NOT NULL (FK tasks.id),
  created_by UUID NOT NULL (FK users.id),
  created_at TIMESTAMP WITH TIMEZONE NOT NULL
);
CREATE INDEX ix_comments_task_id ON comments(task_id);
```

## Architecture Explanation

### Clean Architecture Layers

1. **API Layer** (`app/api/`)
   - HTTP endpoints using FastAPI
   - Route handlers
   - Request/response handling
   - Status code management

2. **Service Layer** (`app/services/`)
   - Business logic implementation
   - Authorization checks
   - Data validation
   - Orchestration of repositories

3. **Repository Layer** (`app/repositories/`)
   - Database access abstraction
   - Query building
   - CRUD operations
   - Base repository pattern for reusability

4. **Models** (`app/models/`)
   - SQLAlchemy ORM models
   - Database table definitions
   - Relationships and constraints

5. **Schemas** (`app/schemas/`)
   - Pydantic request/response schemas
   - Data validation rules
   - Serialization/deserialization

6. **Core** (`app/core/`)
   - Configuration management
   - Security utilities (JWT, password hashing)
   - Database configuration

### Design Patterns Used

- **Repository Pattern**: Abstracts data access logic
- **Service Pattern**: Contains business logic
- **Dependency Injection**: FastAPI's `Depends()` for loose coupling
- **Base Repository**: Generic CRUD operations
- **Async/Await**: Non-blocking I/O throughout
- **Pagination**: Efficient data fetching
- **Filtering**: Query-based filtering
- **Authorization**: Role and ownership checks

## Testing

### Running Tests

```bash
# Run all tests
docker-compose exec backend pytest

# Run specific test file
docker-compose exec backend pytest app/tests/test_main.py

# Run with verbose output
docker-compose exec backend pytest -v

# Run with coverage
docker-compose exec backend pytest --cov=app
```

### Test Coverage

The test suite includes:
- Authentication endpoints (register, login)
- Project CRUD operations
- Task CRUD operations
- Authorization checks
- Error handling
- Health check endpoint

## Security Features

### Password Security
- Passwords are hashed using bcrypt
- Minimum 8 characters required
- Never stored in plain text

### JWT Authentication
- Tokens expire after 30 minutes (configurable)
- Uses HS256 algorithm
- Token contains user ID for authorization

### Authorization
- Role-based access control (Admin, User)
- User can only access their own resources
- Admin can access all resources
- Project ownership verification
- Task access validation

### Input Validation
- Pydantic v2 validation
- Email format validation
- Field length validation
- Enum validation for status/priority
- SQL injection prevention via ORM

### API Security
- CORS middleware configured
- Content-Type validation
- HTTP status codes for errors
- Error messages don't leak sensitive info

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| DATABASE_URL | postgresql+asyncpg://taskuser:taskpass@postgres:5432/taskmanagement | PostgreSQL connection string |
| SECRET_KEY | your-secret-key-... | JWT signing key (change in production!) |
| ALGORITHM | HS256 | JWT algorithm |
| ACCESS_TOKEN_EXPIRE_MINUTES | 30 | JWT token expiry time |
| DEBUG | True | FastAPI debug mode |
| APP_NAME | Task Management System | Application name |
| SQLALCHEMY_ECHO | False | SQL query logging |

## Troubleshooting

### Database Connection Issues
```bash
# Check database is running
docker-compose ps

# Restart services
docker-compose restart

# Check logs
docker-compose logs postgres
docker-compose logs backend
```

### Port Already in Use
If ports 3000, 8000, or 5432 are already in use:

```yaml
# Edit docker-compose.yml
services:
  postgres:
    ports:
      - "5433:5432"  # Change 5433 to unused port
  backend:
    ports:
      - "8001:8000"  # Change 8001 to unused port
  frontend:
    ports:
      - "3001:3000"  # Change 3001 to unused port
```

### Database Migrations Failed
```bash
# Manually run migrations
docker-compose exec backend alembic upgrade head

# Check migration status
docker-compose exec backend alembic current
```

### Frontend Not Loading
```bash
# Clear cache and rebuild
docker-compose down
docker-compose up --build

# Check logs
docker-compose logs frontend
```

## Development Workflow

### Local Backend Development (without Docker)

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r backend/requirements.txt

# Set environment variables
export DATABASE_URL=postgresql://user:pass@localhost:5432/taskmanagement

# Run migrations
alembic upgrade head

# Start server
uvicorn app.main:app --reload

# Run tests
pytest
```

### Local Frontend Development

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## Performance Considerations

### Database Optimization
- Indexes on foreign keys (project_id, assigned_to, created_by)
- Indexes on frequently filtered columns (email)
- Async queries prevent blocking
- Pagination limits large result sets

### Backend Optimization
- Async/await for non-blocking operations
- Connection pooling (NullPool for compatibility)
- N+1 query prevention via ORM relationships
- Efficient filtering and pagination

### Frontend Optimization
- Client-side routing (no full page reloads)
- Axios request/response interceptors
- Protected routes prevent unauthorized access
- Local storage for token persistence

## Deployment Considerations

### Production Security Checklist
- [ ] Change `SECRET_KEY` to a strong, random value (min 32 characters)
- [ ] Set `DEBUG=False`
- [ ] Use strong database password
- [ ] Enable HTTPS
- [ ] Set proper CORS origins
- [ ] Use environment variables from `.env` file
- [ ] Set up database backups
- [ ] Configure logging for audit trails
- [ ] Rate limiting for API endpoints
- [ ] Web Application Firewall (WAF)

### Production Deployment Example
```bash
# Build images for production
docker-compose build

# Push to registry
docker tag task-management-backend:latest myregistry/task-backend:latest
docker push myregistry/task-backend:latest

# Deploy with strong secrets
docker-compose -f docker-compose.yml \
  -e SECRET_KEY='your-production-secret-key' \
  -e DATABASE_URL='your-production-db-url' \
  up -d
```

## Contributing

1. Create a feature branch: `git checkout -b feature/amazing-feature`
2. Commit changes: `git commit -m 'Add amazing feature'`
3. Push to branch: `git push origin feature/amazing-feature`
4. Open a Pull Request

## License

This project is open source and available under the MIT License.

## Support

For issues, questions, or suggestions, please create an issue in the repository.

---

**Built with ❤️ using FastAPI, PostgreSQL, SQLAlchemy, and React**

Last Updated: February 20, 2024
Version: 1.0.0

