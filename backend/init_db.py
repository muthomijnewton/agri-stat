#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Initialize database with sample data for Agricultural Statistics Dashboard
Run this once to populate the database with realistic agricultural products and data
"""

import sys
import os
import logging

# Ensure stdout/stderr use UTF-8 on Windows (avoids cp1252 UnicodeEncodeError).
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

from datetime import datetime, timedelta
from decimal import Decimal

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

from app.db.database import Base, engine, SessionLocal
from app.models.models import User, Product, Transaction, Forecast, InventoryRecommendation
from app.core.security import get_password_hash, password_is_hashed

def init_database():
    """Create all tables in the database"""
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created")

def add_default_user():
    """Add a default user for authentication"""
    db = SessionLocal()
    
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(User.username == "admin@agri").first()
        if existing_user:
            if not password_is_hashed(existing_user.password):
                existing_user.password = get_password_hash(existing_user.password)
                db.commit()
                logger.info("Updated default user password hash")
            logger.warning("User 'admin@agri' already exists, skipping user creation")
            # Still run column migrations even if user exists
            _migrate_add_transaction_type()
            return
        
        logger.info("Adding default user...")
        
        # Create default user with simple password (in production, use hashing)
        user = User(
            username="admin@agri",
            email="admin@agric-stat.local",
            password=get_password_hash("1234"),
            full_name="Admin User",
            is_admin=True,
            is_active=True
        )
        db.add(user)
        db.commit()
        logger.info("Default user 'admin@agri' created successfully")
        _migrate_add_transaction_type()
        
    except Exception as e:
        db.rollback()
        logger.error("Error creating default user: %s", e)
        raise
    finally:
        db.close()


def _migrate_add_transaction_type():
    """
    Idempotent migration: add transaction_type column to existing transactions
    tables that were created before this column was introduced.
    Safe to call on every startup — does nothing if the column already exists.
    """
    import sqlite3
    from app.core.config import DATABASE_URL

    # Only applies to SQLite; PostgreSQL users should run Alembic
    if not DATABASE_URL.startswith("sqlite"):
        return

    db_path = DATABASE_URL.replace("sqlite:///", "")
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(transactions)")
        columns = [row[1] for row in cursor.fetchall()]
        if "transaction_type" not in columns:
            cursor.execute(
                "ALTER TABLE transactions ADD COLUMN transaction_type VARCHAR(20) NOT NULL DEFAULT 'sale'"
            )
            conn.commit()
            logger.info("Migration applied: added transaction_type column to transactions table")
        conn.close()
    except Exception as e:
        logger.warning("Could not apply transaction_type migration: %s", e)

def add_sample_data():
    """Add sample agricultural products and related data"""
    db = SessionLocal()
    
    try:
        # Check if data already exists
        existing_products = db.query(Product).count()
        if existing_products > 0:
            logger.warning("Database already has %d products, skipping sample data", existing_products)
            return
        
        logger.info("Adding sample products...")
        
        # Sample agricultural products — prices are realistic Kenyan market
        # approximates (KES per kg, retail/wholesale, 2025/2026).
        products_data = [
            {
                "name": "Tomatoes",
                "category": "Vegetables",
                "description": "Fresh farm tomatoes - red, ripe and juicy",
                "unit_price": Decimal("80.00"),
                "unit": "kg",
                "is_active": True
            },
            {
                "name": "Maize (Corn)",
                "category": "Grains",
                "description": "High-quality maize for consumption and livestock feed",
                "unit_price": Decimal("55.00"),
                "unit": "kg",
                "is_active": True
            },
            {
                "name": "Beans",
                "category": "Legumes",
                "description": "Dried rosecoco beans - protein rich",
                "unit_price": Decimal("160.00"),
                "unit": "kg",
                "is_active": True
            },
            {
                "name": "Potatoes",
                "category": "Root Vegetables",
                "description": "Fresh Irish potatoes directly from farm",
                "unit_price": Decimal("50.00"),
                "unit": "kg",
                "is_active": True
            },
            {
                "name": "Carrots",
                "category": "Vegetables",
                "description": "Orange carrots - sweet and crunchy",
                "unit_price": Decimal("60.00"),
                "unit": "kg",
                "is_active": True
            },
            {
                "name": "Cabbage",
                "category": "Vegetables",
                "description": "Fresh green cabbage heads",
                "unit_price": Decimal("40.00"),
                "unit": "kg",
                "is_active": True
            },
            {
                "name": "Onions",
                "category": "Root Vegetables",
                "description": "Red onions - aromatic and flavorful",
                "unit_price": Decimal("90.00"),
                "unit": "kg",
                "is_active": True
            },
            {
                "name": "Wheat",
                "category": "Grains",
                "description": "Premium wheat grain for flour and bread",
                "unit_price": Decimal("65.00"),
                "unit": "kg",
                "is_active": True
            },
            {
                "name": "Sukuma Wiki (Kale)",
                "category": "Vegetables",
                "description": "Fresh collard greens - staple leafy vegetable",
                "unit_price": Decimal("30.00"),
                "unit": "kg",
                "is_active": True
            },
            {
                "name": "Capsicum (Bell Pepper)",
                "category": "Vegetables",
                "description": "Colorful bell peppers - red, yellow, green",
                "unit_price": Decimal("200.00"),
                "unit": "kg",
                "is_active": True
            },
            {
                "name": "Broccoli",
                "category": "Vegetables",
                "description": "Fresh green broccoli florets",
                "unit_price": Decimal("150.00"),
                "unit": "kg",
                "is_active": True
            },
            {
                "name": "Spinach",
                "category": "Vegetables",
                "description": "Fresh spinach leaves",
                "unit_price": Decimal("50.00"),
                "unit": "kg",
                "is_active": True
            },
            {
                "name": "Cucumbers",
                "category": "Vegetables",
                "description": "Fresh green cucumbers",
                "unit_price": Decimal("60.00"),
                "unit": "kg",
                "is_active": True
            },
            {
                "name": "Rice (Pishori)",
                "category": "Grains",
                "description": "Premium Kenyan Pishori long-grain rice",
                "unit_price": Decimal("200.00"),
                "unit": "kg",
                "is_active": True
            },
            {
                "name": "Sorghum",
                "category": "Grains",
                "description": "Nutritious sorghum grain",
                "unit_price": Decimal("70.00"),
                "unit": "kg",
                "is_active": True
            },
            {
                "name": "Green Peas",
                "category": "Legumes",
                "description": "Fresh green peas",
                "unit_price": Decimal("120.00"),
                "unit": "kg",
                "is_active": True
            },
            {
                "name": "Lentils",
                "category": "Legumes",
                "description": "Red and brown lentils mix",
                "unit_price": Decimal("180.00"),
                "unit": "kg",
                "is_active": True
            },
            {
                "name": "Garlic",
                "category": "Root Vegetables",
                "description": "Fresh garlic bulbs",
                "unit_price": Decimal("500.00"),
                "unit": "kg",
                "is_active": True
            },
            {
                "name": "Sweet Potatoes",
                "category": "Root Vegetables",
                "description": "Orange-fleshed sweet potatoes",
                "unit_price": Decimal("50.00"),
                "unit": "kg",
                "is_active": True
            },
            {
                "name": "Avocado",
                "category": "Fruits",
                "description": "Hass avocados - export and local grade",
                "unit_price": Decimal("100.00"),
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
        logger.info("Added %d sample products", len(products))
        
        # Refresh to get IDs
        db.refresh(products[0])
        
        # Add sample transactions (90+ total)
        logger.info("Adding sample transactions...")
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
        logger.info("Added %d sample transactions", len(transactions))
        
        # Add sample forecasts (30+ total)
        logger.info("Adding sample forecasts...")
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
        logger.info("Added %d sample forecasts", len(forecasts))
        
        # Add sample recommendations (10+ total with various statuses)
        logger.info("Adding sample recommendations...")
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
        logger.info("Added %d sample recommendations", len(recommendations))
        
        logger.info(
            "Database initialized with sample data — "
            "Products: %d | Transactions: %d | Forecasts: %d | Recommendations: %d",
            len(products), len(transactions), len(forecasts), len(recommendations),
        )
        logger.info("API docs: http://localhost:8000/docs")
        logger.info("Frontend: http://localhost:3000")
        
    except Exception as e:
        db.rollback()
        logger.error("Error adding sample data: %s", e)
        raise
    finally:
        db.close()

def reset_database():
    """Clear all data from database"""
    logger.warning("Clearing all database data...")
    Base.metadata.drop_all(bind=engine)
    logger.info("Database cleared")

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
    
    logger.info("Agricultural Statistics Dashboard - Database Initialization")
    
    if args.reset:
        reset_database()
    
    init_database()
    
    # Always create default user
    add_default_user()
    
    # Only add sample products if explicitly requested with --include-data flag
    if args.include_data:
        add_sample_data()
    
    logger.info("All done! Your app is ready to use.")
