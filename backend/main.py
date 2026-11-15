from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.routes import affidavits, expenses, reconcile

app = FastAPI(
    title="Expense Reconciliation API",
    description="API for reconciling expected expenses against actual expenses from Google Sheets",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"https://.*\.up\.railway\.app|http://localhost:\d+",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    return {"status": "ok"}


app.include_router(reconcile.router)
app.include_router(expenses.router)
app.include_router(affidavits.router)


# NOTE: this file must stay directly under backend/ -- the path below is
# relative to it. The static mount at "/" is a catch-all, so it must be
# registered AFTER all routers.
frontend_dist = Path(__file__).parent.parent / "frontend" / "dist"
print(f"[startup] Looking for frontend at: {frontend_dist.resolve()}")
print(f"[startup] frontend/dist exists: {frontend_dist.is_dir()}")
if frontend_dist.is_dir():
    print(f"[startup] frontend/dist contents: {list(frontend_dist.iterdir())}")
    app.mount("/", StaticFiles(directory=str(frontend_dist), html=True), name="frontend")
else:
    parent = frontend_dist.parent
    print(f"[startup] frontend/ exists: {parent.is_dir()}")
    if parent.is_dir():
        print(f"[startup] frontend/ contents: {list(parent.iterdir())}")
