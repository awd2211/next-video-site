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
make frontend-run   # Terminal 2 - User frontend on :5173 (proxies to 3000)
make admin-run      # Terminal 3 - Admin frontend on :5173 (proxies to 3001)
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
pnpm run dev          # Development server on :5173
pnpm run build        # Production build
pnpm run preview      # Preview production build
pnpm run lint         # Run ESLint

# Admin frontend
cd admin-frontend
pnpm install
pnpm run dev          # Development server on :5173
pnpm run build        # Production build
pnpm run lint         # Run ESLint
pnpm run type-check   # TypeScript type checking
```

### Infrastructure
```bash
make infra-up         # Start PostgreSQL, Redis, MinIO
make infra-down       # Stop infrastructure services
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
- `main.py` - FastAPI app initialization, middleware stack, route registration, and global error handlers
- `config.py` - Pydantic settings (loads from `.env`)
- `database.py` - SQLAlchemy async engine, session management, connection pooling

**Key Directories:**
- `models/` - SQLAlchemy ORM models (User, Video, Comment, Notification, Dashboard, etc.)
- `schemas/` - Pydantic schemas for request/response validation
- `api/` - Public API endpoints (auth, videos, search, categories, websocket)
- `admin/` - Admin API endpoints (video management, stats, logs, AI management, system health, etc.)
- `utils/` - Utilities (security, dependencies, cache, email, MinIO client, logging, notifications, storage monitoring)
- `middleware/` - Custom middleware (see Middleware Stack section)

**Important Patterns:**

1. **Authentication System:**
   - JWT tokens (access + refresh) via `utils/security.py`
   - User auth: `get_current_user()` dependency in `utils/dependencies.py`
   - Admin auth: `get_current_admin_user()` dependency
   - Superadmin: `get_current_superadmin()` dependency
   - Separate User and AdminUser models with RBAC support

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

5. **Middleware Stack** (order matters - applied bottom to top):
   - `OperationLogMiddleware` - Logs admin operations for audit trails
   - `GZipMiddleware` - Compresses responses (minimum 1000 bytes)
   - `CORSMiddleware` - Handles CORS for frontend origins
   - `RequestSizeLimitMiddleware` - Limits request size (10MB default)
   - `HTTPCacheMiddleware` - HTTP caching optimization
   - `SecurityHeadersMiddleware` - Adds security headers (CSP, HSTS, etc.)
   - `PerformanceMonitorMiddleware` - Tracks slow APIs (>1s threshold)
   - `RequestIDMiddleware` - Generates unique request IDs for tracing

6. **Error Handling & Logging:**
   - Global exception handler catches all unhandled errors
   - Specialized handlers for `IntegrityError`, `OperationalError`, `RequestValidationError`
   - All errors logged to database via `utils/logging_utils.py`
   - Critical errors trigger admin notifications via `utils/admin_notification_service.py`
   - Request ID tracking throughout the stack
   - Slow query monitoring enabled on startup (500ms threshold)

7. **Admin Notifications:**
   - System health alerts (storage, errors, performance)
   - Content moderation notifications (new comments, videos pending review)
   - User activity alerts (spam detection, violations)
   - Delivered via `AdminNotificationService` in `utils/admin_notification_service.py`

### Frontend Structure (`/frontend/src`)

- **React 18** with TypeScript and Vite
- **TailwindCSS** for styling
- **TanStack Query** for data fetching and caching
- **React Router** for navigation
- **Video.js** for video playback with YouTube-like controls
- **i18n** for internationalization (locale files in `src/i18n/locales/`)
- **Zustand** for lightweight state management

**Key Components:**
- `VideoPlayer/` - Full-featured video player with keyboard shortcuts
- `VideoCard/` - Reusable video display card
- `Header/` & `Footer/` - Layout components
- `Layout/` - Page wrapper component
- `LanguageSwitcher/` - Language selection component

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
- **React Grid Layout** for customizable dashboard layouts

**Key Pages:**
- `Dashboard/` - Statistics and analytics with customizable widgets
- `Videos/` - Video management (CRUD, bulk operations, analytics)
- `Users/` - User management, banning, and statistics
- `Comments/` - Comment moderation
- `Settings/` - System configuration with multiple panels
- `Logs/` - Operation logs with filtering and export
- `AIManagement/` - AI provider configuration and monitoring
- `SystemHealth/` - Real-time system health monitoring
- `Banners/`, `Announcements/` - Content management
- `Email/` - Email template configuration
- `Reports/` - Analytics and reporting
- `Scheduling/` - Content scheduling
- `Roles/` - RBAC management (temporarily disabled pending migration)

**Key Components:**
- `NotificationBadge/` - Real-time notification display
- `NotificationDrawer/` - Notification management drawer
- `DashboardWidget/` - Customizable dashboard widgets
- `VideoPreviewPopover` - Video preview on hover
- `BatchUploader` - Batch video upload with progress tracking
- `Breadcrumb` - Dynamic breadcrumb navigation

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
- `OperationLog`, `LoginLog`, `SystemErrorLog` - Audit and monitoring
- `Role`, `Permission` - RBAC system
- `EmailConfig`, `SystemSettings` - Configuration
- `AIConfig` - AI provider settings
- `AdminNotification` - Admin notification system
- `DashboardLayout` - Customizable dashboard layouts

**Important Relationships:**
- Videos have many-to-many with Categories, Tags, Actors, Directors
- Comments belong to Users and Videos (with moderation status)
- Watch history tracks progress and completion
- AdminNotifications link to various entity types (videos, comments, users)

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
   - Update i18n locale files for both languages

### Working with Database

- **Migrations are REQUIRED** for any model changes
- Alembic auto-generates migrations but ALWAYS review them
- Test migrations on dev database before production
- Never skip migrations or modify database directly
- Sequence: modify model → `make db-migrate MSG="..."` → review migration file → `make db-upgrade`

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
4. Superadmin has additional privileges for system configuration

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
- `MINIO_ENDPOINT` - MinIO endpoint (e.g., localhost:9002)
- `MINIO_ACCESS_KEY` - MinIO access key
- `MINIO_SECRET_KEY` - MinIO secret key
- `MINIO_PUBLIC_URL` - Public URL for MinIO (for generating file URLs)

Optional:
- `DEBUG=True` - Enable SQL logging and detailed errors
- `SMTP_*` - Email configuration
- `ELASTICSEARCH_URL` - For full-text search (future)
- `CELERY_BROKER_URL` - For async tasks (future)

### Default Ports

**Development (docker-compose.dev.yml):**
- Backend API: 8000
- Frontend Dev: 5173 (proxies to 3000)
- Admin Frontend Dev: 5173 (proxies to 3001)
- PostgreSQL: 5434 (mapped from container 5432)
- Redis: 6381 (mapped from container 6379)
- MinIO API: 9002 (mapped from container 9000)
- MinIO Console: 9003 (mapped from container 9001)

**Production (docker-compose.yml):**
- Uses standard ports (5432, 6379, 9000, 9001)

## Testing

- Backend tests in `backend/tests/` (pytest + pytest-asyncio)
- Use httpx AsyncClient for API testing
- Test database should be separate (configure via env)
- Run tests with `pytest` from backend directory

## API Documentation

- Interactive Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc
- All endpoints automatically documented via FastAPI
- Includes both public API and admin endpoints

## Common Tasks

### Create Admin User
```bash
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

### Monitor Storage Usage
```python
from app.utils.storage_monitor import get_storage_stats
stats = await get_storage_stats()
# Returns: total_size, used_size, available_size, usage_percentage
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
- **Error tracking** logs all errors to database and triggers admin notifications
- **Database pool** is optimized (20+40 connections) - don't create manual connections
- **Use `pnpm`** not npm for frontend dependencies
- **Code formatting**: Use `make format-backend` before committing Python code (Black + isort)
- **i18n changes**: Update both `en-US.json` and `zh-CN.json` when adding new UI text
- **Middleware order matters**: Request flows through middleware in reverse order of registration
- **Storage monitoring** runs automatically on startup, checking MinIO usage every 5 minutes

## Recent Improvements

This project has recently received major enhancements including:
- Full internationalization (i18n) support with English and Chinese locales
- Dark/light theme implementation across both frontends
- Enhanced UX improvements in admin panel (Videos, Users, Banners pages)
- Fixed pagination issues in admin/videos endpoint
- Improved caching system with proper type validation
- Comprehensive API testing infrastructure (see `backend/tests/`)
- Admin notification system with real-time updates
- AI provider management system
- System health monitoring with storage alerts
- Customizable dashboard layouts with drag-and-drop widgets
- Video analytics and reporting
- Enhanced error logging with admin notifications
- Batch upload functionality with progress tracking

For detailed feature documentation, see [FEATURE_SHOWCASE.md](FEATURE_SHOWCASE.md) and [README.md](README.md).
