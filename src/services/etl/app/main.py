from fastapi import FastAPI
from app.routers import channels
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="RecoTg Data Service")
app.include_router(channels.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # можно заменить ["http://localhost:8002"] если хочешь безопаснее
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health(): return {"ok": True}