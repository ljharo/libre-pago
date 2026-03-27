# LibrePago - Frontend

Aplicación web React para gestionar datos de operaciones de pago.

## Requisitos

- Node.js 22+
- npm o yarn

## Quick Start

### 1. Instalar dependencias

```bash
cd frontend
npm install
```

### 2. Configurar variables de entorno

```bash
# Copiar archivo de ejemplo
cp .env.example .env
```

Valores por defecto:
- `VITE_API_URL=http://localhost:8000`
- `VITE_API_KEY=test-api-key`

### 3. Iniciar servidor de desarrollo

```bash
npm run dev
```

La aplicación estará en: http://localhost:3000

## Scripts Disponibles

| Comando | Descripción |
|---------|-------------|
| `npm run dev` | Iniciar servidor de desarrollo |
| `npm run build` | Build de producción |
| `npm run preview` | Previsualizar build |
| `npm run lint` | Verificar código con ESLint |

## Estructura

```
frontend/
├── src/
│   ├── pages/           # Páginas
│   │   ├── LoginPage.tsx
│   │   ├── DashboardPage.tsx
│   │   ├── ImportPage.tsx
│   │   └── UsersPage.tsx
│   ├── lib/
│   │   └── api.ts       # Cliente API
│   ├── App.tsx          # Router principal
│   └── main.tsx         # Entry point
├── public/              # Archivos estáticos
├── index.html
├── package.json
├── vite.config.ts
├── tailwind.config.js
└── tsconfig.json
```

## Rutas

| Ruta | Descripción |
|------|-------------|
| `/login` | Login de usuario |
| `/dashboard` | Dashboard con estadísticas |
| `/import` | Importar archivos Excel |
| `/users` | Gestión de usuarios (solo admin) |

## Desarrollo

### Conexión con el Backend

El frontend se comunica con la API en `VITE_API_URL`. Asegúrate de que el backend esté corriendo.

```bash
# En otra terminal, desde la raíz del proyecto
cd backend
poetry run start
```

### Build de producción

```bash
npm run build
```

Los archivos se generan en `dist/`.

## Docker

```bash
# Build
docker build -t librepago-frontend ./frontend

# Run
docker run -p 3000:80 librepago-frontend
```

## Troubleshooting

### Error de CORS
Si hay errores de CORS, verificar que el backend tenga CORS configurado para el origen del frontend.

### Error de TypeScript
```bash
# Ver errores de tipo sin compilar
npx tsc --noEmit
```

### Instalar Node.js 22 (Linux)
```bash
curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
sudo apt-get install -y nodejs
```
