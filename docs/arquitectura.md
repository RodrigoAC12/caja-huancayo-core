# Arquitectura del Core Caja Huancayo

El core funciona como una API central. Ninguna app móvil o frontend accede directamente a la base de datos.

```text
App Fuerza de Ventas Flutter ─┐
                              ├── Backend FastAPI ─── PostgreSQL/Supabase
App Cliente Flutter ──────────┤
                              │
Frontend React Core ──────────┘
```

## Despliegue final

- Supabase: PostgreSQL y Storage opcional para documentos.
- Render: Backend FastAPI.
- Vercel: Frontend React.
- Flutter: apps móviles configuradas con API_BASE_URL.
