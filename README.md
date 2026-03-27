# LibrePago

Sistema de gestión de spreadsheets para operaciones de pago.

## Arquitectura

```
┌─────────────┐     ┌─────────────┐
│   Frontend  │────▶│  Backend    │
│  (React+TS) │     │ (FastAPI)   │
└─────────────┘     └──────┬──────┘
                           │
                    ┌──────┴──────┐
                    │             │
                ┌───▼───┐    ┌───▼───┐
                │  DB   │    │Redis  │
                │(Postgres)   │(Cache)│
                └────────┘    └───────┘
```

## Tecnologías

### Backend
- **FastAPI** - Framework web moderno y rápido
- **PostgreSQL** - Base de datos relacional
- **SQLAlchemy** - ORM para gestión de base de datos
- **Pandas** - Procesamiento de archivos Excel
- **Alembic** - Gestión de migraciones
- **Poetry** - Gestión de dependencias
- **Redis** - Cache y rate limiting

### Frontend
- **React 18** - Librería UI
- **TypeScript** - Tipado estático
- **Vite** - Build tool
- **Tailwind CSS** - Estilos
- **React Router** - Navegación
- **Axios** - HTTP client
- **Lucide React** - Iconos

## Requisitos

- Docker y Docker Compose
- Node.js 22+ (para desarrollo local del frontend)
- Python 3.11+ (para desarrollo local del backend)

## Quick Start

### Con Docker (Producción/Desarrollo)

```bash
# Levantar todos los servicios
docker compose up -d --build

# Ver logs
docker compose logs -f

# Detener servicios
docker compose down
```

**Servicios:**
- Frontend: http://localhost:3000
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- PostgreSQL: localhost:5432
- Redis: localhost:6379

### Desarrollo Local

#### Backend

```bash
cd backend

# Instalar dependencias
poetry install

# Configurar variables de entorno
cp .env.example .env

# Ejecutar migraciones
poetry run alembic upgrade head

# Iniciar servidor
poetry run start
```

#### Frontend

```bash
cd frontend

# Instalar dependencias
npm install

# Iniciar servidor de desarrollo
npm run dev
```

## Estructura del Proyecto

```
libre-pago/
├── docker-compose.yml          # Orquestación de servicios
├── README.md                   # Este archivo
├── docs/                       # Documentación de API
│   └── API.md                  # Referencia de endpoints
├── backend/                    # API FastAPI
│   ├── app/                    # Código fuente
│   │   ├── main.py             # Aplicación principal
│   │   ├── config.py           # Configuración
│   │   ├── database.py         # Conexión a BD
│   │   ├── models/             # Modelos SQLAlchemy
│   │   ├── routers/            # Endpoints
│   │   ├── schemas/            # Esquemas Pydantic
│   │   └── dependencies.py     # Dependencias FastAPI
│   ├── alembic/                # Migraciones
│   ├── tests/                  # Tests
│   ├── pyproject.toml          # Dependencias Python
│   └── .env                    # Variables de entorno
└── frontend/                   # Aplicación React
    ├── src/
    │   ├── pages/              # Páginas
    │   │   ├── LoginPage.tsx   # Login
    │   │   ├── DashboardPage.tsx # Dashboard
    │   │   ├── ImportPage.tsx  # Importar Excel
    │   │   └── UsersPage.tsx   # Gestión usuarios
    │   ├── lib/
    │   │   └── api.ts          # Cliente API
    │   └── App.tsx             # Router principal
    ├── package.json            # Dependencias Node
    └── vite.config.ts          # Configuración Vite
```

## Páginas del Frontend

| Ruta | Descripción |
|------|-------------|
| `/login` | Login de usuario |
| `/dashboard` | Dashboard con estadísticas |
| `/import` | Importar archivos Excel |
| `/users` | Gestión de usuarios (solo admin) |

## API Endpoints

Consulta la documentación completa en `docs/API.md`.

### Autenticación

```bash
# Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "X-API-Key: test-api-key" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

### Importar Excel

```bash
curl -X POST http://localhost:8000/api/import/closed_conversations \
  -H "X-API-Key: test-api-key" \
  -H "Authorization: Bearer <token>" \
  -F "file=@data.xlsx"
```

### Tipos de spreadsheet
- `closed_conversations` - Conversaciones cerradas
- `lifecycles` - Ciclos de vida
- `ads` - Anuncios
- `csat` - Satisfacción del cliente

## Variables de Entorno

### Backend (.env)

| Variable | Descripción | Default |
|----------|-------------|---------|
| `DB_USER` | Usuario PostgreSQL | admin |
| `DB_PASSWORD` | Contraseña PostgreSQL | password |
| `DB_HOST` | Host PostgreSQL | db |
| `DB_PORT` | Puerto PostgreSQL | 5432 |
| `DB_NAME` | Nombre base de datos | libre_pago_db |
| `REDIS_HOST` | Host Redis | redis |
| `REDIS_PORT` | Puerto Redis | 6379 |
| `API_KEY` | Clave API | test-api-key |
| `JWT_SECRET` | Secret para JWT | change-me-in-production |
| `JWT_EXPIRE_DAYS` | Expiración token | 1 |
| `ADMIN_USERNAME` | Usuario admin | admin |
| `ADMIN_PASSWORD` | Contraseña admin | admin123 |

### Frontend (.env)

| Variable | Descripción | Default |
|----------|-------------|---------|
| `VITE_API_URL` | URL de la API | http://localhost:8000 |
| `VITE_API_KEY` | Clave API | test-api-key |

## Desarrollo

### Pre-commit (Backend)

```bash
cd backend

# Instalar hooks
poetry run pre-commit install

# Ejecutar validaciones
poetry run pre-commit run --all-files
```

### Testing (Backend)

```bash
cd backend

# Ejecutar tests
poetry run pytest

# Con coverage
poetry run pytest --cov=app
```

### Linting (Backend)

```bash
cd backend

poetry run ruff check .
poetry run ruff format .
poetry run mypy app
poetry run isort app --check-only
```

### Build Frontend

```bash
cd frontend

npm run build
```

## Notas

- El frontend se comunica con la API directamente en desarrollo
- En producción, usar Cloudflare Zero Trust como proxy
- Los archivos Excel deben tener formato específico (ver plantillas)
- La segunda hoja del Excel puede contener mapeos de IDs externos

## Licencia

MIT
