# from fastapi import FastAPI
# from fastapi.testclient import TestClient
# from app.core.auth import register_user, login_user
# from app.models.user import User
# from app.schemas.user import UserCreate, UserLogin
# from app.database import get_db
# from sqlalchemy.orm import Session
# import pytest

# app = FastAPI()

# # Dependency override for testing
# @app.get("/test/db")
# def override_get_db():
#     db = next(get_db())
#     try:
#         yield db
#     finally:
#         db.close()

# client = TestClient(app)

# @pytest.fixture
# def test_user():
#     user_data = UserCreate(email="test@example.com", password="password")
#     return user_data

# def test_register_user(test_user):
#     response = client.post("/auth/register", json=test_user.dict())
#     assert response.status_code == 201
#     assert response.json()["email"] == test_user.email

# def test_login_user(test_user):
#     client.post("/auth/register", json=test_user.dict())
#     login_data = UserLogin(email=test_user.email, password=test_user.password)
#     response = client.post("/auth/login", json=login_data.dict())
#     assert response.status_code == 200
#     assert "access_token" in response.json()

# def test_get_current_user(test_user):
#     client.post("/auth/register", json=test_user.dict())
#     login_data = UserLogin(email=test_user.email, password=test_user.password)
#     login_response = client.post("/auth/login", json=login_data.dict())
#     access_token = login_response.json()["access_token"]
    
#     response = client.get("/auth/me", headers={"Authorization": f"Bearer {access_token}"})
#     assert response.status_code == 200
#     assert response.json()["email"] == test_user.email