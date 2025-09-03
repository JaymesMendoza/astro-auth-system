# FastAPI Backend for Astro Authentication System

A comprehensive FastAPI backend that provides authentication and user management services for the Astro frontend.

## Features

### Authentication API
- User registration with email verification
- JWT-based login/logout system
- Token refresh functionality
- Password reset flow
- Email verification

### User Management API
- User profile management
- Password change
- Avatar upload (Cloudinary integration)
- Account deletion

### Admin API
- User management with pagination and filtering
- User role management
- System statistics
- Admin-only endpoints

### Security Features
- Password hashing with bcrypt
- JWT tokens with blacklist support
- Rate limiting
- CORS configuration
- Input validation and sanitization

## Quick Start

### Prerequisites
- Python 3.9+
- Virtual environment (recommended)

### Installation

1. **Navigate to backend directory**
```bash
cd backend
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. **Run database migrations**
```bash
alembic upgrade head
```

6. **Start the server**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## Configuration

The backend uses environment variables for configuration. Copy `.env.example` to `.env` and update the values:

### Required Configuration
- `JWT_SECRET`: Secret key for JWT tokens (change in production!)
- `JWT_REFRESH_SECRET`: Secret key for refresh tokens (change in production!)

### Optional Configuration
- `DATABASE_URL`: Database connection string (defaults to SQLite)
- `REDIS_URL`: Redis connection for rate limiting
- `SMTP_*`: Email service configuration
- `CLOUDINARY_*`: File upload service configuration

## API Endpoints

### Authentication (`/api/auth`)
- `POST /register` - Register new user
- `POST /login` - User login
- `POST /logout` - User logout
- `POST /refresh` - Refresh access token
- `POST /forgot-password` - Request password reset
- `POST /reset-password` - Reset password
- `POST /verify-email` - Verify email address
- `POST /resend-verification` - Resend verification email

### User Management (`/api/user`)
- `GET /profile` - Get user profile
- `PUT /profile` - Update user profile
- `POST /change-password` - Change password
- `POST /upload-avatar` - Upload avatar
- `DELETE /account` - Delete account

### Admin (`/api/admin`)
- `GET /users` - List users (with pagination)
- `GET /users/{id}` - Get user details
- `PUT /users/{id}` - Update user
- `DELETE /users/{id}` - Delete user
- `PUT /users/{id}/role` - Change user role
- `GET /stats` - Get system statistics

## Database

The backend uses SQLAlchemy ORM with support for:
- **SQLite** (default, for development)
- **PostgreSQL** (recommended for production)

### Migrations

Create a new migration:
```bash
alembic revision --autogenerate -m "Description"
```

Apply migrations:
```bash
alembic upgrade head
```

## Development

### Running Tests
```bash
pytest
```

### Code Structure
```
app/
├── api/          # API route handlers
├── core/         # Core configuration and dependencies
├── models/       # SQLAlchemy models
├── schemas/      # Pydantic schemas for validation
├── services/     # Business logic layer
├── middleware/   # Custom middleware
└── utils/        # Utility functions
```

## Deployment

### Docker
A Dockerfile is provided for containerized deployment:

```bash
docker build -t astro-auth-backend .
docker run -p 8000:8000 astro-auth-backend
```

### Environment Variables for Production
Make sure to set secure values for:
- `JWT_SECRET` and `JWT_REFRESH_SECRET`
- `DATABASE_URL` (PostgreSQL recommended)
- Email service credentials
- Cloudinary credentials (for file uploads)

## Integration with Astro Frontend

The backend is configured to work with the Astro frontend:
- CORS is configured for the frontend URL
- API responses use consistent JSON format
- Authentication flow compatible with frontend JWT handling

## Security Considerations

- Change all default secrets in production
- Use HTTPS for all communications
- Configure proper CORS settings
- Set up proper email and file upload services
- Regular security updates

## License

MIT License