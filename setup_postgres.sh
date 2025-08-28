#!/bin/bash
# Setup and start PostgreSQL for Outlook API

echo "🐘 Setting up PostgreSQL for Outlook API..."

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop."
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "📋 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please update the .env file with your Azure credentials!"
fi

# Stop existing containers
echo "🛑 Stopping existing containers..."
docker-compose down

# Start PostgreSQL
echo "🚀 Starting PostgreSQL container..."
docker-compose up -d postgres

# Wait for PostgreSQL to be ready
echo "⏳ Waiting for PostgreSQL to be ready..."
timeout=60
count=0
until docker-compose exec -T postgres pg_isready -U postgres -d outlook_api >/dev/null 2>&1; do
    sleep 2
    count=$((count + 2))
    if [ $count -ge $timeout ]; then
        echo "❌ PostgreSQL failed to start within $timeout seconds"
        exit 1
    fi
    echo "   ... waiting ($count/${timeout}s)"
done

echo "✅ PostgreSQL is ready!"

# Install Python dependencies
echo "📦 Installing Python dependencies..."
.venv/bin/pip install -r requirements.txt

# Test database connection
echo "🔍 Testing database connection..."
python3 -c "
import os
import sys
sys.path.insert(0, '.')
from dotenv import load_dotenv
load_dotenv()

try:
    import psycopg2
    from models.database import DATABASE_CONFIG
    
    conn = psycopg2.connect(
        host=DATABASE_CONFIG['host'],
        port=DATABASE_CONFIG['port'],
        database=DATABASE_CONFIG['database'],
        user=DATABASE_CONFIG['user'],
        password=DATABASE_CONFIG['password']
    )
    conn.close()
    print('✅ Database connection successful!')
except Exception as e:
    print(f'❌ Database connection failed: {e}')
    sys.exit(1)
"

echo ""
echo "🎉 PostgreSQL setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Update your .env file with Azure credentials"
echo "2. Start the API server: .venv/bin/python -m uvicorn main:app --reload --ssl-keyfile=certs/key.pem --ssl-certfile=certs/cert.pem"
echo "3. Visit: https://localhost:8000/client"
echo ""
echo "🛠️  Database Management:"
echo "   - PostgreSQL: http://localhost:5432"
echo "   - pgAdmin: http://localhost:5050 (admin@outlook-api.com / admin)"
echo "   - Stop: docker-compose down"
echo ""
