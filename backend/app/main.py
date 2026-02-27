"""BloodTrace - Module SIH de gestion et tracabilite des dons de sang."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config.settings import settings
from app.config.database import engine, Base
from app.middleware.audit_middleware import AuditMiddleware
from app.api.v1 import auth, donors, donations, inventory, transfusions, dashboard, audit
from app.api.fhir import patient, specimen, service_request


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup and shutdown."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(
    title="BloodTrace",
    description="Module SIH de gestion et tracabilite des dons de sang",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Audit middleware
app.add_middleware(AuditMiddleware)

# API v1 routes
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(donors.router, prefix="/api/v1/donors", tags=["Donors"])
app.include_router(donations.router, prefix="/api/v1/donations", tags=["Donations"])
app.include_router(inventory.router, prefix="/api/v1/inventory", tags=["Inventory"])
app.include_router(transfusions.router, prefix="/api/v1/transfusions", tags=["Transfusions"])
app.include_router(dashboard.router, prefix="/api/v1/dashboard", tags=["Dashboard"])
app.include_router(audit.router, prefix="/api/v1/audit", tags=["Audit"])

# FHIR routes
app.include_router(patient.router, prefix="/api/fhir", tags=["FHIR - Patient"])
app.include_router(specimen.router, prefix="/api/fhir", tags=["FHIR - Specimen"])
app.include_router(service_request.router, prefix="/api/fhir", tags=["FHIR - ServiceRequest"])


@app.get("/api/health")
async def health_check():
    """Health check endpoint for SIH integration monitoring."""
    return {
        "status": "healthy",
        "service": "bloodtrace",
        "version": "1.0.0",
    }
