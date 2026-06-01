import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.database import init_db
from app.routes import auth, subscription, sessions, upload, download, health, templates


@asynccontextmanager
async def lifespan(app: FastAPI):
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    os.makedirs(settings.OUTPUTS_DIR, exist_ok=True)
    await init_db()
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

api_prefix = settings.API_V1_PREFIX
app.include_router(health.router, prefix=api_prefix, tags=["Health"])
app.include_router(auth.router, prefix=api_prefix, tags=["Auth"])
app.include_router(subscription.router, prefix=api_prefix, tags=["Subscription"])
app.include_router(sessions.router, prefix=api_prefix, tags=["Sessions"])
app.include_router(upload.router, prefix=api_prefix, tags=["Upload"])
app.include_router(download.router, prefix=api_prefix, tags=["Download"])
app.include_router(templates.router, prefix=api_prefix, tags=["Templates"])
