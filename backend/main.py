import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.database import Base, engine
from backend.models import user, test, session, violation  # noqa: F401 (register models)
from backend.routers import auth, tests, sessions, violations, reports, ws

Base.metadata.create_all(bind=engine)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SNAPSHOTS_DIR = os.environ.get("SNAPSHOTS_DIR", os.path.join(BASE_DIR, "snapshots"))
os.makedirs(SNAPSHOTS_DIR, exist_ok=True)

app = FastAPI(title="SmartProctor API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/snapshots", StaticFiles(directory=SNAPSHOTS_DIR), name="snapshots")

app.include_router(auth.router)
app.include_router(tests.router)
app.include_router(sessions.router)
app.include_router(violations.router)
app.include_router(reports.router)
app.include_router(ws.router)


@app.get("/health")
def health():
    return {"status": "ok"}


FRONTEND_DIST = os.path.join(BASE_DIR, "frontend", "dist")
if os.path.isdir(FRONTEND_DIST):
    app.mount("/", StaticFiles(directory=FRONTEND_DIST, html=True), name="frontend")
