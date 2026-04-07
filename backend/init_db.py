#!/usr/bin/env python
"""
Initialize database with sample data for Agricultural Statistics Dashboard
Run this once to populate the database with realistic agricultural products and data
"""

import sys
import os
from datetime import datetime, timedelta
from decimal import Decimal

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

from app.db.database import Base, engine, SessionLocal
from app.models.models import User, Product, Transaction, Forecast, InventoryRecommendation

def init_database():
    """Create all tables in the database"""
    print("📦 Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created")

def add_default_user():
    """Add a default user for authentication"""
    db = SessionLocal()
    
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(User.username == "somi").first()
        if existing_user:
            print("⚠️  User 'somi' already exists, skipping user creation")
            return
        
        print("\n👤 Adding default user...")
        
        # Create default user with simple password (in production, use hashing)
        user = User(
            username="somi",
            email="somi@agric-stat.local",
            password="1234",  # Simple password for testing
            full_name="System User",
            is_admin=True,
            is_active=True
        )
        db.add(user)
        db.commit()
        print("✅ Default user 'somi' created successfully")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error creating default user: {e}")
        raise
    finally:
        db.close()

def add_sample_data():
    """Add sample agricultural products and related data"""
    db = SessionLocal()
    
    try:
        # Check if data already exists
        existing_products = db.query(Product).count()
        if existing_products > 0:
            print(f"⚠️  Database already has {existing_products} products, skipping sample data")
            return
        
        print("\n📊 Adding sample products...")
        
        # Sample agricultural products - Extended catalog
        products_data = [
            {
                "name": "Tomatoes",
                "category": "Vegetables",
                "description": "Fresh farm tomatoes - red, ripe and juicy",
                "unit_price": Decimal("25.50"),
                "unit": "kg",
                "is_active": True
            },
            {
                "name": "Maize (Corn)",
                "category": "Grains",
                "description": "High-quality maize for consumption",
                "unit_price": Decimal("15.00"),
                "unit": "kg",
                "is_active": True
            },
            {
                "name": "Beans",
                "category": "Legumes",
                "description": "Dried beans - protein rich",
                "unit_price": Decimal("30.00"),
                "unit": "kg",
                "is_active": True
            },
            {
                "name": "Potatoes",
                "category": "Root Vegetables",
                "description": "Fresh potatoes directly from farm",
                "unit_price": Decimal("18.75"),
                "unit": "kg",
                "is_active": True
            },
            {
                "name": "Carrots",
                "category": "Vegetables",
                "description": "Orange carrots - sweet and crunchy",
                "unit_price": Decimal("22.00"),
                "unit": "kg",
                "is_active": True
            },
            {
                "name": "Cabbage",
                "category": "Vegetables",
                "description": "Fresh green cabbage heads",
                "unit_price": Decimal("12.50"),
                "unit": "kg",
                "is_active": True
            },
            {
                "name": "Onions",
                "category": "Root Vegetables",
                "description": "Golden onions - aromatic and flavorful",
                "unit_price": Decimal("20.00"),
                "unit": "kg",
                "is_active": True
            },
            {
                "name": "Wheat",
                "category": "Grains",
                "description": "Premium wheat for flour and bread",
                "unit_price": Decimal("45.00"),
                "unit": "kg",
                "is_active": True
            },
            {
                "name": "Lettuce",
                "category": "Vegetables",
                "description": "Crisp green leafy lettuce",
                "unit_price": Decimal("28.00"),
                "unit": "kg",
                "is_active": True
            },
            {
                "name": "Peppers",
                "category": "Vegetables",
                "description": "Colorful bell peppers - red, yellow, green",
                "unit_price": Decimal("32.50"),
                "unit": "kg",
                "is_active": True
            },
            {
                "name": "Broccoli",
                "category": "Vegetables",
                "description": "Fresh green broccoli florets",
                "unit_price": Decimal("26.75"),
                "unit": "kg",
                "is_active": True
            },
            {
                "name": "Spinach",
                "category": "Vegetables",
                "description": "Organic fresh spinach leaves",
                "unit_price": Decimal("35.00"),
                "unit": "kg",
                "is_active": True
            },
            {
                "name": "Cucumbers",
                "category": "Vegetables",
                "description": "Fresh green cucumbers",
                "unit_price": Decimal("18.50"),
                "unit": "kg",
                "is_active": True
            },
            {
                "name": "Rice",
                "category": "Grains",
                "description": "Long grain white rice",
                "unit_price": Decimal("38.00"),
                "unit": "kg",
                "is_active": True
            },
            {
                "name": "Sorghum",
                "category": "Grains",
                "description": "Nutritious sorghum grain",
                "unit_price": Decimal("22.50"),
                "unit": "kg",
                "is_active": True
            },
            {
                "name": "Peas",
                "category": "Legumes",
                "description": "Green peas - fresh and sweet",
                "unit_price": Decimal("42.00"),
                "unit": "kg",
                "is_active": True
            },
            {
                "name": "Lentils",
                "category": "Legumes",
                "description": "Red and brown lentils mix",
                "unit_price": Decimal("48.50"),
                "unit": "kg",
                "is_active": True
            },
            {
                "name": "Garlic",
                "category": "Root Vegetables",
                "description": "Fresh garlic bulbs",
                "unit_price": Decimal("55.00"),
                "unit": "kg",
                "is_active": True
            },
            {
                "name": "Radishes",
                "category": "Root Vegetables",
                "description": "Fresh red radishes",
                "unit_price": Decimal("14.25"),
                "unit": "kg",
                "is_active": True
            },
            {
                "name": "Beets",
                "category": "Root Vegetables",
                "description": "Purple beets with greens",
                "unit_price": Decimal("19.75"),
                "unit": "kg",
                "is_active": True
            }
        ]
        
        products = []
        for prod_data in products_data:
            product = Product(**prod_data)
            db.add(product)
            products.append(product)
        
        db.commit()
        print(f"✅ Added {len(products)} sample products")
        
        # Refresh to get IDs
        db.refresh(products[0])
        
        # Add sample transactions (90+ total)
        print("📈 Adding sample transactions...")
        now = datetime.now()
        transactions = []
        
        for i in range(1, 46):  # 45 days of transactions
            date = now - timedelta(days=45-i)
            for product in products[0:5]:  # Use first 5 products for variety
                transaction = Transaction(
                    product_id=product.id,
                    user_id=None,  # No user required for now
                    quantity=50 + (i * 2),
                    unit_price=product.unit_price,
                    total_price=Decimal(50 + (i * 2)) * product.unit_price,
                    transaction_date=date.date(),
                    notes=f"Regular sale on {date.date()}"
                )
                db.add(transaction)
                transactions.append(transaction)
        
        db.commit()
        print(f"✅ Added {len(transactions)} sample transactions")
        
        # Add sample forecasts (30+ total)
        print("📊 Adding sample forecasts...")
        forecasts = []
        
        for i in range(1, 16):  # 15 days of forecasts
            date = now + timedelta(days=i)
            for product in products[0:4]:  # Use first 4 products
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
                forecasts.append(forecast)
        
        db.commit()
        print(f"✅ Added {len(forecasts)} sample forecasts")
        
        # Add sample recommendations (10+ total with various statuses)
        print("💡 Adding sample recommendations...")
        recommendations = []
        
        statuses = ["pending", "approved", "implemented"]
        for i, product in enumerate(products[0:10]):  # Use first 10 products
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
            recommendations.append(recommendation)
        
        db.commit()
        print(f"✅ Added {len(recommendations)} sample recommendations")
        
        print("\n" + "="*50)
        print("✨ DATABASE INITIALIZED WITH SAMPLE DATA")
        print("="*50)
        print(f"📦 Products: {len(products)}")
        print(f"📈 Transactions: {len(transactions)}")
        print(f"📊 Forecasts: {len(forecasts)}")
        print(f"💡 Recommendations: {len(recommendations)}")
        print("\n🌐 Visit API Docs to see data:")
        print("   http://localhost:8000/docs")
        print("\n🎨 Visit Frontend to see charts:")
        print("   http://localhost:3000")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error adding sample data: {e}")
        raise
    finally:
        db.close()

def reset_database():
    """Clear all data from database"""
    print("⚠️  Clearing all database data...")
    Base.metadata.drop_all(bind=engine)
    print("✅ Database cleared")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Initialize database for Agricultural Statistics Dashboard"
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Clear all data before initializing"
    )
    parser.add_argument(
        "--include-data",
        action="store_true",
        help="Include sample product data (optional)"
    )
    
    args = parser.parse_args()
    
    print("\n🌾 Agricultural Statistics Dashboard - Database Initialization\n")
    
    if args.reset:
        reset_database()
    
    init_database()
    
    # Always create default user
    add_default_user()
    
    # Only add sample products if explicitly requested with --include-data flag
    if args.include_data:
        add_sample_data()
    
    print("\n" + "="*50)
    print("✅ All done! Your app is ready to use.")
    print("="*50 + "\n")
