#!/bin/bash

# PostgreSQL Database Setup Script for Agricultural Statistics Dashboard

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Load environment variables
set -a
source .env
set +a

echo -e "${YELLOW}========================================${NC}"
echo -e "${YELLOW}PostgreSQL Database Setup${NC}"
echo -e "${YELLOW}========================================${NC}"

# Check if PostgreSQL is installed
if ! command -v psql &> /dev/null; then
    echo -e "${RED}PostgreSQL is not installed.${NC}"
    echo -e "${YELLOW}Install it with:${NC}"
    echo -e "  Ubuntu/Debian: ${GREEN}sudo apt-get install postgresql postgresql-contrib${NC}"
    echo -e "  macOS: ${GREEN}brew install postgresql${NC}"
    echo -e "  Windows: Download from https://www.postgresql.org/download/windows/${NC}"
    exit 1
fi

echo -e "${GREEN}PostgreSQL found.${NC}"

# Check if PostgreSQL service is running
if ! pg_isready -h $DB_HOST -U $DB_USER &> /dev/null; then
    echo -e "${YELLOW}PostgreSQL service is not running. Starting...${NC}"
    # For Ubuntu/Debian
    if command -v systemctl &> /dev/null; then
        sudo systemctl start postgresql
    fi
fi

# Create database
echo -e "${YELLOW}Creating database: ${GREEN}$DB_NAME${NC}"
PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -U $DB_USER -c "CREATE DATABASE $DB_NAME;" 2>/dev/null || \
    echo -e "${YELLOW}Database already exists or error occurred.${NC}"

# Create tables (you can add more SQL commands here)
echo -e "${YELLOW}Setting up database schema...${NC}"
PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        username VARCHAR(80) UNIQUE NOT NULL,
        email VARCHAR(120) UNIQUE NOT NULL,
        password VARCHAR(255) NOT NULL,
        is_admin BOOLEAN DEFAULT FALSE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS products (
        id SERIAL PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        category VARCHAR(100),
        unit_price DECIMAL(10, 2),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS transactions (
        id SERIAL PRIMARY KEY,
        product_id INTEGER NOT NULL REFERENCES products(id),
        quantity INTEGER NOT NULL,
        price DECIMAL(10, 2),
        transaction_date DATE NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS forecasts (
        id SERIAL PRIMARY KEY,
        product_id INTEGER NOT NULL REFERENCES products(id),
        forecast_date DATE NOT NULL,
        predicted_demand INTEGER,
        confidence_interval DECIMAL(5, 2),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS inventory_recommendations (
        id SERIAL PRIMARY KEY,
        product_id INTEGER NOT NULL REFERENCES products(id),
        recommended_quantity INTEGER,
        current_quantity INTEGER,
        recommendation_date DATE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
"

echo -e "${GREEN}✓ Database setup complete!${NC}"
echo -e "${YELLOW}Database URL: ${GREEN}$DATABASE_URL${NC}"
