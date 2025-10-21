from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core.config import get_settings, ensure_data_dirs
from src.core.errors import register_exception_handlers
from src.api.routers import estimation, polygons, twins, analytics, generator

settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="APIs for vehicle range estimation, geospatial polygons, digital twins, analytics, and synthetic data generation.",
    openapi_tags=[
        {"name": "health", "description": "Service health and metadata"},
        {"name": "estimation", "description": "Vehicle range estimation"},
        {"name": "polygons", "description": "Geospatial polygon utilities"},
        {"name": "twins", "description": "Digital twin CRUD"},
        {"name": "analytics", "description": "Analytics and insights"},
        {"name": "generator", "description": "Synthetic telemetry generator"},
    ],
)

# CORS: allow all for now per instructions
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register standardized error handlers
register_exception_handlers(app)


@app.on_event("startup")
def on_startup() -> None:
    """Ensure required data directories exist at startup."""
    ensure_data_dirs()


# PUBLIC_INTERFACE
@app.get("/", tags=["health"], summary="Health Check", description="Simple health endpoint that returns service status.")
def health_check():
    """Return a basic health message."""
    return {"message": "Healthy", "app": settings.APP_NAME, "version": settings.VERSION}


# Include routers
app.include_router(estimation.router, prefix="/estimation", tags=["estimation"])
app.include_router(polygons.router, prefix="/polygons", tags=["polygons"])
app.include_router(twins.router, prefix="/twins", tags=["twins"])
app.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
app.include_router(generator.router, prefix="/generator", tags=["generator"])
