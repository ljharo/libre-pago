# LibrePago - Backend

API REST para gestionar datos de spreadsheets de operaciones de pago.

## Requisitos

- Python 3.11+
- PostgreSQL 15+ (o usar Docker)
- Redis (opcional, para cache y rate limiting)

## Quick Start

### 1. Instalar dependencias

```bash
# Instalar Poetry (si no lo tienes)
curl -sSL https://install.python-poetry.org | python3 -

# Instalar dependencias del proyecto
poetry install
```

### 2. Configurar variables de entorno

```bash
# Copiar archivo de ejemplo
cp .env.example .env

# Editar .env con tus configuraciones
# Los valores por defecto funcionan para desarrollo local
```

### 3. Base de datos

**Opción A: Docker (recomendado)**
```bash
# Crear contenedor PostgreSQL
docker run -d \
  --name librepago-db \
  -e POSTGRES_USER=admin \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=libre_pago_db \
  -p 5432:5432 \
  postgres:15-alpine

# Crear contenedor Redis (opcional)
docker run -d \
  --name librepago-redis \
  -p 6379:6379 \
  redis:7-alpine
```

**Opción B: PostgreSQL local**
```bash
# Crear base de datos
createdb libre_pago_db -U postgres
```

### 4. Ejecutar migraciones

```bash
poetry run alembic upgrade head
```

### 5. Iniciar servidor

```bash
poetry run start
```

El servidor estará en: http://localhost:8000

## Comandos常用

### Desarrollo

```bash
# Iniciar servidor con hot-reload
poetry run start

# Ver documentación API
# http://localhost:8000/docs
```

### Migraciones

```bash
# Crear nueva migración
poetry run alembic revision --autogenerate -m "descripcion"

# Aplicar migraciones
poetry run alembic upgrade head

# Ver historial de migraciones
poetry run alembic history

# Rollback (una migración)
poetry run alembic downgrade -1
```

### Testing

```bash
# Ejecutar todos los tests
poetry run pytest

# Con coverage
poetry run pytest --cov=app

# Tests específicos
poetry run pytest tests/test_api.py -v
```

### Linting y Formateo

```bash
# Lint con Ruff
poetry run ruff check .

# Auto-fix
poetry run ruff check . --fix

# Formateo
poetry run ruff format .

# Verificar imports
poetry run isort app/ --check-only
```

### Pre-commit

```bash
# Instalar hooks
poetry run pre-commit install

# Ejecutar en todos los archivos
poetry run pre-commit run --all-files
```

## Variables de Entorno

| Variable | Descripción | Default |
|----------|-------------|---------|
| `DB_USER` | Usuario PostgreSQL | admin |
| `DB_PASSWORD` | Contraseña PostgreSQL | password |
| `DB_HOST` | Host PostgreSQL | localhost |
| `DB_PORT` | Puerto PostgreSQL | 5432 |
| `DB_NAME` | Nombre base de datos | libre_pago_db |
| `REDIS_HOST` | Host Redis | localhost |
| `REDIS_PORT` | Puerto Redis | 6379 |
| `API_KEY` | Clave API | test-api-key |
| `DEBUG` | Modo debug | false |
| `JWT_SECRET` | Secret para JWT | change-me-in-production |
| `JWT_EXPIRE_DAYS` | Expiración token (días) | 1 |
| `ADMIN_USERNAME` | Usuario admin inicial | admin |
| `ADMIN_PASSWORD` | Contraseña admin inicial | admin123 |

## Estructura

```
backend/
├── app/
│   ├── main.py           # Aplicación FastAPI
│   ├── config.py        # Configuración
│   ├── database.py      # Conexión a BD
│   ├── models/          # Modelos SQLAlchemy
│   ├── routers/         # Endpoints
│   ├── schemas/         # Esquemas Pydantic
│   ├── dependencies.py  # Dependencias FastAPI
│   └── ...
├── alembic/             # Migraciones
├── tests/               # Tests
├── pyproject.toml       # Dependencias
├── .env                 # Variables de entorno
└── .pre-commit-config.yaml
```

## Docker

```bash
# Build y run desde raíz del proyecto
docker build -t librepago-backend ./backend
docker run -p 8000:8000 --env-file backend/.env librepago-backend
```

## Troubleshooting

### Error de conexión a PostgreSQL
```bash
# Verificar que PostgreSQL esté corriendo
pg_isready -h localhost -p 5432
```

### Error de migración
```bash
# Si hay conflictos, puedo.resetear la base
poetry run alembic downgrade base
poetry run alembic upgrade head
```

### Instalar Poetry en Linux
```bash
curl -sSL https://install.python-poetry.org | python3 -
export PATH="$HOME/.local/bin:$PATH"
```
