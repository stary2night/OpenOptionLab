#!/bin/bash
# OpenOptions Lab API - Quick Start Script

set -e

echo "🚀 OpenOptions Lab API - Quick Start"
echo "======================================"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Check if services are already running
if docker-compose ps | grep -q "Up"; then
    echo "⚠️  Services are already running. Stopping them first..."
    docker-compose down
fi

# Start services
echo ""
echo "📦 Starting services with Docker Compose..."
docker-compose up -d

# Wait for services to be ready
echo ""
echo "⏳ Waiting for services to be ready..."
sleep 5

# Check database connection
echo ""
echo "🔍 Checking database connection..."
until docker-compose exec -T db pg_isready -U postgres > /dev/null 2>&1; do
    echo "   Waiting for PostgreSQL..."
    sleep 2
done
echo "✅ PostgreSQL is ready"

# Run database migrations
echo ""
echo "🗄️  Running database migrations..."
docker-compose exec api alembic upgrade head

# Check API health
echo ""
echo "🏥 Checking API health..."
sleep 2
if curl -s http://localhost:8000/api/v1/health/ > /dev/null; then
    echo "✅ API is healthy"
else
    echo "⚠️  API health check failed, but service may still be starting..."
fi

# Print summary
echo ""
echo "======================================"
echo "✅ OpenOptions Lab API is ready!"
echo "======================================"
echo ""
echo "📍 API Endpoints:"
echo "   - API Docs:     http://localhost:8000/docs"
echo "   - Health Check: http://localhost:8000/api/v1/health/"
echo "   - WebSocket:    ws://localhost:8000/ws/market"
echo ""
echo "🛠️  Useful commands:"
echo "   - View logs:    docker-compose logs -f api"
echo "   - Stop:         docker-compose down"
echo "   - Restart:      docker-compose restart"
echo ""
echo "🧪 Run tests:"
echo "   cd tests && python test_user_system.py"
echo ""
