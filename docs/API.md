# LibrePago API - Documentación

## Autenticación

Todas las rutas (excepto `/health`) requieren el header `x-api-key`:

```bash
curl -H "x-api-key: tu-api-key" http://localhost:8000/endpoint
```

**Respuesta si la key es inválida:**
```json
{"detail": "Invalid API key"}
```
**Código:** 403 Forbidden

---

## Endpoints

### Health Check
```bash
GET /health
```
Sin autenticación.

**Respuesta:**
```json
{"status": "healthy", "app": "LibrePago API"}
```

---

### Conversations (Cerradas)

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/conversations` | Listar conversaciones |
| GET | `/api/conversations/{id}` | Obtener una conversación |
| POST | `/api/conversations` | Crear conversación |
| PUT | `/api/conversations/{id}` | Actualizar conversación |
| DELETE | `/api/conversations/{id}` | Eliminar conversación |
| GET | `/api/conversations/stats/monthly?year=2026&month=3` | Stats mensuales |
| GET | `/api/conversations/stats/ai-vs-human?year=2026&month=3` | % IA vs Humanos |

**Parámetros GET:**
- `skip`: offset (default 0)
- `limit`: límite (default 100, max 1000)
- `fecha_from`: fecha inicio (ISO 8601)
- `fecha_to`: fecha fin (ISO 8601)
- `canal_id`: filtrar por canal
- `equipo_id`: filtrar por equipo

**Ejemplo:**
```bash
curl -H "x-api-key: test-api-key" \
  "http://localhost:8000/api/conversations?limit=10"
```

---

### Lifecycles (Ciclos de Vida)

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/lifecycles` | Listar lifecycles |
| GET | `/api/lifecycles/{id}` | Obtener lifecycle |
| GET | `/api/lifecycles/contact/{contact_id}` | Último lifecycle de un contacto |
| POST | `/api/lifecycles` | Crear lifecycle |
| PUT | `/api/lifecycles/{id}` | Actualizar lifecycle |
| DELETE | `/api/lifecycles/{id}` | Eliminar lifecycle |
| GET | `/api/lifecycles/stats/pipeline` | Stats de pipeline actual |

**Ejemplo - Obtener último lifecycle de un contacto:**
```bash
curl -H "x-api-key: test-api-key" \
  http://localhost:8000/api/lifecycles/contact/12345
```

---

### Ads (Publicidad)

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/ads` | Listar ads |
| GET | `/api/ads/{id}` | Obtener ad |
| POST | `/api/ads` | Crear ad |
| PUT | `/api/ads/{id}` | Actualizar ad |
| DELETE | `/api/ads/{id}` | Eliminar ad |
| GET | `/api/ads/stats/top-campaigns?year=2026&month=3&limit=3` | Top campañas |
| GET | `/api/ads/stats/by-channel?year=2026&month=3` | Stats por canal |

**Ejemplo - Top 3 campañas de marzo:**
```bash
curl -H "x-api-key: test-api-key" \
  "http://localhost:8000/api/ads/stats/top-campaigns?year=2026&month=3&limit=3"
```

---

### CSAT (Satisfacción)

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/csat` | Listar encuestas |
| GET | `/api/csat/{id}` | Obtener encuesta |
| POST | `/api/csat` | Crear encuesta |
| PUT | `/api/csat/{id}` | Actualizar encuesta |
| DELETE | `/api/csat/{id}` | Eliminar encuesta |
| GET | `/api/csat/stats/average?year=2026&month=3` | CSAT promedio |
| GET | `/api/csat/stats/by-agent?year=2026&month=3` | CSAT por agente |

**Ejemplo - CSAT promedio marzo:**
```bash
curl -H "x-api-key: test-api-key" \
  "http://localhost:8000/api/csat/stats/average?year=2026&month=3"
```

---

### Mapeos (Channels, Agents, Teams)

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/channels` | Listar canales |
| POST | `/api/channels` | Crear canal |
| GET | `/api/agents` | Listar agentes |
| POST | `/api/agents` | Crear agente |
| GET | `/api/teams` | Listar equipos |
| POST | `/api/teams` | Crear equipo |

**Ejemplo - Listar canales:**
```bash
curl -H "x-api-key: test-api-key" \
  http://localhost:8000/api/channels
```

---

## Ejemplo Completo

### Crear una conversación y consultar stats

```bash
# 1. Crear conversación
curl -X POST -H "x-api-key: test-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "fecha": "2026-03-25T10:00:00",
    "contact_id": 12345,
    "nombre": "Juan Perez",
    "email": "juan@test.com",
    "telefono": "+584121234567",
    "canal_id": 1,
    "cesionario_id": 2,
    "equipo_id": 1,
    "tipificacion": "Consulta",
    "resumen": "Cliente interesdo en producto"
  }' \
  http://localhost:8000/api/conversations

# 2. Consultar stats del mes
curl -H "x-api-key: test-api-key" \
  "http://localhost:8000/api/conversations/stats/monthly?year=2026&month=3"
```

---

## Respuestas de Error

| Código | Descripción |
|--------|-------------|
| 400 | Bad Request - datos inválidos |
| 403 | Forbidden - API key inválida |
| 404 | Not Found - recurso no existe |
| 422 | Unprocessable Entity - validación fallida |
| 500 | Internal Server Error |

---

## Configuración

Variables de entorno (`.env`):
```
DATABASE_URL=sqlite:///./librepago.db
API_KEY=tu-api-key-segura
DEBUG=false
```