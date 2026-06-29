from datetime import date
from math import atan2, cos, radians, sin, sqrt
import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.auth_deps import require_personal
from app.core.database import get_db
from app.core.db_utils import audit, row_to_dict, rows_to_dicts
from app.schemas.base import VisitaIn

router = APIRouter()

ESTADOS_VISITA_VALIDOS = {"pendiente", "visitado", "no_encontrado", "reagendado", "negocio_cerrado"}


def _asesor_id(db: Session, user: dict) -> str | None:
    row = db.execute(text("SELECT id FROM asesores WHERE usuario_id = :uid"), {"uid": user["id"]}).first()
    data = row_to_dict(row)
    return data["id"] if data else None


def _distance_meters(lat1: float | None, lng1: float | None, lat2: float | None, lng2: float | None) -> float | None:
    """Distancia aproximada Haversine para validar visita vs. ubicación de negocio."""
    if None in (lat1, lng1, lat2, lng2):
        return None
    radius = 6371000
    phi1 = radians(float(lat1))
    phi2 = radians(float(lat2))
    d_phi = radians(float(lat2) - float(lat1))
    d_lambda = radians(float(lng2) - float(lng1))
    a = sin(d_phi / 2) ** 2 + cos(phi1) * cos(phi2) * sin(d_lambda / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return round(radius * c, 2)


@router.get("")
def listar_cartera(
    fecha: date | None = None,
    user: dict = Depends(require_personal),
    db: Session = Depends(get_db),
):
    f = fecha or date.today()
    asesor_id = _asesor_id(db, user)
    where = "WHERE cd.fecha_asignacion = :fecha"
    params = {"fecha": f}
    if user["rol"] == "asesor":
        where += " AND cd.asesor_id = :asesor"
        params["asesor"] = asesor_id

    rows = db.execute(
        text(
            f"""
            SELECT
                cd.*,
                c.numero_documento,
                c.nombres || ' ' || c.apellidos AS cliente_nombre,
                c.telefono,
                c.direccion AS direccion_domicilio,
                c.referencia_direccion,
                c.departamento AS cliente_departamento,
                c.provincia AS cliente_provincia,
                c.distrito AS cliente_distrito,
                c.latitud_domicilio,
                c.longitud_domicilio,
                n.nombre_negocio,
                n.tipo_negocio,
                n.actividad_economica,
                n.direccion_negocio,
                n.referencia_negocio,
                n.departamento AS negocio_departamento,
                n.provincia AS negocio_provincia,
                n.distrito AS negocio_distrito,
                n.lat AS lat,
                n.lng AS lng,
                n.lat AS lat_negocio,
                n.lng AS lng_negocio,
                n.ubicacion_verificada,
                n.fuente_ubicacion,
                n.precision_ubicacion_metros,
                n.fecha_verificacion_ubicacion,
                a.nombres || ' ' || a.apellidos AS asesor_nombre
            FROM cartera_diaria cd
            JOIN clientes c ON c.id = cd.cliente_id
            LEFT JOIN cliente_negocios n ON n.cliente_id = c.id
            JOIN asesores a ON a.id = cd.asesor_id
            {where}
            ORDER BY cd.orden_manual NULLS LAST, cd.prioridad, cd.score_prioridad DESC
            """
        ),
        params,
    ).all()
    return rows_to_dicts(rows)


@router.post("/{cartera_id}/visita")
def registrar_visita(
    cartera_id: str,
    data: VisitaIn,
    user: dict = Depends(require_personal),
    db: Session = Depends(get_db),
):
    cartera = row_to_dict(db.execute(text("SELECT * FROM cartera_diaria WHERE id = :id"), {"id": cartera_id}).first())
    if not cartera:
        raise HTTPException(status_code=404, detail="Item de cartera no encontrado")

    if user["rol"] == "asesor":
        asesor_id = _asesor_id(db, user)
        if asesor_id != cartera["asesor_id"]:
            raise HTTPException(status_code=403, detail="La cartera no pertenece al asesor autenticado")

    negocio = row_to_dict(
        db.execute(text("SELECT lat, lng FROM cliente_negocios WHERE cliente_id = :cliente_id LIMIT 1"), {"cliente_id": cartera["cliente_id"]}).first()
    )
    distancia = _distance_meters(
        data.lat,
        data.lng,
        negocio.get("lat") if negocio else None,
        negocio.get("lng") if negocio else None,
    )

    estado_visita = data.resultado if data.resultado in ESTADOS_VISITA_VALIDOS else "visitado"
    visita_id = str(uuid.uuid4())
    db.execute(
        text(
            """
            INSERT INTO visitas (
                id, cartera_id, asesor_id, cliente_id, tipo_visita, resultado, observacion,
                lat, lng, precision_gps, distancia_negocio_metros
            )
            VALUES (
                :id, :cartera, :asesor, :cliente, :tipo_visita, :resultado, :obs,
                :lat, :lng, :precision_gps, :distancia
            )
            """
        ),
        {
            "id": visita_id,
            "cartera": cartera_id,
            "asesor": cartera["asesor_id"],
            "cliente": cartera["cliente_id"],
            "tipo_visita": data.tipo_visita or "campo",
            "resultado": data.resultado,
            "obs": data.observacion,
            "lat": data.lat,
            "lng": data.lng,
            "precision_gps": data.precision_gps,
            "distancia": distancia,
        },
    )
    db.execute(
        text(
            """
            UPDATE cartera_diaria
            SET estado_visita = :estado_visita,
                resultado_visita = :resultado,
                observacion_visita = :obs,
                lat_visita = :lat,
                lng_visita = :lng,
                precision_gps = :precision_gps,
                distancia_negocio_metros = :distancia,
                timestamp_visita = now()
            WHERE id = :id
            """
        ),
        {
            "estado_visita": estado_visita,
            "resultado": data.resultado,
            "obs": data.observacion,
            "lat": data.lat,
            "lng": data.lng,
            "precision_gps": data.precision_gps,
            "distancia": distancia,
            "id": cartera_id,
        },
    )
    audit(db, user, "REGISTRAR_VISITA_GPS", "cartera", "visitas", visita_id, f"{data.resultado}; distancia={distancia}")
    db.commit()
    return {
        "status": "ok",
        "visita_id": visita_id,
        "cartera_id": cartera_id,
        "estado_visita": estado_visita,
        "precision_gps": data.precision_gps,
        "distancia_negocio_metros": distancia,
    }


@router.get("/visitas")
def listar_visitas(
    fecha: date | None = None,
    cliente_id: str | None = None,
    user: dict = Depends(require_personal),
    db: Session = Depends(get_db),
):
    params: dict[str, object] = {"fecha": fecha or date.today(), "cliente_id": cliente_id}
    where = "WHERE v.fecha_visita::date = :fecha"
    if cliente_id:
        where += " AND v.cliente_id = CAST(:cliente_id AS uuid)"
    if user["rol"] == "asesor":
        asesor_id = _asesor_id(db, user)
        where += " AND v.asesor_id = :asesor_id"
        params["asesor_id"] = asesor_id
    rows = db.execute(
        text(
            f"""
            SELECT
                v.*,
                c.numero_documento,
                c.nombres || ' ' || c.apellidos AS cliente_nombre,
                n.nombre_negocio,
                n.direccion_negocio,
                n.lat AS lat_negocio,
                n.lng AS lng_negocio,
                n.ubicacion_verificada,
                n.fuente_ubicacion,
                n.precision_ubicacion_metros,
                a.codigo_empleado,
                a.nombres || ' ' || a.apellidos AS asesor_nombre
            FROM visitas v
            JOIN clientes c ON c.id = v.cliente_id
            LEFT JOIN cliente_negocios n ON n.cliente_id = c.id
            JOIN asesores a ON a.id = v.asesor_id
            {where}
            ORDER BY v.fecha_visita DESC
            """
        ),
        params,
    ).all()
    return rows_to_dicts(rows)
