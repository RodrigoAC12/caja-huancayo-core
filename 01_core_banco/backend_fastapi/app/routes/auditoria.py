from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.auth_deps import require_roles
from app.core.db_utils import rows_to_dicts

router = APIRouter()

@router.get("")
def listar_auditoria(user: dict = Depends(require_roles("admin", "supervisor")), db: Session = Depends(get_db)):
    rows = db.execute(text("""
        SELECT au.*, u.username, r.nombre AS rol
        FROM auditoria au
        LEFT JOIN usuarios u ON u.id = au.usuario_id
        LEFT JOIN roles r ON r.id = u.rol_id
        ORDER BY au.created_at DESC
        LIMIT 150
    """)).all()
    return rows_to_dicts(rows)
