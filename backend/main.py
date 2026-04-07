import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

load_dotenv()
from utils import key_manager
from api.routes import router

# ── Logging ────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="[NUVOX] %(levelname)s %(asctime)s — %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("nuvox")

app = FastAPI(
    title="NUVOX API",
    description="AI-powered mock interview platform backend",
    version="1.0.0",
)

# CORS — allow all origins for deployment
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API routes first (must take precedence over static files)
app.include_router(router)

@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "version": "1.0.0", 
        "keys": key_manager.get_key_status()
    }

# ── Global error handler ──────────────────────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Unhandled error: {type(exc).__name__}: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal server error: {str(exc)}"},
    )

# ── Static files (serves frontend at /) ──────────────────────────
PUBLIC_DIR = os.path.join(os.path.dirname(__file__), "public")

if os.path.isdir(PUBLIC_DIR):
    app.mount("/", StaticFiles(directory=PUBLIC_DIR, html=True), name="frontend")

# ── Entry point for direct execution ─────────────────────────────
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    logger.info(f"Starting NUVOX on port {port}")
    uvicorn.run("main:app", host="0.0.0.0", port=port)
