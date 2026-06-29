from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.auth_deps import require_personal
from app.core.db_utils import rows_to_dicts

router = APIRouter()

@router.get("/agencias")
def agencias(user: dict = Depends(require_personal), db: Session = Depends(get_db)):
    return rows_to_dicts(db.execute(text("SELECT * FROM agencias ORDER BY nombre")).all())

@router.get("/asesores")
def asesores(user: dict = Depends(require_personal), db: Session = Depends(get_db)):
    return rows_to_dicts(db.execute(text("SELECT a.*, ag.nombre AS agencia_nombre FROM asesores a LEFT JOIN agencias ag ON ag.id = a.agencia_id ORDER BY a.nombres")).all())
