-- Actualiza los tipos de operación permitidos para pagos móviles y QR.
ALTER TABLE operaciones DROP CONSTRAINT IF EXISTS operaciones_tipo_operacion_check;
ALTER TABLE operaciones ADD CONSTRAINT operaciones_tipo_operacion_check
CHECK (tipo_operacion IN (
    'TRANSFERENCIA_PROPIA',
    'TRANSFERENCIA_TERCEROS',
    'PAGO_CREDITO',
    'PAGO_SERVICIO',
    'PAGO_QR',
    'PAGO_TELEFONO',
    'RECARGA'
));
