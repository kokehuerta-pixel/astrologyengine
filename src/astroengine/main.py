"""AstroEngine - Motor de calculo astrologico."""

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from contextlib import asynccontextmanager
from pathlib import Path
from .database import init_db
from .api.users import router as users_router
from .api.natal import router as natal_router
from .api.transit import router as transit_router
from .api.reading import router as reading_router

STATIC_DIR = Path(__file__).resolve().parent.parent.parent / "static"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Inicializa la base de datos al arrancar."""
    await init_db()
    yield


app = FastAPI(
    title="AstroEngine",
    description="Motor de calculo astrologico con Stellium + Gemini API",
    version="0.1.0",
    lifespan=lifespan,
)

# API routers
app.include_router(users_router)
app.include_router(natal_router)
app.include_router(transit_router)
app.include_router(reading_router)

# Static files
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok", "engine": "stellium"}


@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the PWA."""
    return FileResponse(str(STATIC_DIR / "index.html"), media_type="text/html")
