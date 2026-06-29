-- ============================================================
-- Actualización GPS / Mapa de visitas
-- Usar si ya tenías una BD creada y no quieres reconstruir desde cero.
-- Para instalación limpia, ejecutar 01_schema.sql + 02_seed_inicial.sql.
-- ============================================================

ALTER TABLE clientes ADD COLUMN IF NOT EXISTS referencia_direccion TEXT;
ALTER TABLE clientes ADD COLUMN IF NOT EXISTS latitud_domicilio DECIMAL(10,7);
ALTER TABLE clientes ADD COLUMN IF NOT EXISTS longitud_domicilio DECIMAL(10,7);

ALTER TABLE cliente_negocios ADD COLUMN IF NOT EXISTS referencia_negocio TEXT;
ALTER TABLE cliente_negocios ADD COLUMN IF NOT EXISTS departamento VARCHAR(80);
ALTER TABLE cliente_negocios ADD COLUMN IF NOT EXISTS provincia VARCHAR(80);
ALTER TABLE cliente_negocios ADD COLUMN IF NOT EXISTS distrito VARCHAR(80);

ALTER TABLE visitas ADD COLUMN IF NOT EXISTS precision_gps DECIMAL(10,2);
ALTER TABLE visitas ADD COLUMN IF NOT EXISTS distancia_negocio_metros DECIMAL(10,2);

ALTER TABLE cartera_diaria ADD COLUMN IF NOT EXISTS precision_gps DECIMAL(10,2);
ALTER TABLE cartera_diaria ADD COLUMN IF NOT EXISTS distancia_negocio_metros DECIMAL(10,2);

CREATE INDEX IF NOT EXISTS idx_cliente_negocios_geo ON cliente_negocios(lat, lng);
CREATE INDEX IF NOT EXISTS idx_clientes_geo ON clientes(latitud_domicilio, longitud_domicilio);
CREATE INDEX IF NOT EXISTS idx_visitas_fecha ON visitas(fecha_visita DESC);
CREATE INDEX IF NOT EXISTS idx_visitas_cliente_fecha ON visitas(cliente_id, fecha_visita DESC);


ALTER TABLE cliente_negocios ADD COLUMN IF NOT EXISTS ubicacion_verificada BOOLEAN NOT NULL DEFAULT FALSE;
ALTER TABLE cliente_negocios ADD COLUMN IF NOT EXISTS fuente_ubicacion VARCHAR(40);
ALTER TABLE cliente_negocios ADD COLUMN IF NOT EXISTS precision_ubicacion_metros DECIMAL(10,2);
ALTER TABLE cliente_negocios ADD COLUMN IF NOT EXISTS fecha_verificacion_ubicacion TIMESTAMPTZ;
ALTER TABLE cliente_negocios ADD COLUMN IF NOT EXISTS usuario_verificacion_id UUID REFERENCES usuarios(id);
CREATE INDEX IF NOT EXISTS idx_cliente_negocios_verificada ON cliente_negocios(ubicacion_verificada);
