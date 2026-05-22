from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.models import User
from app.schemas.schemas import LoginRequest, LoginResponse

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.post("/login", response_model=LoginResponse, status_code=status.HTTP_200_OK)
def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    """
    Login endpoint with simple username/password authentication
    For production, implement proper password hashing (bcrypt, argon2, etc.)
    """
    # Find user by username
    user = db.query(User).filter(User.username == credentials.username).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    # Check password (simple comparison for now - use hashing in production)
    if user.password != credentials.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    # Return user data on successful login
    return LoginResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        is_admin=user.is_admin,
        message="Login successful"
    )

@router.post("/verify", response_model=LoginResponse)
def verify_user(credentials: LoginRequest, db: Session = Depends(get_db)):
    """
    Verify user credentials (same as login, can be used for session validation)
    """
    return login(credentials, db)

@router.post("/seed-database")
def seed_database(db: Session = Depends(get_db)):
    """
    Initialize database with sample data for testing and demos.
    Run this once after deployment to populate with sample products, transactions, forecasts, and recommendations.
    
    Example: curl -X POST http://localhost:8000/api/auth/seed-database
    """
    from datetime import datetime, timedelta
    from decimal import Decimal
    from app.models.models import Product, Transaction, Forecast, InventoryRecommendation
    
    # Check if data already exists
    product_count = db.query(Product).count()
    if product_count > 0:
        return {
            "message": "Database already populated",
            "products": product_count,
            "status": "skipped"
        }
    
    try:
        # Add sample products
        products_data = [
            {"name": "Tomatoes", "category": "Vegetables", "unit_price": Decimal("25.50"), "unit": "kg"},
            {"name": "Maize (Corn)", "category": "Grains", "unit_price": Decimal("15.00"), "unit": "kg"},
            {"name": "Beans", "category": "Legumes", "unit_price": Decimal("30.00"), "unit": "kg"},
            {"name": "Potatoes", "category": "Root Vegetables", "unit_price": Decimal("18.75"), "unit": "kg"},
            {"name": "Carrots", "category": "Vegetables", "unit_price": Decimal("22.00"), "unit": "kg"},
            {"name": "Cabbage", "category": "Vegetables", "unit_price": Decimal("12.50"), "unit": "kg"},
            {"name": "Onions", "category": "Root Vegetables", "unit_price": Decimal("20.00"), "unit": "kg"},
            {"name": "Wheat", "category": "Grains", "unit_price": Decimal("45.00"), "unit": "kg"},
            {"name": "Lettuce", "category": "Vegetables", "unit_price": Decimal("28.00"), "unit": "kg"},
            {"name": "Peppers", "category": "Vegetables", "unit_price": Decimal("32.50"), "unit": "kg"},
            {"name": "Broccoli", "category": "Vegetables", "unit_price": Decimal("26.75"), "unit": "kg"},
            {"name": "Spinach", "category": "Vegetables", "unit_price": Decimal("35.00"), "unit": "kg"},
            {"name": "Cucumbers", "category": "Vegetables", "unit_price": Decimal("18.50"), "unit": "kg"},
            {"name": "Rice", "category": "Grains", "unit_price": Decimal("38.00"), "unit": "kg"},
            {"name": "Sorghum", "category": "Grains", "unit_price": Decimal("22.50"), "unit": "kg"},
            {"name": "Peas", "category": "Legumes", "unit_price": Decimal("42.00"), "unit": "kg"},
            {"name": "Lentils", "category": "Legumes", "unit_price": Decimal("48.50"), "unit": "kg"},
            {"name": "Garlic", "category": "Root Vegetables", "unit_price": Decimal("55.00"), "unit": "kg"},
            {"name": "Radishes", "category": "Root Vegetables", "unit_price": Decimal("14.25"), "unit": "kg"},
            {"name": "Beets", "category": "Root Vegetables", "unit_price": Decimal("19.75"), "unit": "kg"},
        ]
        
        products = []
        for data in products_data:
            product = Product(
                name=data["name"],
                category=data["category"],
                description=f"Fresh {data['name'].lower()} from farm",
                unit_price=data["unit_price"],
                unit=data["unit"],
                is_active=True
            )
            db.add(product)
            products.append(product)
        
        db.commit()
        for p in products:
            db.refresh(p)
        
        # Add sample transactions
        now = datetime.now()
        for i in range(1, 46):
            date = now - timedelta(days=45-i)
            for product in products[0:5]:
                transaction = Transaction(
                    product_id=product.id,
                    quantity=50 + (i * 2),
                    unit_price=product.unit_price,
                    total_price=Decimal(50 + (i * 2)) * product.unit_price,
                    transaction_date=date.date(),
                    notes=f"Regular sale on {date.date()}"
                )
                db.add(transaction)
        
        db.commit()
        
        # Add sample forecasts
        for i in range(1, 16):
            date = now + timedelta(days=i)
            for product in products[0:4]:
                forecast = Forecast(
                    product_id=product.id,
                    forecast_date=date.date(),
                    predicted_demand=100 + (i * 10),
                    confidence_lower=Decimal("80") + Decimal(i * 8),
                    confidence_upper=Decimal("120") + Decimal(i * 12),
                    model_type="prophet",
                    accuracy_score=Decimal("0.87")
                )
                db.add(forecast)
        
        db.commit()
        
        # Add sample recommendations
        statuses = ["pending", "approved", "implemented"]
        for i, product in enumerate(products[0:10]):
            recommendation = InventoryRecommendation(
                product_id=product.id,
                recommended_quantity=500 + (i * 100),
                current_quantity=200 + (i * 50),
                min_quantity=100,
                max_quantity=1000,
                recommendation_date=now.date(),
                reason=f"Low stock detected for {product.name}. Recommended reorder soon.",
                status=statuses[i % len(statuses)]
            )
            db.add(recommendation)
        
        db.commit()
        
        return {
            "message": "Database seeded successfully",
            "products": len(products),
            "transactions": 225,
            "forecasts": 60,
            "recommendations": 10,
            "status": "success"
        }
    
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error seeding database: {str(e)}"
        )
