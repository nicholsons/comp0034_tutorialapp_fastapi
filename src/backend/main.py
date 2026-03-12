from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from pathlib import Path

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlmodel import Session

from backend.core.db import get_engine, init_db
from backend.routes import auth_router, games_router, quiz_router

# Create logs directory if it doesn't exist
LOGS_DIR = Path(__file__).resolve().parent.parent.parent / "logs"
LOGS_DIR.mkdir(exist_ok=True)
LOG_FILE = LOGS_DIR / "paralympicsapp.log"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


# Async lifespan even though the routes are sync—this is fine.
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan events.

    Handles startup and shutdown events for the FastAPI application.
    On startup, initializes the database by creating tables if they don't exist.

    Args:
        app: The FastAPI application instance.

    Yields:
        None:
    """
    # Startup: creates the database
    engine = get_engine()
    with Session(engine) as session:
        logger.info("Initializing database...")
        init_db(session)
    logger.info("Application startup complete")

    yield

    # Shutdown
    logger.info("Application shutting down...")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application.

    Sets up the FastAPI application with CORS middleware and API routes.

    Returns:
        FastAPI:  FastAPI application instance.
    """
    app = FastAPI(
        title="Paralympics API",
        lifespan=lifespan,
        docs_url="/"
    )

    # Allow requests from front end apps
    origins = [
        "http://localhost",
        "http://127.0.0.1",
        "http://localhost:8050",  # dash default
        "http://localhost:5000",  # flask default
        "http://localhost:8501",  # streamlit default
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        # Log the error details
        logger.error(f"Server error occurred: {exc}")
        # Return a user-friendly error response
        return JSONResponse(
            status_code=500,
            content={"message": "Internal server error. Please try again later."},
        )

    # Register the routers
    app.include_router(games_router.router)
    app.include_router(quiz_router.router)
    app.include_router(auth_router.router)

    return app


app = create_app()

if __name__ == "__main__":
    uvicorn.run(app)
