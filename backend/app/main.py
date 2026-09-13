import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from app.core.config import settings
from app.core.logging import setup_logging, logger
from app.database.base import Base
from app.database.session import engine, SessionLocal
from app.database.seed_data import seed_database
from app.ml.pipeline import get_or_load_model
from app.api.api import api_router
from app.api.routes.health import health_check

setup_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing database tables...")
    import time
    for attempt in range(1, 6):
        try:
            Base.metadata.create_all(bind=engine)
            logger.info("Database tables initialized successfully.")
            break
        except Exception as e:
            if attempt == 5:
                logger.error(f"Database initialization failed after 5 attempts: {e}")
                raise e
            logger.warning(f"Database connection attempt {attempt} failed ({e}). Retrying in 2s...")
            time.sleep(2)
    
    logger.info("Checking and seeding database with North East Region data...")
    db = SessionLocal()
    try:
        seed_database(db)
    except Exception as e:
        logger.error(f"Error during database seed: {e}")
    finally:
        db.close()

    logger.info("Pre-warming AI/ML Geotechnical Model Engine...")
    try:
        get_or_load_model()
        logger.info("AI/ML Model Engine successfully loaded and calibrated.")
    except Exception as e:
        logger.error(f"Error loading ML model: {e}")

    import asyncio
    from app.services.whatsapp import worker
    messaging_task = asyncio.create_task(worker())
    try:
        yield
    finally:
        messaging_task.cancel()
        try:
            await messaging_task
        except asyncio.CancelledError:
            pass

    logger.info("Shutting down Landslide Early Warning System...")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

@app.middleware("http")
async def protect_operations(request: Request, call_next):
    # Optional shared access key for small deployments; use an identity gateway for multi-user production.
    import secrets
    key=os.getenv('OPERATIONS_API_KEY','')
    needs_key=(request.url.path.startswith('/api/') and request.method in ['POST','PUT','PATCH','DELETE']) or request.url.path.startswith('/api/operations/reports')
    if key and needs_key and request.method!='OPTIONS':
        if not secrets.compare_digest(request.headers.get('X-Operations-Key',''),key):
            return JSONResponse(status_code=401,content={'detail':'Enter the deployment access key in Field Operations.'})
    return await call_next(request)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API routes
app.include_router(api_router, prefix=settings.API_V1_STR)

# Direct root /health endpoint
@app.get("/health", tags=["System"])
def root_health():
    db = SessionLocal()
    try:
        return health_check(db)
    finally:
        db.close()

# Root redirect or API info
@app.get("/api", tags=["System"])
def api_info():
    return {
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "docs": "/docs",
        "endpoints": {
            "locations": f"{settings.API_V1_STR}/locations",
            "predict": f"{settings.API_V1_STR}/predict",
            "alerts": f"{settings.API_V1_STR}/alerts",
            "environmental": f"{settings.API_V1_STR}/environmental/current",
            "analysis": f"{settings.API_V1_STR}/analysis/historical",
            "settings": f"{settings.API_V1_STR}/settings/thresholds"
        }
    }

# Production Static Files Serving (if built frontend exists)
frontend_dist = settings.FRONTEND_DIST_DIR
if os.path.exists(frontend_dist) and os.path.isdir(frontend_dist):
    assets_dir = os.path.join(frontend_dist, "assets")
    if os.path.exists(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_spa(full_path: str):
        # Don't hijack API or documentation routes
        if full_path.startswith("api") or full_path.startswith("docs") or full_path.startswith("redoc") or full_path == "health":
            return JSONResponse(status_code=404, content={"detail": "Not found"})
        
        file_path = os.path.realpath(os.path.join(frontend_dist, full_path))
        if os.path.commonpath([os.path.realpath(frontend_dist), file_path]) != os.path.realpath(frontend_dist):
            return JSONResponse(status_code=404, content={"detail":"Not found"})
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return FileResponse(file_path, headers={"Cache-Control":"no-cache"} if full_path in ["sw.js","outbox.js","index.html","manifest.webmanifest"] else None)
        
        index_file = os.path.join(frontend_dist, "index.html")
        if os.path.exists(index_file):
            return FileResponse(index_file)
        return JSONResponse(status_code=404, content={"detail": "Not found"})
else:
    @app.get("/", include_in_schema=False)
    async def root_fallback():
        return JSONResponse(
            content={
                "status": "online",
                "service": settings.PROJECT_NAME,
                "version": settings.VERSION,
                "docs": "/docs",
                "health": "/health",
                "api": settings.API_V1_STR
            }
        )
