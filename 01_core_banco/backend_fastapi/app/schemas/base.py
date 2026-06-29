from pydantic import BaseModel, Field
from typing import Optional

class LoginPersonalIn(BaseModel):
    username: Optional[str] = None
    codigo_empleado: Optional[str] = None
    password: str

class LoginClienteIn(BaseModel):
    numero_documento: str
    password: str

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict

class VisitaIn(BaseModel):
    resultado: str
    observacion: str = ""
    tipo_visita: Optional[str] = "campo"
    lat: Optional[float] = None
    lng: Optional[float] = None
    precision_gps: Optional[float] = None

class SolicitudIn(BaseModel):
    cliente_id: Optional[str] = None
    numero_documento: Optional[str] = None
    nombres: str = ""
    apellidos: str = ""
    telefono: Optional[str] = None
    monto_solicitado: float = Field(gt=0)
    plazo_meses: int = Field(gt=0)
    destino_credito: Optional[str] = None
    cuota_estimada: Optional[float] = None
    tea_referencial: Optional[float] = None
    canal: str = "asesor"
    lat_captura: Optional[float] = None
    lng_captura: Optional[float] = None

class EstadoSolicitudIn(BaseModel):
    estado: str
    monto_aprobado: Optional[float] = None
    comentario: str = ""
    motivo_rechazo: Optional[str] = None

class PreEvaluacionIn(BaseModel):
    cliente_id: Optional[str] = None
    solicitud_id: Optional[str] = None
    numero_documento: Optional[str] = None
    ingresos_estimados: float = 0
    gastos_estimados: float = 0
    monto_solicitado: float = 0
    plazo_meses: int = 12

class BuroIn(BaseModel):
    dni: str
    cliente_id: Optional[str] = None
    solicitud_id: Optional[str] = None

class OperacionIn(BaseModel):
    cuenta_origen_id: str
    cuenta_destino_id: Optional[str] = None
    tipo_operacion: str
    monto: float = Field(gt=0)
    moneda: str = "PEN"
    descripcion: Optional[str] = None

class ClienteSolicitudIn(BaseModel):
    monto_solicitado: float = Field(gt=0)
    plazo_meses: int = Field(gt=0)
    destino_credito: Optional[str] = None
    cuota_estimada: Optional[float] = None
    tea_referencial: Optional[float] = None
