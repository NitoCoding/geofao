# Django GIS Portal - Docker Development Setup

Setup ini memungkinkan Anda menjalankan aplikasi Django GIS Portal di dalam container Docker tanpa perlu menginstall library Linux di Windows.

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) terinstall dan running
- Git (untuk clone repository)

## Quick Start

### 1. Start Development Environment

```bash
# Menggunakan script Windows
docker-dev.bat start

# Atau menggunakan script Linux/Mac
./docker-dev.sh start

# Atau manual
docker-compose up --build -d
```

### 2. Akses Aplikasi

- **Django App**: http://localhost:8000
- **Database**: localhost:5432
- **Admin Panel**: http://localhost:8000/admin
  - Username: `admin`
  - Password: `admin123`

## Struktur Docker

### Services

- **web**: Django application dengan GIS capabilities
- **db**: PostgreSQL database dengan PostGIS extension

### Volumes

- `postgres_data`: Persistent storage untuk database
- Source code di-mount ke container untuk hot reload

## Development Commands

### Script Windows (docker-dev.bat)

```cmd
# Start development environment
docker-dev.bat start

# Stop services
docker-dev.bat stop

# Restart services
docker-dev.bat restart

# View logs
docker-dev.bat logs

# Run Django commands
docker-dev.bat run makemigrations
docker-dev.bat run migrate
docker-dev.bat run collectstatic

# Open Django shell
docker-dev.bat shell

# Run tests
docker-dev.bat test
```

### Script Linux/Mac (docker-dev.sh)

```bash
# Start development environment
./docker-dev.sh start

# Stop services
./docker-dev.sh stop

# Restart services
./docker-dev.sh restart

# View logs
./docker-dev.sh logs

# Run Django commands
./docker-dev.sh run makemigrations
./docker-dev.sh run migrate
./docker-dev.sh run collectstatic

# Open Django shell
./docker-dev.sh shell

# Run tests
./docker-dev.sh test
```

### Manual Docker Commands

```bash
# Build and start
docker-compose up --build -d

# View logs
docker-compose logs -f web
docker-compose logs -f db

# Execute commands in container
docker-compose exec web python manage.py makemigrations
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py shell

# Stop services
docker-compose down

# Rebuild specific service
docker-compose up --build web
```

## Database Management

### Connection Details

- **Host**: localhost (atau `db` dari dalam container)
- **Port**: 5432
- **Database**: gisdb
- **Username**: gisuser
- **Password**: secret123

### Reset Database

```bash
# Stop services
docker-compose down

# Remove volume
docker volume rm rework_geoaibarru_postgres_data

# Start fresh
docker-compose up --build -d
```

## Troubleshooting

### Common Issues

1. **Port already in use**
   ```bash
   # Check what's using port 8000
   netstat -ano | findstr :8000
   
   # Kill process
   taskkill /PID <PID> /F
   ```

2. **Database connection failed**
   ```bash
   # Check if database is running
   docker-compose ps
   
   # Check database logs
   docker-compose logs db
   ```

3. **Permission denied on Windows**
   - Pastikan Docker Desktop memiliki akses ke drive C:
   - Restart Docker Desktop

4. **GDAL/GEOS libraries not found**
   ```bash
   # Rebuild container
   docker-compose build --no-cache web
   docker-compose up -d
   ```

### Logs

```bash
# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f web
docker-compose logs -f db

# View last 100 lines
docker-compose logs --tail=100 web
```

## Development Workflow

1. **Start environment**: `docker-dev.bat start`
2. **Make code changes** - hot reload otomatis
3. **Run migrations**: `docker-dev.bat run makemigrations && docker-dev.bat run migrate`
4. **Test changes**: `docker-dev.bat test`
5. **Stop environment**: `docker-dev.bat stop`

## File Structure

```
rework_geoaibarru/
├── Dockerfile              # Container definition
├── docker-compose.yml      # Multi-service setup
├── .dockerignore          # Docker build optimization
├── docker-dev.bat         # Windows development script
├── docker-dev.sh          # Linux/Mac development script
├── README-Docker.md       # This file
└── ...                    # Django project files
```

## Performance Tips

- Gunakan volume mounting untuk source code (hot reload)
- Exclude `__pycache__`, `.git`, dan file temporary dari container
- Gunakan multi-stage build untuk production
- Monitor resource usage dengan `docker stats`

## Next Steps

Setelah development environment berjalan:

1. Buat aplikasi Django baru: `docker-dev.bat run startapp myapp`
2. Tambahkan ke `INSTALLED_APPS` di `settings.py`
3. Buat models dan migrations
4. Test aplikasi di browser

## Support

Jika ada masalah:

1. Check logs: `docker-dev.bat logs`
2. Restart services: `docker-dev.bat restart`
3. Rebuild container: `docker-compose build --no-cache web`
4. Check Docker Desktop status dan resources

