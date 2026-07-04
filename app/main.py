from contextlib import asynccontextmanager
from pathlib import Path

import httpx
import structlog
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.api.endpoints import admin, auth, favorites, search
from app.core.database import Base, engine
from app.core.exceptions import CityNotFoundError, NomadStackError, ServiceUnavailableError
from app.services.cache import cache

BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.dev.ConsoleRenderer(),
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)
logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting NomadStack API")
    Base.metadata.create_all(bind=engine)
    await cache.init()
    async with httpx.AsyncClient() as client:
        app.state.http_client = client
        yield
    await cache.close()
    logger.info("NomadStack API stopped")


app = FastAPI(
    title="NomadStack API",
    description="A Travel Intelligence API aggregating multiple data sources — "
    "weather, exchange rates, attractions, and country data into a unified travel score.",
    version="2.0.0",
    lifespan=lifespan,
    contact={"name": "NomadStack Team", "url": "https://github.com/neoastra303/NomadStack-API"},
    license_info={"name": "MIT", "url": "https://opensource.org/licenses/MIT"},
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"],
)


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response


@app.exception_handler(NomadStackError)
async def nomadstack_exception_handler(request: Request, exc: NomadStackError):
    if isinstance(exc, CityNotFoundError):
        return JSONResponse(status_code=404, content={"error": str(exc)})
    if isinstance(exc, ServiceUnavailableError):
        return JSONResponse(status_code=502, content={"error": str(exc)})
    return JSONResponse(status_code=500, content={"error": str(exc)})


app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
app.include_router(admin.router, prefix="/api/v1", tags=["Admin"])
app.include_router(search.router, prefix="/api/v1", tags=["Travel Intelligence"])
app.include_router(auth.router, prefix="/api/v1", tags=["Auth"])
app.include_router(favorites.router, prefix="/api/v1", tags=["User"])


@app.get("/", summary="Serve the SPA", include_in_schema=False)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/health", summary="Health check", tags=["System"])
async def health_check():
    return {"status": "healthy", "version": "2.0.0"}


@app.get("/robots.txt", summary="Robots.txt", include_in_schema=False)
async def robots():
    return PlainTextResponse("User-agent: *\nAllow: /\n")
