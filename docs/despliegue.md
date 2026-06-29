# Despliegue local y nube

## Local

1. PostgreSQL local o Docker Compose.
2. Ejecutar scripts SQL de `01_core_banco/database`.
3. Backend FastAPI en `localhost:8003`.
4. Frontend React en `localhost:5173`.

## Supabase

1. Crear proyecto.
2. Ejecutar `01_schema.sql`, `02_seed_inicial.sql` y `03_indexes.sql`.
3. Copiar `DATABASE_URL`.
4. Usar esa URL en Render.

## Render

- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

Variables:

```env
DATABASE_URL=...
SECRET_KEY=...
CORS_ORIGINS=https://tu-frontend.vercel.app
APP_ENV=production
```

## Vercel

Variable:

```env
VITE_API_BASE_URL=https://tu-api.onrender.com
```
