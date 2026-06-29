from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.auth_deps import require_personal
from app.core.db_utils import audit
from app.schemas.base import PreEvaluacionIn, BuroIn
import json

router = APIRouter()

@router.post("/pre-evaluar")
def pre_evaluar(data: PreEvaluacionIn, user: dict = Depends(require_personal), db: Session = Depends(get_db)):
    ingresos = max(float(data.ingresos_estimados or 0), 0)
    gastos = max(float(data.gastos_estimados or 0), 0)
    capacidad = max(ingresos - gastos, 0)
    cuota_ref = (float(data.monto_solicitado or 0) / max(int(data.plazo_meses or 12), 1)) * 1.25
    ratio = cuota_ref / capacidad if capacidad > 0 else 99
    if ingresos <= 0:
        resultado, puntaje, motivo = "REVISAR", 50, "Ingresos no declarados. Requiere validación de campo."
    elif ratio <= 0.35:
        resultado, puntaje, motivo = "APTO", 85, "Capacidad de pago suficiente para el monto solicitado."
    elif ratio <= 0.55:
        resultado, puntaje, motivo = "REVISAR", 62, "El monto puede ser viable, pero requiere revisión del analista."
    else:
        resultado, puntaje, motivo = "NO_PROCEDE", 30, "La cuota estimada supera la capacidad de pago recomendable."
    calificacion = "Bajo riesgo" if resultado == "APTO" else "Riesgo medio" if resultado == "REVISAR" else "Alto riesgo"
    db.execute(text("""
        INSERT INTO evaluaciones_crediticias (solicitud_id, cliente_id, asesor_id, ingresos_estimados, gastos_estimados, capacidad_pago, ratio_endeudamiento, puntaje, calificacion, resultado, motivo)
        VALUES (CAST(:solicitud AS uuid), CAST(:cliente AS uuid), NULL, :ingresos, :gastos, :capacidad, :ratio, :puntaje, :calificacion, :resultado, :motivo)
    """), {"solicitud": data.solicitud_id, "cliente": data.cliente_id, "ingresos": ingresos, "gastos": gastos, "capacidad": capacidad, "ratio": ratio, "puntaje": puntaje, "calificacion": calificacion, "resultado": resultado, "motivo": motivo})
    audit(db, user, "PRE_EVALUAR", "evaluacion", "solicitudes_credito", data.solicitud_id, resultado)
    db.commit()
    return {"resultado": resultado, "puntaje": puntaje, "calificacion": calificacion, "motivo": motivo, "capacidad_pago": capacidad, "ratio_endeudamiento": round(ratio, 4)}

@router.post("/buro/consulta")
def consultar_buro(data: BuroIn, user: dict = Depends(require_personal), db: Session = Depends(get_db)):
    perfiles = {
        0: ("NORMAL", 1, 4500, 0, False),
        1: ("NORMAL", 2, 12000, 0, False),
        2: ("CPP", 2, 18000, 15, False),
        3: ("NORMAL", 0, 0, 0, False),
        4: ("DUDOSO", 3, 25000, 95, False),
        5: ("DEFICIENTE", 2, 16000, 45, False),
        6: ("NORMAL", 1, 6000, 0, False),
        7: ("PERDIDA", 4, 40000, 210, True),
        8: ("CPP", 1, 9000, 20, False),
        9: ("NORMAL", 2, 14000, 0, False),
    }
    ultimo = int(data.dni[-1]) if data.dni and data.dni[-1].isdigit() else 0
    cal, entidades, deuda, mora, lista = perfiles[ultimo]
    resultado = {"calificacion_sbs": cal, "entidades_con_deuda": entidades, "deuda_total": deuda, "dias_mayor_mora": mora, "en_lista_negra": lista}
    db.execute(text("""
        INSERT INTO consultas_buro (solicitud_id, cliente_id, dni_consultado, calificacion_sbs, entidades_con_deuda, deuda_total, dias_mayor_mora, en_lista_negra, resultado_json)
        VALUES (CAST(:sol AS uuid), CAST(:cli AS uuid), :dni, :cal, :entidades, :deuda, :mora, :lista, CAST(:json AS jsonb))
    """), {"sol": data.solicitud_id, "cli": data.cliente_id, "dni": data.dni, "cal": cal, "entidades": entidades, "deuda": deuda, "mora": mora, "lista": lista, "json": json.dumps(resultado)})
    audit(db, user, "CONSULTA_BURO", "evaluacion", "solicitudes_credito", data.solicitud_id, cal)
    db.commit()
    return resultado
