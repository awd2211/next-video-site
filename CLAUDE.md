# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

VideoSite is a full-stack video streaming platform with three main components:
- **Backend**: FastAPI-based REST API (`/backend`)
- **Frontend**: React user-facing application (`/frontend`)
- **Admin Frontend**: React admin dashboard (`/admin-frontend`)

The architecture uses PostgreSQL for data, Redis for caching, MinIO for object storage, and is fully containerized with Docker.

## Development Commands

> **Tip**: Run `make help` to see all available commands with descriptions.

### Quick Start
```bash
# Start infrastructure (PostgreSQL, Redis, MinIO)
make infra-up

# Install all dependencies
make all-install

# Initialize database
make db-init

# Run services in separate terminals
make backend-run    # Terminal 1 - Backend API on :8000
make frontend-run   # Terminal 2 - User frontend on :3000
make admin-run      # Terminal 3 - Admin frontend on :3001
```

### Backend Development
```bash
# Activate Python virtual environment
cd backend && source venv/bin/activate

# Run backend with hot reload
make backend-run
# Or: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Database migrations
make db-migrate MSG="your message"    # Create migration
make db-upgrade                       # Apply migrations
alembic downgrade -1                  # Rollback one migration
alembic history                       # View migration history

# Code formatting
make format-backend                   # Format with Black and isort
make format-check                     # Check formatting without changes
make format                           # Format all code

# Run tests
pytest                                # Run all tests
pytest tests/test_specific.py         # Run specific test file
pytest -v                             # Verbose output
pytest -k "test_name"                 # Run tests matching pattern
pytest --cov=app --cov-report=html    # Generate coverage report
```

### Frontend Development
```bash
# User frontend
cd frontend
pnpm install
pnpm run dev          # Development server
pnpm run build        # Production build
pnpm run preview      # Preview production build
pnpm run lint         # Run ESLint

# Admin frontend
cd admin-frontend
pnpm install
pnpm run dev          # Development server
pnpm run build        # Production build
```

### Infrastructure
```bash
make infra-up         # Start PostgreSQL, Redis, MinIO
make infra-down       # Stop infrastructure
make clean            # Remove all containers and volumes
docker-compose -f docker-compose.dev.yml ps    # Check status
```

### Docker (Full Deployment)
```bash
docker-compose up -d                           # Start all services
docker-compose exec backend alembic upgrade head  # Run migrations
docker-compose logs -f backend                 # View logs
docker-compose restart backend                 # Restart service
```

## Architecture

### Backend Structure (`/backend/app`)

**Core Files:**
- `main.py` - FastAPI app initialization, middleware, and route registration
- `config.py` - Pydantic settings (loads from `.env`)
- `database.py` - SQLAlchemy async engine, session management, connection pooling

**Key Directories:**
- `models/` - SQLAlchemy ORM models (User, Video, Comment, etc.)
- `schemas/` - Pydantic schemas for request/response validation
- `api/` - Public API endpoints (auth, videos, search, categories)
- `admin/` - Admin API endpoints (video management, stats, logs, etc.)
- `utils/` - Utilities (security, dependencies, cache, email, MinIO client)
- `middleware/` - Custom middleware (operation logging)

**Important Patterns:**

1. **Authentication System:**
   - JWT tokens (access + refresh) via `utils/security.py`
   - User auth: `get_current_user()` dependency in `utils/dependencies.py`
   - Admin auth: `get_current_admin_user()` dependency
   - Superadmin: `get_current_superadmin()` dependency
   - Separate User and AdminUser models

2. **Database Sessions:**
   - Async SQLAlchemy with asyncpg driver
   - Connection pool configured in `database.py` (20 base + 40 overflow)
   - Use `get_db()` dependency for session injection
   - Always commit/rollback properly (handled by dependency)

3. **Caching Strategy:**
   - Redis caching via `utils/cache.py`
   - Cache decorator pattern for function results
   - TTL-based expiration
   - Cache warming on startup via `utils/cache_warmer.py`
   - Use `CacheManager` class for operations

4. **File Storage:**
   - MinIO object storage via `utils/minio_client.py`
   - Handles video files, images, thumbnails
   - Bucket: `videos` (configurable)
   - Pre-signed URLs for secure access

5. **Middleware:**
   - CORS configured for frontend origins
   - GZip compression (minimum 1000 bytes)
   - Rate limiting via SlowAPI
   - Operation logging middleware for audit trails

### Frontend Structure (`/frontend/src`)

- **React 18** with TypeScript and Vite
- **TailwindCSS** for styling
- **TanStack Query** for data fetching and caching
- **React Router** for navigation
- **Video.js** for video playback with YouTube-like controls
- **i18n** for internationalization (locale files in `src/i18n/locales/`)

**Key Components:**
- `VideoPlayer/` - Full-featured video player with keyboard shortcuts
- `VideoCard/` - Reusable video display card
- `Header/` & `Footer/` - Layout components
- `Layout/` - Page wrapper component

**Services:**
- API client configuration (axios with baseURL)
- Query hooks for videos, categories, search

**Internationalization:**
- Locale files: `src/i18n/locales/en-US.json`, `zh-CN.json`
- Add new translations by updating locale JSON files
- Use i18n hooks in components for translated text

### Admin Frontend Structure (`/admin-frontend/src`)

- **Ant Design** UI component library
- **Ant Design Charts** for data visualization
- **React Router** for navigation
- **i18n** for internationalization (locale files in `src/i18n/locales/`)
- **Dark/Light theme** support with theme context

**Key Pages:**
- `Dashboard/` - Statistics and analytics
- `Videos/` - Video management (CRUD, bulk operations)
- `Users/` - User management and banning
- `Comments/` - Comment moderation
- `Settings/` - System configuration
- `Logs/` - Operation logs
- `Banners/`, `Announcements/` - Content management

**Internationalization:**
- Same i18n setup as user frontend
- Supports both English and Chinese locales
- Theme preferences persisted in localStorage

### Database Models

**Core Models:**
- `User` - Regular users (separate from admin)
- `AdminUser` - Admin/superadmin users with RBAC
- `Video` - Videos with metadata, relationships to categories/countries/actors
- `Category`, `Country`, `Tag` - Classification
- `Actor`, `Director` - People involved in videos
- `Comment`, `Rating` - User interactions
- `Favorite`, `WatchHistory` - User activity
- `Banner`, `Recommendation`, `Announcement` - Operational content
- `OperationLog` - Audit trail
- `Role`, `Permission` - RBAC system
- `EmailConfig`, `SystemSettings` - Configuration

**Important Relationships:**
- Videos have many-to-many with Categories, Tags, Actors, Directors
- Comments belong to Users and Videos (with moderation status)
- Watch history tracks progress and completion

## Development Workflow

### Adding a New Feature

1. **Backend API:**
   - Create/update model in `backend/app/models/`
   - Run `make db-migrate MSG="description"` and `make db-upgrade`
   - Add Pydantic schema in `backend/app/schemas/`
   - Implement endpoint in `backend/app/api/` or `backend/app/admin/`
   - Register router in `main.py`
   - Test via Swagger UI at http://localhost:8000/api/docs

2. **Frontend:**
   - Create service function in `src/services/`
   - Build React component in `src/components/` or page in `src/pages/`
   - Add route to router if needed
   - Use TanStack Query for data fetching

3. **Admin Frontend:**
   - Similar to frontend but use Ant Design components
   - Add to admin navigation/menu

### Working with Database

- **Migrations are REQUIRED** for any model changes
- Alembic auto-generates migrations but ALWAYS review them
- Test migrations on dev database before production
- Never skip migrations or modify database directly

### Authentication Flow

**User Login:**
1. POST `/api/v1/auth/login` → returns access + refresh tokens
2. Frontend stores tokens (localStorage or secure storage)
3. Include `Authorization: Bearer {access_token}` in requests
4. Refresh tokens via `/api/v1/auth/refresh` when expired

**Admin Login:**
1. Use separate AdminUser credentials
2. Token payload includes `is_admin: true`
3. Admin endpoints check admin status via dependencies

### Caching Strategy

- **Video Lists:** Cache with TTL (5-15 minutes)
- **Categories/Countries:** Long TTL (1 hour) - rarely change
- **User-Specific Data:** No caching or short TTL
- **Statistics:** Cache with 5-minute TTL
- Use cache invalidation on updates (delete cache keys)

## Configuration

### Environment Variables (backend/.env)

Required:
- `DATABASE_URL` - Async Postgres connection (postgresql+asyncpg://...)
- `DATABASE_URL_SYNC` - Sync connection for Alembic (postgresql://...)
- `SECRET_KEY` - Application secret
- `JWT_SECRET_KEY` - JWT signing key
- `REDIS_URL` - Redis connection
- `MINIO_ENDPOINT`, `MINIO_ACCESS_KEY`, `MINIO_SECRET_KEY` - Object storage

Optional:
- `DEBUG=True` - Enable SQL logging
- `SMTP_*` - Email configuration
- `ELASTICSEARCH_URL` - For full-text search (future)

### Default Ports

- Backend API: 8000
- Frontend: 3000 (Vite dev server on 5173)
- Admin Frontend: 3001
- PostgreSQL: 5432
- Redis: 6379
- MinIO API: 9000
- MinIO Console: 9001

## Testing

- Backend tests in `backend/tests/` (pytest + pytest-asyncio)
- Use httpx AsyncClient for API testing
- Test database should be separate (configure via env)

## API Documentation

- Interactive Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc
- All endpoints automatically documented via FastAPI

## Common Tasks

### Create Admin User
```python
cd backend && source venv/bin/activate
python << EOF
from app.database import SessionLocal
from app.models.user import AdminUser
from app.utils.security import get_password_hash

db = SessionLocal()
admin = AdminUser(
    email='admin@example.com',
    username='admin',
    hashed_password=get_password_hash('admin123'),
    full_name='Admin',
    is_active=True,
    is_superadmin=True
)
db.add(admin)
db.commit()
EOF
```

### Check Database Connection Pool Status
```python
from app.database import get_pool_status
status = get_pool_status()
# Returns: pool_size, checked_in, checked_out, overflow
```

### Clear All Cache
```python
from app.utils.cache import get_redis
client = await get_redis()
await client.flushdb()
```

## Important Notes

- **Never commit `.env` files** - use `.env.example` as template
- **Always use async/await** for database operations in FastAPI routes
- **Use dependencies** for auth instead of manual token checking
- **Pydantic validates** all request/response data automatically
- **MinIO buckets** must be created before first use
- **Frontend proxies** API requests via Vite config (avoid CORS in dev)
- **Admin routes** are prefixed with `/api/v1/admin/`
- **Rate limiting** is enabled on all endpoints via SlowAPI
- **Operation logs** are automatically recorded for admin actions via middleware
- **Database pool** is optimized (20+40 connections) - don't create manual connections
- **Use `pnpm`** not npm for frontend dependencies
