from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.auth_deps import require_personal
from app.core.database import get_db
from app.core.db_utils import audit, row_to_dict, rows_to_dicts

router = APIRouter()


class ClienteUbicacionIn(BaseModel):
    direccion: str | None = None
    referencia_direccion: str | None = None
    latitud_domicilio: float | None = None
    longitud_domicilio: float | None = None
    nombre_negocio: str | None = None
    direccion_negocio: str | None = None
    referencia_negocio: str | None = None
    lat_negocio: float | None = None
    lng_negocio: float | None = None
    ubicacion_verificada: bool | None = None
    fuente_ubicacion: str | None = None
    precision_ubicacion_metros: float | None = None


@router.get("")
def listar_clientes(q: str | None = None, user: dict = Depends(require_personal), db: Session = Depends(get_db)):
    sql = """
        SELECT
            c.*,
            n.nombre_negocio,
            n.tipo_negocio,
            n.direccion_negocio,
            n.referencia_negocio,
            n.lat AS lat_negocio,
            n.lng AS lng_negocio,
            n.ubicacion_verificada,
            n.fuente_ubicacion,
            n.precision_ubicacion_metros,
            n.fecha_verificacion_ubicacion,
            n.ingresos_estimados
        FROM clientes c
        LEFT JOIN cliente_negocios n ON n.cliente_id = c.id
        WHERE (:q IS NULL OR c.numero_documento ILIKE :like OR c.nombres ILIKE :like OR c.apellidos ILIKE :like)
        ORDER BY c.created_at DESC
        LIMIT 100
    """
    rows = db.execute(text(sql), {"q": q, "like": f"%{q or ''}%"}).all()
    return rows_to_dicts(rows)


@router.get("/{cliente_id}/ficha")
def ficha(cliente_id: str, user: dict = Depends(require_personal), db: Session = Depends(get_db)):
    cliente = row_to_dict(db.execute(text("SELECT * FROM clientes WHERE id = :id"), {"id": cliente_id}).first())
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    negocio = row_to_dict(db.execute(text("SELECT * FROM cliente_negocios WHERE cliente_id = :id LIMIT 1"), {"id": cliente_id}).first())
    cuentas = rows_to_dicts(db.execute(text("SELECT * FROM cuentas_ahorro WHERE cliente_id = :id"), {"id": cliente_id}).all())
    creditos = rows_to_dicts(db.execute(text("SELECT * FROM creditos WHERE cliente_id = :id"), {"id": cliente_id}).all())
    solicitudes = rows_to_dicts(db.execute(text("SELECT * FROM solicitudes_credito WHERE cliente_id = :id ORDER BY created_at DESC"), {"id": cliente_id}).all())
    movimientos = rows_to_dicts(db.execute(text("SELECT * FROM movimientos_cuenta WHERE cliente_id = :id ORDER BY fecha_operacion DESC LIMIT 10"), {"id": cliente_id}).all())
    visitas = rows_to_dicts(db.execute(text("""
        SELECT v.*, a.codigo_empleado, a.nombres || ' ' || a.apellidos AS asesor_nombre
        FROM visitas v
        JOIN asesores a ON a.id = v.asesor_id
        WHERE v.cliente_id = :id
        ORDER BY v.fecha_visita DESC
        LIMIT 10
    """), {"id": cliente_id}).all())
    return {
        "cliente": cliente,
        "negocio": negocio,
        "cuentas": cuentas,
        "creditos": creditos,
        "solicitudes": solicitudes,
        "movimientos": movimientos,
        "visitas": visitas,
    }


@router.patch("/{cliente_id}/ubicacion")
def actualizar_ubicacion(
    cliente_id: str,
    data: ClienteUbicacionIn,
    user: dict = Depends(require_personal),
    db: Session = Depends(get_db),
):
    cliente = row_to_dict(db.execute(text("SELECT id FROM clientes WHERE id = :id"), {"id": cliente_id}).first())
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    db.execute(text("""
        UPDATE clientes
        SET direccion = COALESCE(:direccion, direccion),
            referencia_direccion = COALESCE(:referencia_direccion, referencia_direccion),
            latitud_domicilio = COALESCE(:latitud_domicilio, latitud_domicilio),
            longitud_domicilio = COALESCE(:longitud_domicilio, longitud_domicilio)
        WHERE id = :cliente_id
    """), {
        "cliente_id": cliente_id,
        "direccion": data.direccion,
        "referencia_direccion": data.referencia_direccion,
        "latitud_domicilio": data.latitud_domicilio,
        "longitud_domicilio": data.longitud_domicilio,
    })

    negocio = row_to_dict(db.execute(text("SELECT id FROM cliente_negocios WHERE cliente_id = :cliente_id LIMIT 1"), {"cliente_id": cliente_id}).first())
    if negocio:
        db.execute(text("""
            UPDATE cliente_negocios
            SET nombre_negocio = COALESCE(:nombre_negocio, nombre_negocio),
                direccion_negocio = COALESCE(:direccion_negocio, direccion_negocio),
                referencia_negocio = COALESCE(:referencia_negocio, referencia_negocio),
                lat = COALESCE(:lat_negocio, lat),
                lng = COALESCE(:lng_negocio, lng),
                ubicacion_verificada = COALESCE(:ubicacion_verificada, ubicacion_verificada),
                fuente_ubicacion = COALESCE(:fuente_ubicacion, fuente_ubicacion),
                precision_ubicacion_metros = COALESCE(:precision_ubicacion_metros, precision_ubicacion_metros),
                fecha_verificacion_ubicacion = CASE WHEN :lat_negocio IS NOT NULL AND :lng_negocio IS NOT NULL THEN now() ELSE fecha_verificacion_ubicacion END,
                usuario_verificacion_id = CASE WHEN :lat_negocio IS NOT NULL AND :lng_negocio IS NOT NULL THEN :usuario_id ELSE usuario_verificacion_id END,
                updated_at = now()
            WHERE id = :negocio_id
        """), {
            "negocio_id": negocio["id"],
            "nombre_negocio": data.nombre_negocio,
            "direccion_negocio": data.direccion_negocio,
            "referencia_negocio": data.referencia_negocio,
            "lat_negocio": data.lat_negocio,
            "lng_negocio": data.lng_negocio,
            "ubicacion_verificada": data.ubicacion_verificada,
            "fuente_ubicacion": data.fuente_ubicacion,
            "precision_ubicacion_metros": data.precision_ubicacion_metros,
            "usuario_id": user["id"],
        })
    elif data.nombre_negocio or data.direccion_negocio or data.lat_negocio or data.lng_negocio:
        db.execute(text("""
            INSERT INTO cliente_negocios (
                cliente_id, nombre_negocio, direccion_negocio, referencia_negocio, lat, lng,
                ubicacion_verificada, fuente_ubicacion, precision_ubicacion_metros,
                fecha_verificacion_ubicacion, usuario_verificacion_id
            )
            VALUES (
                :cliente_id, :nombre_negocio, :direccion_negocio, :referencia_negocio, :lat_negocio, :lng_negocio,
                COALESCE(:ubicacion_verificada, FALSE), :fuente_ubicacion, :precision_ubicacion_metros,
                CASE WHEN :lat_negocio IS NOT NULL AND :lng_negocio IS NOT NULL THEN now() ELSE NULL END,
                CASE WHEN :lat_negocio IS NOT NULL AND :lng_negocio IS NOT NULL THEN :usuario_id ELSE NULL END
            )
        """), {
            "cliente_id": cliente_id,
            "nombre_negocio": data.nombre_negocio,
            "direccion_negocio": data.direccion_negocio,
            "referencia_negocio": data.referencia_negocio,
            "lat_negocio": data.lat_negocio,
            "lng_negocio": data.lng_negocio,
            "ubicacion_verificada": data.ubicacion_verificada,
            "fuente_ubicacion": data.fuente_ubicacion,
            "precision_ubicacion_metros": data.precision_ubicacion_metros,
            "usuario_id": user["id"],
        })

    audit(db, user, "ACTUALIZAR_UBICACION", "clientes", "clientes", cliente_id, "Ubicación de domicilio/negocio actualizada")
    db.commit()
    return ficha(cliente_id, user, db)
