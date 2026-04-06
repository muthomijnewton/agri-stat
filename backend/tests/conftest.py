import pytest
import sys
from pathlib import Path
import tempfile

# Add the backend app directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.main import app
from app.db.database import Base, get_db
from app.models.models import User, Product, Transaction, Forecast, InventoryRecommendation


@pytest.fixture(scope="function")
def engine():
    """Create a test engine using a temporary file-based SQLite database."""
    # Create a temporary database file
    db_file = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
    db_url = f"sqlite:///{db_file.name}"
    db_file.close()
    
    eng = create_engine(db_url, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=eng)
    
    yield eng
    
    Base.metadata.drop_all(bind=eng)
    eng.dispose()
    
    # Clean up temp file
    try:
        Path(db_file.name).unlink()
    except:
        pass


@pytest.fixture(scope="function")
def db_session(engine):
    """Create a test database session."""
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    
    yield session
    
    session.rollback()
    session.close()


@pytest.fixture
def client(db_session):
    """Create a test client with overridden dependencies."""
    def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    yield TestClient(app)
    
    app.dependency_overrides.clear()


@pytest.fixture
def db(db_session):
    """Alias for db_session for backwards compatibility."""
    return db_session


@pytest.fixture
def sample_product(db_session):
    """Create a sample product for testing."""
    product = Product(
        name="Test Rice",
        category="Grains",
        description="High quality rice",
        unit_price=25.50,
        unit="kg",
        is_active=True
    )
    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)
    return product


@pytest.fixture
def sample_user(db_session):
    """Create a sample user for testing."""
    user = User(
        username="testuser",
        email="test@example.com",
        password="hashed_password",
        full_name="Test User",
        is_admin=False,
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def sample_transaction(db_session, sample_product, sample_user):
    """Create a sample transaction for testing."""
    transaction = Transaction(
        product_id=sample_product.id,
        user_id=sample_user.id,
        quantity=10,
        unit_price=25.50,
        total_price=255.00,
        transaction_date="2026-04-06",
        notes="Test transaction"
    )
    db_session.add(transaction)
    db_session.commit()
    db_session.refresh(transaction)
    return transaction


@pytest.fixture
def sample_forecast(db_session, sample_product):
    """Create a sample forecast for testing."""
    forecast = Forecast(
        product_id=sample_product.id,
        forecast_date="2026-04-10",
        predicted_demand=150,
        confidence_lower=120,
        confidence_upper=180,
        model_type="prophet",
        accuracy_score=0.92
    )
    db_session.add(forecast)
    db_session.commit()
    db_session.refresh(forecast)
    return forecast


@pytest.fixture
def sample_recommendation(db_session, sample_product):
    """Create a sample inventory recommendation for testing."""
    recommendation = InventoryRecommendation(
        product_id=sample_product.id,
        recommended_quantity=500,
        current_quantity=100,
        min_quantity=50,
        max_quantity=1000,
        recommendation_date="2026-04-06",
        reason="Low stock detected",
        status="pending"
    )
    db_session.add(recommendation)
    db_session.commit()
    db_session.refresh(recommendation)
    return recommendation
