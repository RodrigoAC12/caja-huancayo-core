from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import verify_password, create_access_token
from app.core.auth_deps import require_cliente
from app.core.db_utils import row_to_dict, rows_to_dicts, audit
from app.schemas.base import LoginClienteIn, TokenOut, OperacionIn, ClienteSolicitudIn
import uuid

router = APIRouter()


def _cliente_actual(db: Session, user: dict) -> dict:
    row = db.execute(text("SELECT * FROM clientes WHERE usuario_id = :uid"), {"uid": user["id"]}).first()
    cliente = row_to_dict(row)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return cliente

@router.post("/login", response_model=TokenOut)
def login_cliente(data: LoginClienteIn, db: Session = Depends(get_db)):
    row = db.execute(
        text("SELECT * FROM usuarios WHERE username = :username AND tipo_usuario = 'cliente'"),
        {"username": data.numero_documento},
    ).first()
    user_db = row_to_dict(row)
    if not user_db or user_db["estado"] != "activo" or not verify_password(data.password, user_db["password_hash"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales inválidas")

    cliente = db.execute(text("SELECT * FROM clientes WHERE usuario_id = :uid"), {"uid": user_db["id"]}).first()
    cliente_data = row_to_dict(cliente)
    db.execute(text("UPDATE usuarios SET ultimo_login = now(), intentos_fallidos = 0 WHERE id = :id"), {"id": user_db["id"]})
    audit(db, {"id": user_db["id"]}, "LOGIN", "cliente", "usuarios", user_db["id"], "Ingreso a app cliente")
    db.commit()
    token = create_access_token({"sub": user_db["id"], "rol": "cliente", "tipo_usuario": "cliente"})
    return {"access_token": token, "token_type": "bearer", "user": {"usuario": user_db["username"], "rol": "cliente", "cliente": cliente_data}}

@router.get("/perfil")
def perfil(user: dict = Depends(require_cliente), db: Session = Depends(get_db)):
    return _cliente_actual(db, user)

@router.get("/cuentas")
def cuentas(user: dict = Depends(require_cliente), db: Session = Depends(get_db)):
    cliente = _cliente_actual(db, user)
    rows = db.execute(text("SELECT * FROM cuentas_ahorro WHERE cliente_id = :cid ORDER BY created_at"), {"cid": cliente["id"]}).all()
    return rows_to_dicts(rows)

@router.get("/creditos")
def creditos(user: dict = Depends(require_cliente), db: Session = Depends(get_db)):
    cliente = _cliente_actual(db, user)
    rows = db.execute(text("SELECT * FROM creditos WHERE cliente_id = :cid ORDER BY created_at DESC"), {"cid": cliente["id"]}).all()
    return rows_to_dicts(rows)

@router.get("/creditos/{numero_credito}/cronograma")
def cronograma(numero_credito: str, user: dict = Depends(require_cliente), db: Session = Depends(get_db)):
    cliente = _cliente_actual(db, user)
    credito = row_to_dict(db.execute(text("SELECT id FROM creditos WHERE numero_credito = :n AND cliente_id = :cid"), {"n": numero_credito, "cid": cliente["id"]}).first())
    if not credito:
        raise HTTPException(status_code=404, detail="Crédito no encontrado")
    rows = db.execute(text("SELECT * FROM cronograma_credito WHERE credito_id = :id ORDER BY nro_cuota"), {"id": credito["id"]}).all()
    return rows_to_dicts(rows)

@router.get("/movimientos")
def movimientos(limit: int = 20, user: dict = Depends(require_cliente), db: Session = Depends(get_db)):
    cliente = _cliente_actual(db, user)
    rows = db.execute(text("""
        SELECT m.*, c.numero_cuenta
        FROM movimientos_cuenta m
        LEFT JOIN cuentas_ahorro c ON c.id = m.cuenta_id
        WHERE m.cliente_id = :cid
        ORDER BY m.fecha_operacion DESC
        LIMIT :limit
    """), {"cid": cliente["id"], "limit": limit}).all()
    return rows_to_dicts(rows)

@router.get("/tarjetas")
def tarjetas(user: dict = Depends(require_cliente), db: Session = Depends(get_db)):
    cliente = _cliente_actual(db, user)
    rows = db.execute(text("SELECT * FROM tarjetas WHERE cliente_id = :cid ORDER BY created_at"), {"cid": cliente["id"]}).all()
    return rows_to_dicts(rows)

@router.get("/notificaciones")
def notificaciones(user: dict = Depends(require_cliente), db: Session = Depends(get_db)):
    cliente = _cliente_actual(db, user)
    rows = db.execute(text("SELECT * FROM notificaciones WHERE cliente_id = :cid OR usuario_id = :uid ORDER BY created_at DESC LIMIT 50"), {"cid": cliente["id"], "uid": user["id"]}).all()
    return rows_to_dicts(rows)

@router.post("/operaciones")
def crear_operacion(data: OperacionIn, user: dict = Depends(require_cliente), db: Session = Depends(get_db)):
    cliente = _cliente_actual(db, user)

    cuenta = row_to_dict(db.execute(text("""
        SELECT *
        FROM cuentas_ahorro
        WHERE id = CAST(:id AS uuid)
          AND cliente_id = CAST(:cid AS uuid)
          AND estado = 'activa'
        FOR UPDATE
    """), {"id": data.cuenta_origen_id, "cid": cliente["id"]}).first())

    if not cuenta:
        raise HTTPException(status_code=404, detail="Cuenta origen no encontrada o no activa")

    tipo = data.tipo_operacion.upper().strip()
    tipos_permitidos = {
        "TRANSFERENCIA_PROPIA",
        "TRANSFERENCIA_TERCEROS",
        "PAGO_CREDITO",
        "PAGO_SERVICIO",
        "PAGO_QR",
        "PAGO_TELEFONO",
        "RECARGA",
    }
    if tipo not in tipos_permitidos:
        raise HTTPException(status_code=422, detail=f"Tipo de operación no permitido: {tipo}")

    monto = float(data.monto)
    saldo_actual = float(cuenta["saldo_disponible"] or 0)

    if monto <= 0:
        raise HTTPException(status_code=422, detail="El monto debe ser mayor a cero")
    if saldo_actual < monto:
        raise HTTPException(status_code=400, detail="Saldo insuficiente")

    descripcion = (data.descripcion or tipo).strip()
    op_id = str(uuid.uuid4())
    codigo = "OP-" + op_id.replace("-", "")[:10].upper()
    comprobante = "CP-" + op_id.replace("-", "")[:10].upper()
    nuevo_saldo = round(saldo_actual - monto, 2)

    destino_uuid = data.cuenta_destino_id if data.cuenta_destino_id else None

    db.execute(text("""
        UPDATE cuentas_ahorro
        SET saldo_disponible = :saldo,
            saldo_contable = :saldo,
            updated_at = now()
        WHERE id = CAST(:id AS uuid)
    """), {"saldo": nuevo_saldo, "id": cuenta["id"]})

    db.execute(text("""
        INSERT INTO operaciones (
            id, cliente_id, cuenta_origen_id, cuenta_destino_id,
            tipo_operacion, monto, moneda, estado, canal,
            codigo_operacion, descripcion
        )
        VALUES (
            CAST(:id AS uuid), CAST(:cliente AS uuid), CAST(:origen AS uuid), CAST(:destino AS uuid),
            :tipo, :monto, :moneda, 'procesada', 'APP_CLIENTE',
            :codigo, :descripcion
        )
    """), {
        "id": op_id,
        "cliente": cliente["id"],
        "origen": cuenta["id"],
        "destino": destino_uuid,
        "tipo": tipo,
        "monto": monto,
        "moneda": data.moneda or "PEN",
        "codigo": codigo,
        "descripcion": descripcion,
    })

    db.execute(text("""
        INSERT INTO movimientos_cuenta (
            cuenta_id, cliente_id, tipo_movimiento, concepto,
            canal, monto, moneda, saldo_resultante
        )
        VALUES (
            CAST(:cuenta AS uuid), CAST(:cliente AS uuid), :tipo, :concepto,
            'APP_CLIENTE', :monto, :moneda, :saldo
        )
    """), {
        "cuenta": cuenta["id"],
        "cliente": cliente["id"],
        "tipo": tipo,
        "concepto": descripcion,
        "monto": -monto,
        "moneda": data.moneda or "PEN",
        "saldo": nuevo_saldo,
    })

    db.execute(text("""
        INSERT INTO comprobantes (operacion_id, numero_comprobante, cliente_id, monto, descripcion)
        VALUES (CAST(:op AS uuid), :numero, CAST(:cliente AS uuid), :monto, :descripcion)
    """), {
        "op": op_id,
        "numero": comprobante,
        "cliente": cliente["id"],
        "monto": monto,
        "descripcion": descripcion,
    })

    db.execute(text("""
        INSERT INTO notificaciones (usuario_id, cliente_id, titulo, mensaje, tipo, canal)
        VALUES (CAST(:usuario AS uuid), CAST(:cliente AS uuid), 'Operación procesada', :mensaje, 'operacion', 'APP_CLIENTE')
    """), {
        "usuario": user["id"],
        "cliente": cliente["id"],
        "mensaje": f"Se procesó {tipo.replace('_', ' ').title()} por S/ {monto:.2f}. Código {codigo}.",
    })

    audit(db, user, "CREAR_OPERACION", "cliente", "operaciones", op_id, f"{tipo} {codigo}")
    db.commit()

    return {
        "id": op_id,
        "codigo_operacion": codigo,
        "numero_comprobante": comprobante,
        "estado": "procesada",
        "saldo_resultante": nuevo_saldo,
        "monto": monto,
        "moneda": data.moneda or "PEN",
        "descripcion": descripcion,
        "tipo_operacion": tipo,
        "cuenta_origen_id": str(cuenta["id"]),
    }

@router.get("/solicitudes")
def mis_solicitudes(user: dict = Depends(require_cliente), db: Session = Depends(get_db)):
    cliente = _cliente_actual(db, user)
    rows = db.execute(text("SELECT * FROM solicitudes_credito WHERE cliente_id = :cid ORDER BY created_at DESC"), {"cid": cliente["id"]}).all()
    return rows_to_dicts(rows)

@router.post("/solicitudes")
def crear_solicitud_cliente(data: ClienteSolicitudIn, user: dict = Depends(require_cliente), db: Session = Depends(get_db)):
    cliente = _cliente_actual(db, user)
    sol_id = str(uuid.uuid4())
    expediente = "EXP-CLI-" + sol_id.replace("-", "")[:8].upper()
    db.execute(text("""
        INSERT INTO solicitudes_credito (id, cliente_id, canal, numero_expediente, monto_solicitado, plazo_meses, destino_credito, cuota_estimada, tea_referencial, estado)
        VALUES (:id, :cliente, 'cliente', :exp, :monto, :plazo, :destino, :cuota, :tea, 'enviado')
    """), {"id": sol_id, "cliente": cliente["id"], "exp": expediente, "monto": data.monto_solicitado, "plazo": data.plazo_meses, "destino": data.destino_credito, "cuota": data.cuota_estimada, "tea": data.tea_referencial})
    db.execute(text("INSERT INTO solicitud_estado_historial (solicitud_id, estado_nuevo, usuario_id, comentario) VALUES (:sol, 'enviado', :user, 'Solicitud creada desde app cliente')"), {"sol": sol_id, "user": user["id"]})
    db.execute(text("INSERT INTO notificaciones (usuario_id, cliente_id, titulo, mensaje, tipo) VALUES (:user, :cliente, 'Solicitud recibida', :msg, 'solicitud')"), {"user": user["id"], "cliente": cliente["id"], "msg": f"Tu solicitud {expediente} fue registrada correctamente."})
    audit(db, user, "CREAR_SOLICITUD", "cliente", "solicitudes_credito", sol_id, expediente)
    db.commit()
    return {"id": sol_id, "numero_expediente": expediente, "estado": "enviado"}
