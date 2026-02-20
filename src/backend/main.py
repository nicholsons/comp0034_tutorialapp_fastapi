from __future__ import annotations

from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session

from backend.core.db import engine, init_db
from backend.routes import games_router


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
    with Session(engine) as session:
        init_db(session)
        yield


def create_app() -> FastAPI:
    """Create and configure the FastAPI application.

        Sets up the FastAPI application with CORS middleware and API routes.
        Configures allowed origins for cross-origin requests and registers
        the routers.

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

    # Register the routers
    app.include_router(games_router.router)

    return app

app = create_app()

if __name__ == "__main__":
    uvicorn.run(app)
