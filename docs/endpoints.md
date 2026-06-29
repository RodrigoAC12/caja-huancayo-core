# Servicios principales

## Personal interno

- `POST /auth/login`
- `GET /auth/me`
- `GET /clientes`
- `GET /clientes/{cliente_id}/ficha`
- `PATCH /clientes/{cliente_id}/ubicacion`
- `GET /cartera`
- `POST /cartera/{cartera_id}/visita`
- `GET /cartera/visitas`
- `GET /solicitudes`
- `POST /solicitudes`
- `GET /solicitudes/{id}`
- `PATCH /solicitudes/{id}/estado`
- `POST /pre-evaluar`
- `POST /buro/consulta`
- `GET /operaciones`
- `GET /reportes/dashboard`
- `GET /reportes/productividad`
- `GET /auditoria`

## App cliente

- `POST /cliente/login`
- `GET /cliente/perfil`
- `GET /cliente/cuentas`
- `GET /cliente/creditos`
- `GET /cliente/creditos/{numero_credito}/cronograma`
- `GET /cliente/movimientos`
- `GET /cliente/tarjetas`
- `GET /cliente/notificaciones`
- `POST /cliente/operaciones`
- `GET /cliente/solicitudes`
- `POST /cliente/solicitudes`

## Ubicación y visitas

- `GET /cartera`: devuelve la cartera asignada con dirección, referencia y coordenadas del negocio.
- `POST /cartera/{cartera_id}/visita`: registra la visita del asesor con ubicación, observación y resultado.
- `GET /cartera/visitas`: muestra visitas registradas por fecha o por cliente.
- `PATCH /clientes/{cliente_id}/ubicacion`: actualiza domicilio y negocio del cliente.
