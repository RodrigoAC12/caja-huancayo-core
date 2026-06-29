from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import verify_password, create_access_token
from app.core.auth_deps import get_current_user, require_personal
from app.core.db_utils import row_to_dict, audit
from app.schemas.base import LoginPersonalIn, TokenOut

router = APIRouter()


def _build_user_payload(db: Session, usuario_id: str) -> dict:
    row = db.execute(
        text("""
            SELECT u.id, u.username, u.tipo_usuario, r.nombre AS rol,
                   a.id AS asesor_id, a.codigo_empleado, a.nombres, a.apellidos,
                   a.perfil, a.agencia_id
            FROM usuarios u
            JOIN roles r ON r.id = u.rol_id
            LEFT JOIN asesores a ON a.usuario_id = u.id
            WHERE u.id = :id
        """),
        {"id": usuario_id},
    ).first()
    return row_to_dict(row)

@router.post("/login", response_model=TokenOut)
def login(data: LoginPersonalIn, db: Session = Depends(get_db)):
    username = data.username or data.codigo_empleado
    if not username:
        raise HTTPException(status_code=422, detail="Debe enviar username o codigo_empleado")

    row = db.execute(
        text("SELECT * FROM usuarios WHERE username = :username AND tipo_usuario = 'personal'"),
        {"username": username},
    ).first()
    user_db = row_to_dict(row)
    if not user_db:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales inválidas")
    if user_db["estado"] != "activo":
        raise HTTPException(status_code=423, detail="Usuario bloqueado o inactivo")
    if user_db.get("bloqueado_hasta") and datetime.fromisoformat(user_db["bloqueado_hasta"]) > datetime.now(timezone.utc):
        raise HTTPException(status_code=423, detail="Usuario bloqueado temporalmente")

    if not verify_password(data.password, user_db["password_hash"]):
        db.execute(
            text("""
                UPDATE usuarios
                SET intentos_fallidos = intentos_fallidos + 1,
                    bloqueado_hasta = CASE WHEN intentos_fallidos + 1 >= 5 THEN now() + interval '10 minutes' ELSE bloqueado_hasta END
                WHERE id = :id
            """),
            {"id": user_db["id"]},
        )
        db.commit()
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales inválidas")

    db.execute(text("UPDATE usuarios SET intentos_fallidos = 0, bloqueado_hasta = NULL, ultimo_login = now() WHERE id = :id"), {"id": user_db["id"]})
    profile = _build_user_payload(db, user_db["id"])
    audit(db, profile, "LOGIN", "auth", "usuarios", user_db["id"], "Ingreso al portal interno")
    db.commit()
    token = create_access_token({"sub": user_db["id"], "rol": profile["rol"], "tipo_usuario": "personal"})
    return {"access_token": token, "token_type": "bearer", "user": profile}

@router.get("/me")
def me(user: dict = Depends(get_current_user)):
    return user

@router.post("/logout")
def logout(user: dict = Depends(require_personal), db: Session = Depends(get_db)):
    audit(db, user, "LOGOUT", "auth", "usuarios", user["id"], "Salida del portal interno")
    db.commit()
    return {"status": "ok"}
