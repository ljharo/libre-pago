# LibrePago Backend

Backend API para gestionar datos de spreadsheets de LibrePago.

## Tecnologías

- **FastAPI**: Framework web moderno y rápido
- **PostgreSQL**: Base de datos relacional
- **SQLAlchemy**: ORM para gestión de base de datos
- **Pandas**: Procesamiento de archivos Excel
- **Alembic**: Gestión de migraciones de base de datos
- **Poetry**: Gestión de dependencias

## Requisitos

- Python 3.11+
- PostgreSQL 15
- Docker (para desarrollo)

## Instalación

```bash
# Instalar dependencias
poetry install

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus configuraciones

# Ejecutar migraciones
poetry run alembic upgrade head

# Poblar datos base (channels, agents, teams)
poetry run python -m app.seed
```

## Desarrollo

```bash
# Iniciar servidor de desarrollo
poetry run start

# Ejecutar migraciones
poetry run alembic upgrade head

# Crear nueva migración
poetry run alembic revision --autogenerate -m "description"

# Pre-commit
poetry run pre-commit install
poetry run pre-commit run --all-files
```

## Docker

```bash
# Levantar servicios
docker compose -f docker-compose.dev.yml up -d

# Ver logs
docker compose logs -f api

# Detener servicios
docker compose down
```

## Testing

```bash
# Ejecutar tests
poetry run pytest

# Con coverage
poetry run pytest --cov=app
```

## Linting

```bash
poetry run ruff check .
poetry run ruff format .
poetry run mypy app
poetry run isort app --check-only
```

## API Endpoints

### Health Check
- `GET /health` - Verificar estado del servicio

### Importación de Excel
- `GET /api/import/templates/{spreadsheet_type}` - Obtener plantilla de importación
- `POST /api/import/{spreadsheet_type}` - Importar archivo Excel

**Tipos de spreadsheet soportados:**
- `closed_conversations` - Conversaciones cerradas
- `lifecycles` - Ciclos de vida
- `ads` - Anuncios
- `csat` - Satisfacción del cliente

### Conversaciones
- `GET /api/conversations` - Listar todas las conversaciones
- `GET /api/conversations/{conversation_id}` - Obtener conversación específica
- `GET /api/conversations/stats/monthly` - Estadísticas mensuales
- `GET /api/conversations/stats/ai-vs-human` - Comparación AI vs humano

### Ciclos de Vida
- `GET /api/lifecycles` - Listar todos los ciclos de vida
- `GET /api/lifecycles/{lifecycle_id}` - Obtener ciclo de vida específico
- `GET /api/lifecycles/contact/{contact_id}` - Obtener ciclos de vida por contacto
- `GET /api/lifecycles/stats/pipeline` - Estadísticas de pipeline

### Anuncios
- `GET /api/ads` - Listar todos los anuncios
- `GET /api/ads/{ad_id}` - Obtener anuncio específico
- `GET /api/ads/stats/by-channel` - Estadísticas por canal
- `GET /api/ads/stats/top-campaigns` - Mejores campañas

### CSAT
- `GET /api/csat` - Listar todas las evaluaciones CSAT
- `GET /api/csat/{csat_id}` - Obtener evaluación específica
- `GET /api/csat/stats/average` - Promedio de satisfacción
- `GET /api/csat/stats/by-agent` - CSAT por agente

### Mapeos
- `GET /api/channels` - Listar canales
- `GET /api/agents` - Listar agentes
- `GET /api/teams` - Listar equipos

## Autenticación

La API requiere un header `X-API-Key` para todas las solicitudes que lo requieran:

```bash
curl -H "X-API-Key: test-api-key" http://localhost:8000/api/channels
```

## Estructura del Proyecto

```
libre-pago/
├── app/
│   ├── config.py          # Configuración de la aplicación
│   ├── database.py        # Conexión a base de datos
│   ├── main.py            # Aplicación FastAPI
│   ├── models/            # Modelos de SQLAlchemy
│   ├── routers/           # Endpoints de la API
│   ├── schemas/           # Esquemas Pydantic
│   ├── dependencies.py    # Dependencias FastAPI
│   ├── seed.py            # Datos iniciales
│   └── scripts/           # Scripts de utilidad
├── alembic/               # Migraciones de base de datos
├── data/                  # Archivos Excel de prueba
├── tests/                 # Tests del proyecto
└── pyproject.toml         # Configuración de Poetry
```

## Variables de Entorno

| Variable | Descripción | Default |
|----------|-------------|---------|
| `DB_USER` | Usuario de PostgreSQL | postgres |
| `DB_PASSWORD` | Contraseña de PostgreSQL | postgres |
| `DB_HOST` | Host de PostgreSQL | localhost |
| `DB_PORT` | Puerto de PostgreSQL | 5432 |
| `DB_NAME` | Nombre de la base de datos | librepago |
| `API_KEY` | Clave para la API | default-api-key-change-me |
| `DEBUG` | Modo debug | false |

## Licencia

MIT
