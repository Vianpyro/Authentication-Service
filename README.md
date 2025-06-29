# Authentication Service

A production-ready, multi-tenant authentication service built with FastAPI, PostgreSQL, and security-first principles. This service provides secure user authentication, registration, session management, and multi-factor authentication for multiple applications.

## 🏗️ Project Architecture

This project follows a microservices architecture with clear separation of concerns:

```
Authentication-Service/
├── api/                     # FastAPI REST API
│   ├── app/                 # Application logic
│   │   ├── main.py          # FastAPI entry point
│   │   ├── routes/          # API endpoints
│   │   └── utility/         # Shared utilities
│   └── requirements*.txt    # Python dependencies
├── database/                # PostgreSQL database
│   ├── sql/                 # Database schema & functions
│   ├── scripts/             # Database maintenance
│   └── Dockerfile           # Database container
├── .devcontainer/           # Development environment
│   ├── devcontainer.json    # Dev container configuration
│   ├── docker-compose.yml   # Multi-service setup
│   └── Dockerfile           # Development image
└── .vscode/                 # VS Code configuration
    ├── launch.json          # Debug configurations
    ├── tasks.json           # Build & run tasks
    └── settings.json        # Editor settings
```

## 🚀 Quick Start

### Prerequisites

- **Docker** with Docker Compose
- **VS Code** with Dev Containers extension (recommended)
- **Git** for version control

### Development Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-org/Authentication-Service.git
   cd Authentication-Service
   ```

2. **Configure environment variables:**
   ```bash
   # Copy the example environment file
   cp .env.example .env

   # Edit the configuration
   nano .env
   ```

   **Example `.env` file:**
   ```properties
   # Database Configuration
   DB_PASSWORD=your_secure_password_here
   POSTGRES_DB=authentication-service
   POSTGRES_USER=postgres
   POSTGRES_HOST=database
   POSTGRES_PORT=5432

   # API Configuration
   API_PORT=8000

   # Constructed URLs (optional - can be built in compose file)
   DATABASE_URL=postgresql+asyncpg://postgres:${DB_PASSWORD}@${POSTGRES_HOST}:${POSTGRES_PORT}/${POSTGRES_DB}
   ```

> [!IMPORTANT]
> Change `DB_PASSWORD` to a secure password before running in production.

3. **Open in VS Code Dev Container:**
   ```bash
   code .
   # When prompted, click "Reopen in Container"
   ```

4. **Start the services:**
   ```bash
   # The dev container automatically starts PostgreSQL
   # Start the API server using VS Code task or:
   cd api
   uvicorn app.main:app --reload
   ```

5. **Access the services:**
   - **API Documentation:** http://localhost:8000/docs
   - **API v1:** http://localhost:8000/api/v1
   - **Database Admin:** `"$BROWSER" "http://localhost:8080/admin/database"`

## 🔐 Security Features

### Multi-Tenant Architecture
- **Row-Level Security (RLS):** Complete tenant isolation at the database level
- **Application Registration:** Secure app-based access control
- **API Key Management:** Per-application authentication

### User Security
- **Password Hashing:** Argon2id with configurable parameters
- **Multi-Factor Authentication:** TOTP-based 2FA with backup codes
- **Device Fingerprinting:** Device recognition and management
- **Account Protection:** Brute force protection, account locking

### Session Management
- **Opaque Tokens:** Secure, database-backed session tokens
- **Token Types:** Access and refresh token support
- **IP Tracking:** Session hijacking detection
- **Automatic Cleanup:** Expired session removal

### Database Security
- **Encryption at Rest:** Sensitive data encrypted in database
- **Audit Logging:** Comprehensive security event tracking
- **Automated Cleanup:** Scheduled data sanitization
- **Role-Based Access:** Minimal privilege database roles

## 🛠️ Development

### Available Services

#### API Service ([`api/`](api/))
FastAPI-based REST API with:
- Versioned endpoints (`/api/v1/`, `/api/v2/`)
- Pydantic schema validation
- Async database operations
- Comprehensive error handling

**Key Commands:**
```bash
cd api
# Install dependencies
pip install -r requirements-dev.txt

# Run development server
uvicorn app.main:app --reload

# Run tests
python -m pytest tests/ -v
```

#### Database Service ([`database/`](database/))
PostgreSQL database with:
- Security-first schema design
- Automated maintenance scripts
- Custom domains and functions
- Comprehensive indexing

**Key Commands:**
```bash
cd database
# Rebuild database
./scripts/rebuild-db.sh vscode authentication-service

# Flatten SQL files
./scripts/flatten-sql.sh

# Build database container
docker build -t auth-database .
```

### VS Code Integration

The project includes comprehensive VS Code configuration:

#### Tasks Available
- **"Run all tests"** - Execute the full test suite
- **"Run file tests"** - Test the current file
- **"Start FastAPI server"** - Launch development server
- **"Rebuild Database"** - Reset database to clean state

#### Debug Configurations
- **"Python: FastAPI"** - Debug the API with database rebuild
- **"Python: Current File"** - Debug any Python file

#### Extensions Included
- Python support with linting and formatting
- PostgreSQL syntax highlighting
- REST Client for API testing
- Docker integration

### Code Quality

The project enforces strict code quality standards:

- **Python:** Black formatting (120 char limit), isort imports
- **SQL:** SQLFluff linting with PostgreSQL dialect
- **Testing:** Pytest with async support
- **Type Safety:** Pydantic models with strict validation

## 📚 API Documentation

### Authentication Flow

1. **Application Registration:**
   ```bash
   POST /api/v1/app/register
   {
     "name": "My Application",
     "slug": "my-app",
     "url": "https://myapp.com"
   }
   ```

2. **User Registration:**
   ```bash
   POST /api/v1/users/register
   {
     "email": "user@example.com",
     "password": "secure_password",
     "app_id": "uuid-from-step-1"
   }
   ```

3. **User Login:**
   ```bash
   POST /api/v1/auth/login
   {
     "email": "user@example.com",
     "password": "secure_password",
     "app_id": "uuid"
   }
   ```

### Multi-Factor Authentication

```bash
# Enable 2FA
POST /api/v1/auth/2fa/enable
Authorization: Bearer <session_token>

# Verify TOTP
POST /api/v1/auth/2fa/verify
{
  "totp_code": "123456"
}
```

### Session Management

```bash
# Refresh token
POST /api/v1/auth/refresh
{
  "refresh_token": "refresh_token_here"
}

# Logout
POST /api/v1/auth/logout
Authorization: Bearer <session_token>
```

For complete API documentation, visit `/docs` when running the service.

## 🚀 Deployment

### Production Environment

1. **Environment Variables:**
   ```bash
   # Create production environment file
   cp .env.example .env.production

   # Required variables for production:
   DB_PASSWORD=secure_random_password_here
   POSTGRES_DB=authentication-service
   POSTGRES_USER=auth_service
   POSTGRES_HOST=database
   POSTGRES_PORT=5432
   API_PORT=8000

   # Optional: Pre-constructed database URL
   DATABASE_URL=postgresql+asyncpg://${POSTGRES_USER}:${DB_PASSWORD}@${POSTGRES_HOST}:${POSTGRES_PORT}/${POSTGRES_DB}
   ```

2. **Docker Compose Production:**
   ```yaml
   services:
     db:
       build: ./database
       environment:
         POSTGRES_USER: auth_service
         POSTGRES_PASSWORD: ${DB_PASSWORD}
         POSTGRES_DB: authentication-service
       volumes:
         - db_data:/var/lib/postgresql/data

     api:
       build: ./api
       environment:
         DATABASE_URL: postgresql+asyncpg://auth_service:${DB_PASSWORD}@db:5432/authentication-service
       ports:
         - "8000:8000"
       depends_on:
         - db

   volumes:
     db_data:
   ```

3. **Deploy:**
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

### Health Checks

Monitor service health:
```bash
# API health
curl http://localhost:8000/

# Database health
docker exec auth-db pg_isready -U auth_service
```

## 🔍 Monitoring & Maintenance

### Automated Maintenance

The database includes automated cleanup jobs:
- **Every 5 minutes:** Account locking, brute force protection
- **Daily:** Expired data cleanup, user lifecycle management

### Key Metrics to Monitor

- **API Performance:** Response times, error rates
- **Database:** Connection usage, query performance
- **Security:** Failed login attempts, locked accounts
- **Storage:** Database size growth, backup status

### Useful Monitoring Queries

```sql
-- Active sessions by application
SELECT a.name, COUNT(s.*) as active_sessions
FROM applications a
LEFT JOIN sessions s ON s.app_id = a.id
WHERE s.expires_at > NOW()
GROUP BY a.name;

-- Security events in last 24 hours
SELECT event_type, COUNT(*)
FROM security_events
WHERE occurred_at > NOW() - INTERVAL '1 day'
GROUP BY event_type;
```

## 🧪 Testing

### Running Tests

```bash
# API tests
cd api
python -m pytest tests/ -v

# Database tests
cd database
psql -U vscode -d authentication-service -f test_functions.sql
```

### Test Coverage

The project includes tests for:
- **API Endpoints:** Request/response validation
- **Database Functions:** Security and business logic
- **Authentication Flow:** End-to-end user journeys
- **Security Features:** 2FA, session management, etc.

## 🤝 Contributing

### Development Workflow

1. **Create a feature branch:**
   ```bash
   git checkout -b feature/new-authentication-method
   ```

2. **Make your changes:**
   - Follow existing code style and patterns
   - Add tests for new functionality
   - Update documentation as needed

3. **Run quality checks:**
   ```bash
   # Format code
   black --line-length 120 api/

   # Run tests
   python -m pytest api/tests/ -v

   # Lint SQL
   sqlfluff lint database/sql/
   ```

4. **Submit a pull request:**
   - Provide clear description of changes
   - Include test results
   - Reference any related issues

### Code Standards

- **Security First:** All changes must maintain security principles
- **Tenant Isolation:** Preserve multi-tenant data separation
- **Backward Compatibility:** API changes require version bumps
- **Documentation:** Update README files for significant changes

## 📋 Roadmap

### Current Features ✅
- Multi-tenant user authentication
- Session management with opaque tokens
- TOTP-based multi-factor authentication
- Device fingerprinting and management
- Comprehensive audit logging
- Automated security maintenance

### Planned Features 🚧
- OAuth2/OIDC provider support
- WebAuthn/FIDO2 authentication
- Advanced rate limiting
- Email-based passwordless authentication
- Administrative dashboard
- Metrics and analytics API

### Future Considerations 💭
- Mobile SDK development
- Federated identity support
- Advanced threat detection
- Compliance reporting (GDPR, SOC2)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

### Documentation
- **API Documentation:** Available at `/docs` when running
- **Database Schema:** See [`database/README.md`](database/README.md)
- **API Details:** See [`api/README.md`](api/README.md)

### Getting Help
- **Issues:** Use GitHub Issues for bug reports and feature requests
- **Discussions:** Use GitHub Discussions for questions and ideas
- **Security:** Report security issues privately via email

### Troubleshooting

#### Common Issues

1. **Database Connection Failed:**
   ```bash
   # Check if database is running
   docker ps | grep postgres

   # Check connection
   psql -U vscode -h localhost -d authentication-service
   ```

2. **API Import Errors:**
   ```bash
   # Ensure you're in the api directory
   cd api
   pip install -r requirements-dev.txt
   ```

3. **Dev Container Issues:**
   ```bash
   # Rebuild dev container
   # Ctrl+Shift+P -> "Dev Containers: Rebuild Container"
   ```

#### Performance Issues
- Check database indexes with `EXPLAIN ANALYZE`
- Monitor connection pool usage
- Review slow query logs

---

**Built with ❤️ for secure, scalable authentication**
