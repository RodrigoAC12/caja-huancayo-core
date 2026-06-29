from datetime import date, datetime
from decimal import Decimal
from uuid import UUID
from sqlalchemy import text
from sqlalchemy.orm import Session


def clean_value(v):
    if isinstance(v, Decimal):
        return float(v)
    if isinstance(v, (datetime, date)):
        return v.isoformat()
    if isinstance(v, UUID):
        return str(v)
    return v


def row_to_dict(row):
    if row is None:
        return None
    mapping = row._mapping if hasattr(row, "_mapping") else row
    return {k: clean_value(v) for k, v in dict(mapping).items()}


def rows_to_dicts(rows):
    return [row_to_dict(r) for r in rows]


def audit(db: Session, user: dict | None, accion: str, modulo: str, entidad: str | None = None, entidad_id: str | None = None, descripcion: str | None = None):
    try:
        db.execute(
            text("""
                INSERT INTO auditoria (usuario_id, accion, modulo, entidad, entidad_id, descripcion)
                VALUES (:usuario_id, :accion, :modulo, :entidad, CAST(:entidad_id AS uuid), :descripcion)
            """),
            {
                "usuario_id": user.get("id") if user else None,
                "accion": accion,
                "modulo": modulo,
                "entidad": entidad,
                "entidad_id": entidad_id,
                "descripcion": descripcion,
            },
        )
    except Exception:
        # La auditoría no debe interrumpir el flujo principal de la operación.
        pass
