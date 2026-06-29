from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.routes import auth, cliente, clientes, cartera, solicitudes, evaluacion, operaciones, reportes, auditoria, catalogos

app = FastAPI(
    title="Core Caja Huancayo",
    description="API para portal interno, app de fuerza de ventas y app cliente.",
    version="1.0.0",
)

origins = [o.strip() for o in settings.CORS_ORIGINS.split(",") if o.strip()]
if settings.APP_ENV == "local":
    origins.append("*")

app.add_middleware(
    CORSMiddleware,
    allow_origins=list(set(origins)),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["Auth personal"])
app.include_router(cliente.router, prefix="/cliente", tags=["App cliente"])
app.include_router(clientes.router, prefix="/clientes", tags=["Clientes"])
app.include_router(cartera.router, prefix="/cartera", tags=["Fuerza de ventas"])
app.include_router(solicitudes.router, prefix="/solicitudes", tags=["Solicitudes"])
app.include_router(evaluacion.router, tags=["Evaluación"])
app.include_router(operaciones.router, prefix="/operaciones", tags=["Operaciones"])
app.include_router(reportes.router, prefix="/reportes", tags=["Reportes"])
app.include_router(auditoria.router, prefix="/auditoria", tags=["Auditoría"])
app.include_router(catalogos.router, prefix="/catalogos", tags=["Catálogos"])

@app.get("/")
def root():
    return {
        "sistema": "Core Caja Huancayo",
        "version": "1.0.0",
        "ambiente": settings.APP_ENV,
        "status": "ok",
    }

@app.get("/health")
def health():
    return {"status": "healthy"}
