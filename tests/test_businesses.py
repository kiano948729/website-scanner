"""
Tests for business API endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database.connection import get_db, Base
from app.models.business import Business


# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def db_session():
    """Create database session for testing."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


def test_create_business(client, db_session):
    """Test creating a new business."""
    business_data = {
        "name": "Test Business",
        "city": "Amsterdam",
        "country": "Netherlands",
        "is_zzp": True,
        "website_exists": False
    }
    
    response = client.post("/api/v1/businesses/", json=business_data)
    assert response.status_code == 200
    
    data = response.json()
    assert data["name"] == "Test Business"
    assert data["city"] == "Amsterdam"
    assert data["is_zzp"] is True
    assert data["website_exists"] is False


def test_get_businesses(client, db_session):
    """Test getting list of businesses."""
    # Create test business
    business = Business(
        name="Test Business",
        city="Amsterdam",
        country="Netherlands",
        is_zzp=True,
        website_exists=False
    )
    db_session.add(business)
    db_session.commit()
    
    response = client.get("/api/v1/businesses/")
    assert response.status_code == 200
    
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Test Business"


def test_get_business_stats(client, db_session):
    """Test getting business statistics."""
    # Create test businesses
    businesses = [
        Business(name="Business 1", city="Amsterdam", country="Netherlands", is_zzp=True, website_exists=False),
        Business(name="Business 2", city="Rotterdam", country="Netherlands", is_zzp=True, website_exists=True),
        Business(name="Business 3", city="Brussels", country="Belgium", is_zzp=False, website_exists=True),
    ]
    
    for business in businesses:
        db_session.add(business)
    db_session.commit()
    
    response = client.get("/api/v1/businesses/stats/summary")
    assert response.status_code == 200
    
    data = response.json()
    assert data["total_businesses"] == 3
    assert data["businesses_with_website"] == 2
    assert data["businesses_without_website"] == 1
    assert data["zzp_businesses"] == 2
    assert data["zzp_without_website"] == 1


def test_search_businesses(client, db_session):
    """Test searching businesses."""
    # Create test businesses
    businesses = [
        Business(name="Webdesign Amsterdam", city="Amsterdam", country="Netherlands"),
        Business(name="Marketing Rotterdam", city="Rotterdam", country="Netherlands"),
        Business(name="Consulting Brussels", city="Brussels", country="Belgium"),
    ]
    
    for business in businesses:
        db_session.add(business)
    db_session.commit()
    
    response = client.get("/api/v1/businesses/search/?q=Amsterdam")
    assert response.status_code == 200
    
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Webdesign Amsterdam"


def test_get_business_by_id(client, db_session):
    """Test getting a specific business by ID."""
    business = Business(
        name="Test Business",
        city="Amsterdam",
        country="Netherlands"
    )
    db_session.add(business)
    db_session.commit()
    
    response = client.get(f"/api/v1/businesses/{business.id}")
    assert response.status_code == 200
    
    data = response.json()
    assert data["name"] == "Test Business"
    assert data["city"] == "Amsterdam"


def test_update_business(client, db_session):
    """Test updating a business."""
    business = Business(
        name="Test Business",
        city="Amsterdam",
        country="Netherlands"
    )
    db_session.add(business)
    db_session.commit()
    
    update_data = {
        "name": "Updated Business",
        "city": "Rotterdam"
    }
    
    response = client.put(f"/api/v1/businesses/{business.id}", json=update_data)
    assert response.status_code == 200
    
    data = response.json()
    assert data["name"] == "Updated Business"
    assert data["city"] == "Rotterdam"


def test_delete_business(client, db_session):
    """Test deleting a business."""
    business = Business(
        name="Test Business",
        city="Amsterdam",
        country="Netherlands"
    )
    db_session.add(business)
    db_session.commit()
    
    response = client.delete(f"/api/v1/businesses/{business.id}")
    assert response.status_code == 200
    
    # Verify business is deleted
    get_response = client.get(f"/api/v1/businesses/{business.id}")
    assert get_response.status_code == 404 