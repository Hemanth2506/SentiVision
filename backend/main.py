import os
import sys
import logging

# Add project root and ml directory to sys.path to allow imports from ml/
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "ml")))

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from routes import auth, analyze, stats
from dotenv import load_dotenv
from ml.predict import load_model

# Load env vars
load_dotenv()

# Configure logging with timestamps
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("sentivision-api")

# Create database tables (SQLite auto-creation)
try:
    logger.info("Initializing database tables...")
    env_mode = os.getenv("ENV", "development")
    if env_mode == "development":
        logger.info("Development mode detected. Resetting database (drop_all)...")
        Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables initialized successfully.")
except Exception as e:
    logger.error(f"Error creating database tables: {e}")

# Initialize FastAPI application
app = FastAPI(
    title="SentiVision AI API",
    description="Backend API for SentiVision AI — Sentiment Analysis SaaS Platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration
# If credentials=True, allow_origins cannot be ["*"]
cors_origins_env = os.getenv("CORS_ORIGINS", "")
if cors_origins_env:
    origins = [origin.strip() for origin in cors_origins_env.split(",") if origin.strip()]
else:
    origins = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(analyze.router)
app.include_router(stats.router)

from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.error(f"Validation error for {request.method} {request.url.path}: {exc.errors()}")
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()}
    )

# Request logging middleware
import time

@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Received request: {request.method} {request.url.path}")
    start_time = time.time()
    response = await call_next(request)
    process_time = (time.time() - start_time) * 1000
    logger.info(f"Response status: {response.status_code} | Duration: {process_time:.2f}ms")
    response.headers["X-Process-Time"] = f"{process_time:.2f}ms"
    return response

@app.on_event("startup")
def startup_event():
    """
    Load ML models on startup so they are cached and ready.
    """
    logger.info("Loading ML Model and Vectorizer...")
    try:
        load_model()
        logger.info("ML Model and Vectorizer loaded successfully.")
    except Exception as e:
        logger.error(f"Failed to load ML model on startup: {e}")
        logger.warning("Please ensure you have run the training pipeline first: python ml/train.py")

@app.get("/")
def read_root():
    return {
        "app": "SentiVision AI API",
        "status": "online",
        "tagline": "Understand Every Word. Instantly."
    }
