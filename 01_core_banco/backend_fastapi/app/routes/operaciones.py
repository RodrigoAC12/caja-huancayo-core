from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.auth_deps import require_personal
from app.core.db_utils import rows_to_dicts

router = APIRouter()

@router.get("")
def listar_operaciones(user: dict = Depends(require_personal), db: Session = Depends(get_db)):
    rows = db.execute(text("""
        SELECT o.*, c.nombres || ' ' || c.apellidos AS cliente_nombre, c.numero_documento
        FROM operaciones o
        JOIN clientes c ON c.id = o.cliente_id
        ORDER BY o.created_at DESC
        LIMIT 100
    """)).all()
    return rows_to_dicts(rows)
