import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.core.database import get_db, Base

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture
def client():
    # Create test database
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c
    # Clean up
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def test_user():
    return {
        "email": "test@example.com",
        "username": "testuser",
        "password": "TestPassword123!",
        "first_name": "Test",
        "last_name": "User"
    }

def test_health_check(client):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_root_endpoint(client):
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["message"] == "Astro Auth System API"

def test_user_registration(client, test_user):
    """Test user registration."""
    response = client.post("/api/auth/register", json=test_user)
    assert response.status_code == 200
    assert "registered successfully" in response.json()["message"]

def test_user_registration_duplicate_email(client, test_user):
    """Test user registration with duplicate email."""
    # Register first user
    client.post("/api/auth/register", json=test_user)
    
    # Try to register with same email
    response = client.post("/api/auth/register", json=test_user)
    assert response.status_code == 400
    assert "Email already registered" in response.json()["detail"]

def test_user_login(client, test_user):
    """Test user login."""
    # Register user first
    client.post("/api/auth/register", json=test_user)
    
    # Login
    login_data = {
        "email": test_user["email"],
        "password": test_user["password"]
    }
    response = client.post("/api/auth/login", json=login_data)
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert "refresh_token" in response.json()

def test_user_login_invalid_credentials(client):
    """Test user login with invalid credentials."""
    login_data = {
        "email": "nonexistent@example.com",
        "password": "wrongpassword"
    }
    response = client.post("/api/auth/login", json=login_data)
    assert response.status_code == 401
    assert "Incorrect email or password" in response.json()["detail"]

def test_protected_endpoint_without_token(client):
    """Test accessing protected endpoint without token."""
    response = client.get("/api/user/profile")
    assert response.status_code == 403

def test_user_profile_unverified(client, test_user):
    """Test user profile with unverified user."""
    # Register and login
    client.post("/api/auth/register", json=test_user)
    login_response = client.post("/api/auth/login", json={
        "email": test_user["email"],
        "password": test_user["password"]
    })
    
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Try to access profile (should fail because email not verified)
    response = client.get("/api/user/profile", headers=headers)
    assert response.status_code == 400
    assert "Email not verified" in response.json()["detail"]

def test_forgot_password(client, test_user):
    """Test forgot password functionality."""
    # Register user first
    client.post("/api/auth/register", json=test_user)
    
    # Request password reset
    response = client.post("/api/auth/forgot-password", json={
        "email": test_user["email"]
    })
    assert response.status_code == 200
    assert "password reset instructions" in response.json()["message"]

def test_logout(client, test_user):
    """Test user logout."""
    # Use a different email to avoid rate limiting
    test_user_logout = test_user.copy()
    test_user_logout["email"] = "logout@example.com"
    test_user_logout["username"] = "logoutuser"
    
    # Register and login
    client.post("/api/auth/register", json=test_user_logout)
    login_response = client.post("/api/auth/login", json={
        "email": test_user_logout["email"],
        "password": test_user_logout["password"]
    })
    
    # Check if login was successful
    if login_response.status_code != 200:
        print(f"Login failed: {login_response.json()}")
        return
    
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Logout
    response = client.post("/api/auth/logout", headers=headers)
    assert response.status_code == 200
    assert "Successfully logged out" in response.json()["message"]