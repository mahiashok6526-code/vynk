import os
import sys
import logging

logger = logging.getLogger("vynk")

# Ensure backend and root directories are present in sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, ".."))
backend_dir = os.path.join(root_dir, "backend")

for p in [backend_dir, root_dir, current_dir]:
    if os.path.exists(p) and p not in sys.path:
        sys.path.insert(0, p)

try:
    from app.main import app
except ImportError:
    try:
        from backend.app.main import app
    except Exception as exc:
        logger.exception("Failed to import Vynk FastAPI app in serverless environment")
        from fastapi import FastAPI
        from fastapi.responses import JSONResponse

        app = FastAPI(title="Vynk API Error Handler")

        @app.api_route("/{full_path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"])
        async def fallback_handler(full_path: str):
            return JSONResponse(
                status_code=500,
                content={
                    "error": "Serverless application initialization failed",
                    "detail": str(exc),
                    "backend_dir": backend_dir,
                    "sys_path": sys.path,
                }
            )
