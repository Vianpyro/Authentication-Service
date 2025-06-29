# Authentication Service API

This is the FastAPI-based REST API component of the Authentication Service. It provides secure user authentication, registration, and session management capabilities through a well-structured, versioned API.

## 🏗️ Architecture

The API follows a clean, modular architecture:

```
api/
├── app/
│   ├── main.py              # FastAPI application entry point
│   ├── version.py           # Version information
│   ├── routes/              # API route definitions
│   │   ├── home.py          # Root endpoint
│   │   └── v1/              # API version 1
│   │       ├── __init__.py  # V1 API setup
│   │       ├── endpoints/   # Route handlers
│   │       └── schemas/     # Pydantic models
│   └── utility/             # Shared utilities
│       ├── database.py      # Database connection
│       └── email.py         # Email utilities
├── requirements.txt         # Production dependencies
├── requirements-dev.txt     # Development dependencies
└── pyproject.toml           # Project configuration
```

## 🚀 Getting Started

### Prerequisites

- Python 3.12.11 or higher
- PostgreSQL database (handled by the database component)
- Development environment setup (dev container recommended)

### Installation

1. **Install dependencies:**
   ```bash
   pip install -r requirements-dev.txt
   ```

2. **Set up environment variables:**
   - The API uses the database connection configured in [`app.utility.database`](app/utility/database.py)
   - Default connection: `postgresql+asyncpg://vscode@0.0.0.0:5432/authentication-service`

### Running the API

1. **Development server:**
   ```bash
   # From the api directory
   uvicorn app.main:app --reload

   # Or use the VS Code task: "Start FastAPI server"
   ```

2. **Using the debugger:**
   - Use the VS Code launch configuration "Python: FastAPI" for debugging
   - This will also rebuild the database before starting

3. **Production:**
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

The API will be available at:
- **Main API:** http://localhost:8000
- **API v1:** http://localhost:8000/api/v1
- **Interactive docs:** http://localhost:8000/docs
- **OpenAPI spec:** http://localhost:8000/openapi.json

## 📚 API Structure

### Versioning Strategy

The API uses URL-based versioning to ensure backward compatibility:
- `/` - Root endpoints (non-versioned)
- `/api/v1/` - Version 1 endpoints
- `/api/v2/` - Version 2 endpoints (planned)

### Current Endpoints

#### Root Endpoints
- `GET /` - Welcome message

#### Application Management (`/api/v1/app/`)
- `POST /api/v1/app/register` - Register a new application
- `DELETE /api/v1/app/` - Delete an application

### Schema Design

The API uses a sophisticated schema system with reusable field types:

1. **Common Field Types** ([`app.routes.v1.schemas.common`](app/routes/v1/schemas/common.py))
   - Shared field definitions (UUIDs, timestamps, hashes, etc.)
   - Consistent validation across all schemas

2. **Domain-Specific Schemas**
   - [`application`](app/routes/v1/schemas/application.py) - Application management
   - [`user`](app/routes/v1/schemas/user.py) - User data structures
   - [`email`](app/routes/v1/schemas/email.py) - Email notifications
   - [`session`](app/routes/v1/schemas/session.py) - User sessions
   - And more...

## 🔧 Development

### Code Style

The project follows strict formatting and linting standards:
- **Black** for Python code formatting (120 character line limit)
- **isort** for import organization
- **Pytest** for testing

### VS Code Integration

The project includes comprehensive VS Code configuration:

1. **Tasks available:**
   - "Run all tests" - Execute the full test suite
   - "Run file tests" - Test the current file
   - "Start FastAPI server" - Launch development server

2. **Debug configurations:**
   - "Python: FastAPI" - Debug the API with database rebuild
   - "Python: Current File" - Debug any Python file

### Database Integration

The API connects to PostgreSQL using:
- **SQLAlchemy** with async support
- **asyncpg** driver for high performance
- Connection pooling and health checks

Database session management is handled through the [`get_db`](app/utility/database.py) dependency:

```python
from app.utility.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession

async def my_endpoint(db: AsyncSession = Depends(get_db)):
    # Use database session
    pass
```

### Testing

Run tests using pytest:

```bash
# Run all tests
python -m pytest tests/

# Run with verbose output
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_example.py
```

## 🔐 Security Features

The API implements several security measures:

1. **Input Validation**
   - Pydantic schemas with strict field validation
   - Pattern matching for sensitive fields (hashes, tokens)
   - Length limits and type checking

2. **Database Security**
   - Row-level security policies
   - Parameterized queries to prevent SQL injection
   - Tenant isolation through app_id validation

3. **Authentication Flow**
   - Argon2id password hashing
   - Session token management
   - Multi-factor authentication support
   - Device fingerprinting

## 📦 Dependencies

### Production Dependencies
- **FastAPI** - Modern web framework
- **SQLAlchemy** - Database ORM with async support
- **asyncpg** - PostgreSQL async driver
- **argon2-cffi** - Secure password hashing
- **cryptography** - Encryption utilities
- **pydantic[email]** - Data validation with email support
- **pyotp** - TOTP 2FA implementation

### Development Dependencies
- **pytest** - Testing framework
- **pytest-asyncio** - Async test support
- **build** - Package building

## 🚀 Deployment

The API can be deployed using:

1. **Docker** (recommended)
   ```bash
   docker build -t auth-api .
   docker run -p 8000:8000 auth-api
   ```

2. **Direct deployment**
   ```bash
   pip install -r requirements.txt
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

## 🤝 Contributing

1. Follow the existing code structure and naming conventions
2. Add appropriate Pydantic schemas for new endpoints
3. Include proper error handling and HTTP status codes
4. Write tests for new functionality
5. Update this README when adding new features

## 📝 API Documentation

Once running, visit `/docs` for interactive API documentation powered by Swagger UI, or `/redoc` for ReDoc-style documentation.
