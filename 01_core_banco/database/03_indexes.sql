CREATE INDEX IF NOT EXISTS idx_usuarios_username ON usuarios(username);
CREATE INDEX IF NOT EXISTS idx_clientes_documento ON clientes(numero_documento);
CREATE INDEX IF NOT EXISTS idx_cuentas_cliente ON cuentas_ahorro(cliente_id);
CREATE INDEX IF NOT EXISTS idx_creditos_cliente ON creditos(cliente_id);
CREATE INDEX IF NOT EXISTS idx_movimientos_cliente_fecha ON movimientos_cuenta(cliente_id, fecha_operacion DESC);
CREATE INDEX IF NOT EXISTS idx_cartera_asesor_fecha ON cartera_diaria(asesor_id, fecha_asignacion);
CREATE INDEX IF NOT EXISTS idx_solicitudes_cliente ON solicitudes_credito(cliente_id);
CREATE INDEX IF NOT EXISTS idx_solicitudes_asesor ON solicitudes_credito(asesor_id);
CREATE INDEX IF NOT EXISTS idx_solicitudes_estado ON solicitudes_credito(estado);
CREATE INDEX IF NOT EXISTS idx_notificaciones_cliente ON notificaciones(cliente_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_auditoria_fecha ON auditoria(created_at DESC);

CREATE INDEX IF NOT EXISTS idx_cliente_negocios_geo ON cliente_negocios(lat, lng);
CREATE INDEX IF NOT EXISTS idx_clientes_geo ON clientes(latitud_domicilio, longitud_domicilio);
CREATE INDEX IF NOT EXISTS idx_visitas_fecha ON visitas(fecha_visita DESC);
CREATE INDEX IF NOT EXISTS idx_visitas_cliente_fecha ON visitas(cliente_id, fecha_visita DESC);
