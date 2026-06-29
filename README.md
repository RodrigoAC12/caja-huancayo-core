# Core Caja Huancayo — Plataforma Operativa Bancaria

Sistema central para la gestión de clientes, cuentas, créditos, solicitudes, operaciones, cartera comercial, visitas de campo, reportes y auditoría.

El Core concentra la información del banco y atiende al portal interno, la app de fuerza de ventas y la app del cliente.

## Módulos incluidos

- Portal interno para personal autorizado.
- Gestión de clientes y negocios.
- Cartera diaria de asesores.
- Ubicación de domicilio y negocio del cliente.
- Registro de visitas de campo con GPS.
- Solicitudes de crédito.
- Evaluación y seguimiento de expedientes.
- Cuentas, créditos, movimientos y operaciones.
- Reportes de productividad.
- Auditoría de acciones internas.

## Carpetas principales

```text
01_core_banco/
├── backend_fastapi/    Servicio central del Core
├── frontend_react/     Portal interno del personal
└── database/           Base de datos y carga inicial

docs/                   Guías de operación
```

## Accesos locales

| Rol | Usuario | Contraseña |
|---|---:|---:|
| Administrador | `admin` | `admin123` |
| Supervisor | `0002` | `1234` |
| Asesor | `0001` | `1234` |
| Cliente | `12345678` | `1234` |

## Inicio local

1. Levantar la base de datos:

```bash
cd 01_core_banco
cp .env.example .env
docker compose up -d
```

2. Cargar estructura y datos iniciales:

```bash
psql -U postgres -d bd_caja_huancayo_core -f database/01_schema.sql
psql -U postgres -d bd_caja_huancayo_core -f database/02_seed_inicial.sql
psql -U postgres -d bd_caja_huancayo_core -f database/03_indexes.sql
```

3. Levantar el servicio central:

```bash
cd backend_fastapi
python -m venv venv
# Windows: venv\Scripts\activate
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn main:app --reload --host 0.0.0.0 --port 8003
```

4. Levantar el portal interno:

```bash
cd ../frontend_react
npm install
cp .env.example .env
npm run dev
```

Abrir en el navegador:

```text
http://localhost:5173
```

## Ubicación y visitas de campo

El Core guarda la ubicación del domicilio, la ubicación del negocio y el registro de cada visita realizada por el asesor. La app de fuerza de ventas consulta estos datos para mostrar el mapa y envía la ubicación real del asesor cuando registra una visita.

Para bases ya creadas antes de esta versión, ejecutar:

```bash
psql -U postgres -d bd_caja_huancayo_core -f database/06_update_geolocation.sql
```
