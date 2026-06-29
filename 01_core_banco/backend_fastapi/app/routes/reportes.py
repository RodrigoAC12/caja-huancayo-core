from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.auth_deps import require_personal
from app.core.db_utils import row_to_dict, rows_to_dicts

router = APIRouter()

@router.get("/dashboard")
def dashboard(user: dict = Depends(require_personal), db: Session = Depends(get_db)):
    stats = {}
    for key, sql in {
        "clientes": "SELECT COUNT(*) AS total FROM clientes",
        "solicitudes": "SELECT COUNT(*) AS total FROM solicitudes_credito",
        "aprobadas": "SELECT COUNT(*) AS total FROM solicitudes_credito WHERE estado = 'aprobado'",
        "cartera_pendiente": "SELECT COUNT(*) AS total FROM cartera_diaria WHERE estado_visita = 'pendiente' AND fecha_asignacion = current_date",
        "visitas_hoy": "SELECT COUNT(*) AS total FROM visitas WHERE fecha_visita::date = current_date",
        "visitas_gps_valido": "SELECT COUNT(*) AS total FROM visitas WHERE fecha_visita::date = current_date AND lat IS NOT NULL AND lng IS NOT NULL",
    }.items():
        stats[key] = row_to_dict(db.execute(text(sql)).first())["total"]
    monto = row_to_dict(db.execute(text("SELECT COALESCE(SUM(monto_solicitado),0) AS total FROM solicitudes_credito")).first())["total"]
    stats["monto_solicitado"] = monto
    recientes = rows_to_dicts(db.execute(text("""
        SELECT s.numero_expediente, s.estado, s.monto_solicitado, c.nombres || ' ' || c.apellidos AS cliente_nombre, s.created_at
        FROM solicitudes_credito s JOIN clientes c ON c.id = s.cliente_id
        ORDER BY s.created_at DESC LIMIT 5
    """)).all())
    return {"stats": stats, "solicitudes_recientes": recientes}

@router.get("/productividad")
def productividad(user: dict = Depends(require_personal), db: Session = Depends(get_db)):
    rows = db.execute(text("""
        SELECT a.nombres || ' ' || a.apellidos AS asesor_nombre,
               COUNT(DISTINCT s.id) AS enviadas,
               COUNT(DISTINCT s.id) FILTER (WHERE s.estado IN ('aprobado','desembolsado')) AS aprobadas,
               COALESCE(SUM(s.monto_solicitado),0) AS monto_total,
               ROUND(CASE WHEN COUNT(DISTINCT s.id) > 0 THEN COUNT(DISTINCT s.id) FILTER (WHERE s.estado IN ('aprobado','desembolsado'))::numeric / COUNT(DISTINCT s.id)::numeric * 100 ELSE 0 END, 1) AS tasa_aprobacion,
               COUNT(DISTINCT v.id) AS visitas_registradas,
               COUNT(DISTINCT v.id) FILTER (WHERE v.lat IS NOT NULL AND v.lng IS NOT NULL) AS visitas_con_gps,
               ROUND(AVG(v.distancia_negocio_metros), 1) AS distancia_promedio_metros
        FROM asesores a
        LEFT JOIN solicitudes_credito s ON s.asesor_id = a.id
        LEFT JOIN visitas v ON v.asesor_id = a.id
        GROUP BY a.id, a.nombres, a.apellidos
        ORDER BY enviadas DESC
    """)).all()
    return rows_to_dicts(rows)
