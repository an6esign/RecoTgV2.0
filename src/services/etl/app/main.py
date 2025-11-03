from fastapi import FastAPI
from app.routers import channels

app = FastAPI(title="RecoTg Data Service")
app.include_router(channels.router)

@app.get("/health")
def health(): return {"ok": True}