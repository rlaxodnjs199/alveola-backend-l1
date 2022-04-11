from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.gapi import gapi_router
from app.api.v1.ctscan import ctscan_router
from app.core.db.pgsql.session import engine
from app.core.db.pgsql import Base
from app.models import *


def init_cors(app: FastAPI) -> None:
    ORIGINS = [
        "http://localhost",
        "http://localhost:3000",
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


def init_routers(app: FastAPI) -> None:
    app.include_router(gapi_router)
    app.include_router(ctscan_router)


def create_app() -> FastAPI:
    app = FastAPI(
        title="Alveola",
        description="Alveola FastAPI",
        version="1.0.0",
    )
    init_routers(app)
    init_cors(app)

    return app


app = create_app()


@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
