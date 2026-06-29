-- ============================================================
-- Core Caja Huancayo — PostgreSQL / Supabase
-- Core bancario orientado a nube
-- ============================================================
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Limpieza ordenada para desarrollo local
DROP TABLE IF EXISTS auditoria CASCADE;
DROP TABLE IF EXISTS comprobantes CASCADE;
DROP TABLE IF EXISTS operaciones CASCADE;
DROP TABLE IF EXISTS notificaciones CASCADE;
DROP TABLE IF EXISTS tarjetas CASCADE;
DROP TABLE IF EXISTS documentos_solicitud CASCADE;
DROP TABLE IF EXISTS consultas_buro CASCADE;
DROP TABLE IF EXISTS evaluaciones_crediticias CASCADE;
DROP TABLE IF EXISTS solicitud_estado_historial CASCADE;
DROP TABLE IF EXISTS solicitudes_credito CASCADE;
DROP TABLE IF EXISTS visitas CASCADE;
DROP TABLE IF EXISTS cartera_diaria CASCADE;
DROP TABLE IF EXISTS movimientos_cuenta CASCADE;
DROP TABLE IF EXISTS cronograma_credito CASCADE;
DROP TABLE IF EXISTS creditos CASCADE;
DROP TABLE IF EXISTS cuentas_ahorro CASCADE;
DROP TABLE IF EXISTS cliente_negocios CASCADE;
DROP TABLE IF EXISTS asesores CASCADE;
DROP TABLE IF EXISTS agencias CASCADE;
DROP TABLE IF EXISTS clientes CASCADE;
DROP TABLE IF EXISTS sesiones CASCADE;
DROP TABLE IF EXISTS usuarios CASCADE;
DROP TABLE IF EXISTS roles CASCADE;

CREATE TABLE roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nombre VARCHAR(30) UNIQUE NOT NULL,
    descripcion TEXT
);

CREATE TABLE usuarios (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    rol_id UUID REFERENCES roles(id),
    username VARCHAR(30) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    tipo_usuario VARCHAR(15) NOT NULL CHECK (tipo_usuario IN ('personal','cliente')),
    estado VARCHAR(15) NOT NULL DEFAULT 'activo' CHECK (estado IN ('activo','bloqueado','inactivo')),
    intentos_fallidos INTEGER NOT NULL DEFAULT 0,
    bloqueado_hasta TIMESTAMPTZ,
    ultimo_login TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE sesiones (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    usuario_id UUID NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    refresh_token_hash TEXT,
    dispositivo TEXT,
    ip VARCHAR(60),
    fecha_inicio TIMESTAMPTZ NOT NULL DEFAULT now(),
    fecha_expiracion TIMESTAMPTZ,
    revocado BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE agencias (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    codigo VARCHAR(20) UNIQUE NOT NULL,
    nombre VARCHAR(120) NOT NULL,
    region VARCHAR(80),
    direccion TEXT,
    lat DECIMAL(10,7),
    lng DECIMAL(10,7),
    estado VARCHAR(15) NOT NULL DEFAULT 'activa' CHECK (estado IN ('activa','inactiva')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE clientes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    usuario_id UUID UNIQUE REFERENCES usuarios(id),
    tipo_documento VARCHAR(5) NOT NULL DEFAULT 'DNI',
    numero_documento VARCHAR(15) UNIQUE NOT NULL,
    nombres VARCHAR(100) NOT NULL,
    apellidos VARCHAR(100) NOT NULL,
    fecha_nacimiento DATE,
    telefono VARCHAR(20),
    email VARCHAR(120),
    direccion TEXT,
    referencia_direccion TEXT,
    departamento VARCHAR(80),
    provincia VARCHAR(80),
    distrito VARCHAR(80),
    latitud_domicilio DECIMAL(10,7),
    longitud_domicilio DECIMAL(10,7),
    estado_civil VARCHAR(20),
    estado_cliente VARCHAR(15) NOT NULL DEFAULT 'activo' CHECK (estado_cliente IN ('activo','observado','inactivo')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE cliente_negocios (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cliente_id UUID NOT NULL REFERENCES clientes(id) ON DELETE CASCADE,
    nombre_negocio VARCHAR(120),
    tipo_negocio VARCHAR(60),
    actividad_economica VARCHAR(80),
    antiguedad_meses INTEGER DEFAULT 0,
    direccion_negocio TEXT,
    referencia_negocio TEXT,
    departamento VARCHAR(80),
    provincia VARCHAR(80),
    distrito VARCHAR(80),
    lat DECIMAL(10,7),
    lng DECIMAL(10,7),
    ubicacion_verificada BOOLEAN NOT NULL DEFAULT FALSE,
    fuente_ubicacion VARCHAR(40),
    precision_ubicacion_metros DECIMAL(10,2),
    fecha_verificacion_ubicacion TIMESTAMPTZ,
    usuario_verificacion_id UUID REFERENCES usuarios(id),
    ingresos_estimados DECIMAL(12,2) DEFAULT 0,
    gastos_estimados DECIMAL(12,2) DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE asesores (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    usuario_id UUID UNIQUE REFERENCES usuarios(id),
    agencia_id UUID REFERENCES agencias(id),
    codigo_empleado VARCHAR(20) UNIQUE NOT NULL,
    nombres VARCHAR(100) NOT NULL,
    apellidos VARCHAR(100) NOT NULL,
    telefono VARCHAR(20),
    zona_asignada VARCHAR(100),
    perfil VARCHAR(30) NOT NULL DEFAULT 'asesor' CHECK (perfil IN ('asesor','supervisor','administrador','analista')),
    estado VARCHAR(15) NOT NULL DEFAULT 'activo' CHECK (estado IN ('activo','inactivo')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE cuentas_ahorro (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cliente_id UUID NOT NULL REFERENCES clientes(id) ON DELETE CASCADE,
    numero_cuenta VARCHAR(30) UNIQUE NOT NULL,
    tipo_cuenta VARCHAR(40) DEFAULT 'Ahorro',
    moneda VARCHAR(3) DEFAULT 'PEN',
    saldo_disponible DECIMAL(12,2) NOT NULL DEFAULT 0,
    saldo_contable DECIMAL(12,2) NOT NULL DEFAULT 0,
    tea DECIMAL(5,2) DEFAULT 0,
    estado VARCHAR(20) DEFAULT 'activa' CHECK (estado IN ('activa','bloqueada','cerrada')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE creditos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cliente_id UUID NOT NULL REFERENCES clientes(id) ON DELETE CASCADE,
    numero_credito VARCHAR(30) UNIQUE NOT NULL,
    producto VARCHAR(60) DEFAULT 'Crédito Pyme',
    monto_desembolsado DECIMAL(12,2) DEFAULT 0,
    monto_aprobado DECIMAL(12,2) DEFAULT 0,
    saldo_capital DECIMAL(12,2) DEFAULT 0,
    saldo_total DECIMAL(12,2) DEFAULT 0,
    tea DECIMAL(5,2) DEFAULT 0,
    plazo_meses INTEGER DEFAULT 0,
    cuotas_total INTEGER DEFAULT 0,
    cuotas_pagadas INTEGER DEFAULT 0,
    dias_mora INTEGER DEFAULT 0,
    estado VARCHAR(20) DEFAULT 'vigente' CHECK (estado IN ('vigente','pagado','vencido','castigado','cancelado')),
    fecha_desembolso DATE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE cronograma_credito (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    credito_id UUID NOT NULL REFERENCES creditos(id) ON DELETE CASCADE,
    nro_cuota INTEGER NOT NULL,
    fecha_vencimiento DATE NOT NULL,
    monto_cuota DECIMAL(10,2) DEFAULT 0,
    monto_capital DECIMAL(10,2) DEFAULT 0,
    monto_interes DECIMAL(10,2) DEFAULT 0,
    saldo DECIMAL(12,2) DEFAULT 0,
    estado_cuota VARCHAR(20) DEFAULT 'pendiente' CHECK (estado_cuota IN ('pendiente','pagada','vencida')),
    fecha_pago DATE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (credito_id, nro_cuota)
);

CREATE TABLE movimientos_cuenta (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cuenta_id UUID REFERENCES cuentas_ahorro(id),
    cliente_id UUID NOT NULL REFERENCES clientes(id) ON DELETE CASCADE,
    tipo_movimiento VARCHAR(30) NOT NULL,
    concepto VARCHAR(120),
    canal VARCHAR(30) DEFAULT 'APP',
    monto DECIMAL(12,2) NOT NULL,
    moneda VARCHAR(3) DEFAULT 'PEN',
    saldo_resultante DECIMAL(12,2),
    fecha_operacion TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE cartera_diaria (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    asesor_id UUID NOT NULL REFERENCES asesores(id),
    cliente_id UUID NOT NULL REFERENCES clientes(id),
    fecha_asignacion DATE NOT NULL,
    tipo_gestion VARCHAR(30) NOT NULL CHECK (tipo_gestion IN ('RENOVACION','AMPLIACION','NUEVA_SOLICITUD','SEGUIMIENTO','RECUPERACION_MORA','DESERTOR')),
    prioridad VARCHAR(10) DEFAULT 'normal' CHECK (prioridad IN ('alta','media','normal')),
    score_prioridad INTEGER DEFAULT 0,
    monto_referencial DECIMAL(12,2) DEFAULT 0,
    estado_visita VARCHAR(20) DEFAULT 'pendiente' CHECK (estado_visita IN ('pendiente','visitado','no_encontrado','reagendado','negocio_cerrado')),
    resultado_visita VARCHAR(40),
    observacion_visita TEXT,
    lat_visita DECIMAL(10,7),
    lng_visita DECIMAL(10,7),
    precision_gps DECIMAL(10,2),
    distancia_negocio_metros DECIMAL(10,2),
    timestamp_visita TIMESTAMPTZ,
    orden_manual INTEGER,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (asesor_id, cliente_id, fecha_asignacion)
);

CREATE TABLE visitas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cartera_id UUID REFERENCES cartera_diaria(id) ON DELETE SET NULL,
    asesor_id UUID NOT NULL REFERENCES asesores(id),
    cliente_id UUID NOT NULL REFERENCES clientes(id),
    tipo_visita VARCHAR(30) DEFAULT 'campo',
    resultado VARCHAR(40) NOT NULL,
    observacion TEXT,
    lat DECIMAL(10,7),
    lng DECIMAL(10,7),
    precision_gps DECIMAL(10,2),
    distancia_negocio_metros DECIMAL(10,2),
    fecha_visita TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE solicitudes_credito (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cliente_id UUID NOT NULL REFERENCES clientes(id),
    asesor_id UUID REFERENCES asesores(id),
    agencia_id UUID REFERENCES agencias(id),
    canal VARCHAR(20) NOT NULL DEFAULT 'asesor' CHECK (canal IN ('cliente','asesor','web_core')),
    numero_expediente VARCHAR(30) UNIQUE NOT NULL,
    monto_solicitado DECIMAL(12,2) NOT NULL,
    monto_aprobado DECIMAL(12,2),
    plazo_meses INTEGER NOT NULL,
    moneda VARCHAR(3) DEFAULT 'PEN',
    tipo_cuota VARCHAR(20) DEFAULT 'mensual',
    destino_credito TEXT,
    cuota_estimada DECIMAL(10,2),
    tea_referencial DECIMAL(5,2),
    estado VARCHAR(30) NOT NULL DEFAULT 'enviado' CHECK (estado IN ('borrador','enviado','recibido','en_evaluacion','observado','aprobado','rechazado','desembolsado')),
    motivo_rechazo TEXT,
    observacion_analista TEXT,
    firma_cliente_url TEXT,
    lat_captura DECIMAL(10,7),
    lng_captura DECIMAL(10,7),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE solicitud_estado_historial (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    solicitud_id UUID NOT NULL REFERENCES solicitudes_credito(id) ON DELETE CASCADE,
    estado_anterior VARCHAR(30),
    estado_nuevo VARCHAR(30) NOT NULL,
    usuario_id UUID REFERENCES usuarios(id),
    comentario TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE evaluaciones_crediticias (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    solicitud_id UUID REFERENCES solicitudes_credito(id) ON DELETE SET NULL,
    cliente_id UUID NOT NULL REFERENCES clientes(id),
    asesor_id UUID REFERENCES asesores(id),
    ingresos_estimados DECIMAL(12,2) DEFAULT 0,
    gastos_estimados DECIMAL(12,2) DEFAULT 0,
    capacidad_pago DECIMAL(12,2) DEFAULT 0,
    ratio_endeudamiento DECIMAL(8,4) DEFAULT 0,
    puntaje INTEGER DEFAULT 0,
    calificacion VARCHAR(30),
    resultado VARCHAR(20) CHECK (resultado IN ('APTO','REVISAR','NO_PROCEDE')),
    motivo TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE consultas_buro (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    solicitud_id UUID REFERENCES solicitudes_credito(id) ON DELETE SET NULL,
    cliente_id UUID REFERENCES clientes(id) ON DELETE SET NULL,
    dni_consultado VARCHAR(15) NOT NULL,
    calificacion_sbs VARCHAR(30),
    entidades_con_deuda INTEGER DEFAULT 0,
    deuda_total DECIMAL(12,2) DEFAULT 0,
    dias_mayor_mora INTEGER DEFAULT 0,
    en_lista_negra BOOLEAN DEFAULT FALSE,
    resultado_json JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE documentos_solicitud (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    solicitud_id UUID NOT NULL REFERENCES solicitudes_credito(id) ON DELETE CASCADE,
    cliente_id UUID NOT NULL REFERENCES clientes(id),
    tipo_documento VARCHAR(50) NOT NULL,
    storage_path TEXT,
    storage_url TEXT,
    mime_type VARCHAR(80),
    tamanio_kb INTEGER,
    estado_validacion VARCHAR(20) DEFAULT 'pendiente' CHECK (estado_validacion IN ('pendiente','aprobado','rechazado')),
    observacion TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE operaciones (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cliente_id UUID NOT NULL REFERENCES clientes(id),
    cuenta_origen_id UUID REFERENCES cuentas_ahorro(id),
    cuenta_destino_id UUID REFERENCES cuentas_ahorro(id),
    tipo_operacion VARCHAR(40) NOT NULL CHECK (tipo_operacion IN ('TRANSFERENCIA_PROPIA','TRANSFERENCIA_TERCEROS','PAGO_CREDITO','PAGO_SERVICIO','PAGO_QR','PAGO_TELEFONO','RECARGA')),
    monto DECIMAL(12,2) NOT NULL,
    moneda VARCHAR(3) DEFAULT 'PEN',
    estado VARCHAR(20) DEFAULT 'procesada' CHECK (estado IN ('pendiente','procesada','rechazada','anulada')),
    canal VARCHAR(20) DEFAULT 'APP_CLIENTE',
    codigo_operacion VARCHAR(40) UNIQUE NOT NULL,
    descripcion TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE comprobantes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    operacion_id UUID NOT NULL REFERENCES operaciones(id) ON DELETE CASCADE,
    numero_comprobante VARCHAR(40) UNIQUE NOT NULL,
    cliente_id UUID NOT NULL REFERENCES clientes(id),
    monto DECIMAL(12,2) NOT NULL,
    descripcion TEXT,
    fecha_emision TIMESTAMPTZ NOT NULL DEFAULT now(),
    url_pdf TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE tarjetas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cliente_id UUID NOT NULL REFERENCES clientes(id),
    numero_enmascarado VARCHAR(30) NOT NULL,
    marca VARCHAR(30) DEFAULT 'VISA',
    tipo_tarjeta VARCHAR(30) DEFAULT 'debito',
    linea_credito DECIMAL(12,2) DEFAULT 0,
    saldo_utilizado DECIMAL(12,2) DEFAULT 0,
    fecha_corte DATE,
    fecha_pago DATE,
    compras_internet BOOLEAN DEFAULT TRUE,
    estado VARCHAR(20) DEFAULT 'activa' CHECK (estado IN ('activa','bloqueada','vencida','cancelada')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE notificaciones (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    usuario_id UUID REFERENCES usuarios(id) ON DELETE SET NULL,
    cliente_id UUID REFERENCES clientes(id) ON DELETE CASCADE,
    titulo VARCHAR(120) NOT NULL,
    mensaje TEXT,
    tipo VARCHAR(30) DEFAULT 'general',
    leida BOOLEAN NOT NULL DEFAULT FALSE,
    canal VARCHAR(20) DEFAULT 'APP',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE auditoria (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    usuario_id UUID REFERENCES usuarios(id) ON DELETE SET NULL,
    accion VARCHAR(80) NOT NULL,
    modulo VARCHAR(80) NOT NULL,
    entidad VARCHAR(80),
    entidad_id UUID,
    descripcion TEXT,
    ip VARCHAR(60),
    user_agent TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- updated_at automático
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_usuarios_updated BEFORE UPDATE ON usuarios FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE TRIGGER trg_clientes_updated BEFORE UPDATE ON clientes FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE TRIGGER trg_cliente_negocios_updated BEFORE UPDATE ON cliente_negocios FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE TRIGGER trg_asesores_updated BEFORE UPDATE ON asesores FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE TRIGGER trg_cuentas_updated BEFORE UPDATE ON cuentas_ahorro FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE TRIGGER trg_creditos_updated BEFORE UPDATE ON creditos FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE TRIGGER trg_cartera_updated BEFORE UPDATE ON cartera_diaria FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE TRIGGER trg_solicitudes_updated BEFORE UPDATE ON solicitudes_credito FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE TRIGGER trg_tarjetas_updated BEFORE UPDATE ON tarjetas FOR EACH ROW EXECUTE FUNCTION set_updated_at();
