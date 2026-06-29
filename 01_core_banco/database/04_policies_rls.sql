-- Supabase RLS opcional.
-- La API FastAPI es la única capa autorizada para usar directamente la base de datos.
-- Por eso no se activan políticas RLS por defecto.
-- Si se decide exponer Supabase directamente a clientes, habilitar RLS tabla por tabla.

-- Ejemplo referencial:
-- ALTER TABLE clientes ENABLE ROW LEVEL SECURITY;
-- CREATE POLICY clientes_select_own ON clientes
-- FOR SELECT USING (auth.uid()::text = usuario_id::text);
