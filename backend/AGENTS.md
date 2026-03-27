# Comandos del Proyecto

## Desarrollo

```bash
# Instalar dependencias
poetry install

# Iniciar el servidor de desarrollo
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
docker-compose up -d

# Ver logs
docker-compose logs -f api

# Detener servicios
docker-compose down
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
