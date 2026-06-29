from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import decode_token
from app.core.db_utils import row_to_dict

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> dict:
    try:
        payload = decode_token(token)
        user_id = payload.get("sub")
        if not user_id:
            raise ValueError("Token sin sujeto")
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido")

    row = db.execute(
        text("""
            SELECT u.id, u.username, u.tipo_usuario, u.estado, r.nombre AS rol
            FROM usuarios u
            JOIN roles r ON r.id = u.rol_id
            WHERE u.id = :id
        """),
        {"id": user_id},
    ).first()
    user = row_to_dict(row)
    if not user or user["estado"] != "activo":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario no autorizado")
    return user


def require_roles(*roles: str):
    def checker(user: dict = Depends(get_current_user)):
        if user["rol"] not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permisos insuficientes")
        return user
    return checker


def require_cliente(user: dict = Depends(get_current_user)):
    if user["tipo_usuario"] != "cliente":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Ruta exclusiva para clientes")
    return user


def require_personal(user: dict = Depends(get_current_user)):
    if user["tipo_usuario"] != "personal":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Ruta exclusiva para personal del banco")
    return user
