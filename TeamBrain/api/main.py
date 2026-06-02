from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .init_db import init_db
from .routers import notebooks, pages, blocks, ai, versions, search, tags, import_export, shares, sync, files


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title="MindVault API",
    description="Personal Knowledge Base System API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(notebooks.router)
app.include_router(pages.router)
app.include_router(blocks.router)
app.include_router(ai.router)
app.include_router(versions.router)
app.include_router(search.router)
app.include_router(tags.router)
app.include_router(import_export.router)
app.include_router(shares.router)
app.include_router(sync.router)
app.include_router(files.router)


@app.get("/api/health")
async def health_check():
    return {"status": "ok"}
