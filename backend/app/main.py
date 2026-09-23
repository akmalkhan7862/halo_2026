import time
import uuid
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.database import Base, engine, SessionLocal
from app.api.routes import (
    auth,
    resumes,
    job_descriptions,
    analysis,
    interviews,
    reports,
    role_analysis
)
try:
    from scripts.seed_roles import seed_roles
    from scripts.import_esco import import_esco_skills
    from scripts.import_onet import import_onet_skills
    from scripts.seed_target_roles import seed_target_roles
except ImportError:
    seed_roles = None
    import_esco_skills = None
    import_onet_skills = None
    seed_target_roles = None
from app.utils.logger import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB tables on startup
    logger.info("Initializing database tables...")
    Base.metadata.create_all(bind=engine)
    
    # Auto-seed initial benchmark taxonomy if empty
    try:
        if import_esco_skills:
            import_esco_skills()
        if import_onet_skills:
            import_onet_skills()
        if seed_roles:
            seed_roles()
        if seed_target_roles:
            seed_target_roles()
        logger.info("Taxonomy and benchmark data initialized successfully.")
    except Exception as e:
        logger.warning(f"Note on taxonomy seed: {e}")

    yield
    logger.info("Application shutting down.")


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    request_id = str(uuid.uuid4())
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = f"{process_time:.4f}s"
    response.headers["X-Request-ID"] = request_id
    return response


# Include Routers
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(resumes.router, prefix=settings.API_V1_STR)
app.include_router(job_descriptions.router, prefix=settings.API_V1_STR)
app.include_router(analysis.router, prefix=settings.API_V1_STR)
app.include_router(interviews.router, prefix=settings.API_V1_STR)
app.include_router(reports.router, prefix=settings.API_V1_STR)
app.include_router(role_analysis.router, prefix=settings.API_V1_STR)


@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "project": settings.PROJECT_NAME,
        "environment": settings.ENVIRONMENT
    }


@app.get("/", tags=["Root"])
def root():
    return {
        "message": "Welcome to Resume Intelligence and Mock Interview Platform API",
        "docs": f"{settings.API_V1_STR}/docs"
    }
