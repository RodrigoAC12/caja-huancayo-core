from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.auth_deps import require_personal
from app.core.db_utils import row_to_dict, rows_to_dicts, audit
from app.schemas.base import SolicitudIn, EstadoSolicitudIn
import uuid

router = APIRouter()


def _asesor(db: Session, user: dict):
    return row_to_dict(db.execute(text("SELECT * FROM asesores WHERE usuario_id = :uid"), {"uid": user["id"]}).first())


def _upsert_cliente(db: Session, data: SolicitudIn) -> str:
    if data.cliente_id:
        row = db.execute(text("SELECT id FROM clientes WHERE id = :id"), {"id": data.cliente_id}).first()
        if row:
            return data.cliente_id
    if not data.numero_documento:
        raise HTTPException(status_code=422, detail="Debe enviar cliente_id o numero_documento")
    row = db.execute(text("SELECT id FROM clientes WHERE numero_documento = :doc"), {"doc": data.numero_documento}).first()
    cliente = row_to_dict(row)
    if cliente:
        return cliente["id"]
    cid = str(uuid.uuid4())
    db.execute(text("""
        INSERT INTO clientes (id, numero_documento, nombres, apellidos, telefono)
        VALUES (:id, :doc, :nom, :ape, :tel)
    """), {"id": cid, "doc": data.numero_documento, "nom": data.nombres or "Cliente", "ape": data.apellidos or "Nuevo", "tel": data.telefono})
    return cid

@router.get("")
def listar(estado: str | None = None, user: dict = Depends(require_personal), db: Session = Depends(get_db)):
    where = "WHERE (:estado IS NULL OR s.estado = :estado)"
    params = {"estado": estado}
    asesor = _asesor(db, user)
    if user["rol"] == "asesor" and asesor:
        where += " AND s.asesor_id = :asesor"
        params["asesor"] = asesor["id"]
    rows = db.execute(text(f"""
        SELECT s.*, c.numero_documento, c.nombres || ' ' || c.apellidos AS cliente_nombre,
               a.nombres || ' ' || a.apellidos AS asesor_nombre
        FROM solicitudes_credito s
        JOIN clientes c ON c.id = s.cliente_id
        LEFT JOIN asesores a ON a.id = s.asesor_id
        {where}
        ORDER BY s.created_at DESC
    """), params).all()
    return rows_to_dicts(rows)

@router.post("")
def crear(data: SolicitudIn, user: dict = Depends(require_personal), db: Session = Depends(get_db)):
    asesor = _asesor(db, user)
    cliente_id = _upsert_cliente(db, data)
    sol_id = str(uuid.uuid4())
    expediente = "EXP-ASE-" + sol_id.replace("-", "")[:8].upper()
    db.execute(text("""
        INSERT INTO solicitudes_credito (id, cliente_id, asesor_id, agencia_id, canal, numero_expediente, monto_solicitado, plazo_meses, destino_credito, cuota_estimada, tea_referencial, estado, lat_captura, lng_captura)
        VALUES (:id, :cliente, CAST(:asesor AS uuid), CAST(:agencia AS uuid), 'asesor', :exp, :monto, :plazo, :destino, :cuota, :tea, 'enviado', :lat, :lng)
    """), {"id": sol_id, "cliente": cliente_id, "asesor": asesor["id"] if asesor else None, "agencia": asesor["agencia_id"] if asesor else None, "exp": expediente, "monto": data.monto_solicitado, "plazo": data.plazo_meses, "destino": data.destino_credito, "cuota": data.cuota_estimada, "tea": data.tea_referencial, "lat": data.lat_captura, "lng": data.lng_captura})
    db.execute(text("INSERT INTO solicitud_estado_historial (solicitud_id, estado_nuevo, usuario_id, comentario) VALUES (:id, 'enviado', :user, 'Solicitud creada desde fuerza de ventas')"), {"id": sol_id, "user": user["id"]})
    audit(db, user, "CREAR_SOLICITUD", "solicitudes", "solicitudes_credito", sol_id, expediente)
    db.commit()
    return {"id": sol_id, "numero_expediente": expediente, "estado": "enviado"}

@router.get("/{solicitud_id}")
def detalle(solicitud_id: str, user: dict = Depends(require_personal), db: Session = Depends(get_db)):
    solicitud = row_to_dict(db.execute(text("""
        SELECT s.*, c.numero_documento, c.nombres || ' ' || c.apellidos AS cliente_nombre,
               a.nombres || ' ' || a.apellidos AS asesor_nombre
        FROM solicitudes_credito s
        JOIN clientes c ON c.id = s.cliente_id
        LEFT JOIN asesores a ON a.id = s.asesor_id
        WHERE s.id = :id
    """), {"id": solicitud_id}).first())
    if not solicitud:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")
    historial = rows_to_dicts(db.execute(text("SELECT * FROM solicitud_estado_historial WHERE solicitud_id = :id ORDER BY created_at"), {"id": solicitud_id}).all())
    evaluaciones = rows_to_dicts(db.execute(text("SELECT * FROM evaluaciones_crediticias WHERE solicitud_id = :id ORDER BY created_at DESC"), {"id": solicitud_id}).all())
    buro = rows_to_dicts(db.execute(text("SELECT * FROM consultas_buro WHERE solicitud_id = :id ORDER BY created_at DESC"), {"id": solicitud_id}).all())
    documentos = rows_to_dicts(db.execute(text("SELECT * FROM documentos_solicitud WHERE solicitud_id = :id ORDER BY created_at DESC"), {"id": solicitud_id}).all())
    return {"solicitud": solicitud, "historial": historial, "evaluaciones": evaluaciones, "buro": buro, "documentos": documentos}

@router.patch("/{solicitud_id}/estado")
def cambiar_estado(solicitud_id: str, data: EstadoSolicitudIn, user: dict = Depends(require_personal), db: Session = Depends(get_db)):
    actual = row_to_dict(db.execute(text("SELECT * FROM solicitudes_credito WHERE id = :id"), {"id": solicitud_id}).first())
    if not actual:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")
    permitidos = {'borrador','enviado','recibido','en_evaluacion','observado','aprobado','rechazado','desembolsado'}
    if data.estado not in permitidos:
        raise HTTPException(status_code=422, detail="Estado no permitido")
    db.execute(text("""
        UPDATE solicitudes_credito
        SET estado = :estado, monto_aprobado = COALESCE(:monto, monto_aprobado), motivo_rechazo = :motivo, observacion_analista = :comentario
        WHERE id = :id
    """), {"estado": data.estado, "monto": data.monto_aprobado, "motivo": data.motivo_rechazo, "comentario": data.comentario, "id": solicitud_id})
    db.execute(text("""
        INSERT INTO solicitud_estado_historial (solicitud_id, estado_anterior, estado_nuevo, usuario_id, comentario)
        VALUES (:id, :anterior, :nuevo, :user, :comentario)
    """), {"id": solicitud_id, "anterior": actual["estado"], "nuevo": data.estado, "user": user["id"], "comentario": data.comentario})
    db.execute(text("""
        INSERT INTO notificaciones (cliente_id, titulo, mensaje, tipo)
        VALUES (:cliente, 'Actualización de solicitud', :msg, 'solicitud')
    """), {"cliente": actual["cliente_id"], "msg": f"Tu solicitud {actual['numero_expediente']} cambió a estado: {data.estado}."})
    audit(db, user, "CAMBIAR_ESTADO", "solicitudes", "solicitudes_credito", solicitud_id, f"{actual['estado']} -> {data.estado}")
    db.commit()
    return {"status": "ok", "estado": data.estado}
