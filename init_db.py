#!/usr/bin/env python
"""
Database initialization script using SQLAlchemy ORM
This script creates all tables based on the defined models
"""

import os
import sys
from dotenv import load_dotenv

# Add the backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

load_dotenv()

from app.db.database import Base, engine

def init_db():
    """Create all database tables"""
    print("🔧 Initializing database tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Database initialization complete!")

if __name__ == "__main__":
    init_db()
