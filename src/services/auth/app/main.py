from fastapi import FastAPI
from .routers import auth

app = FastAPI(title="Auth Service")

app.include_router(auth.router)

@app.get("/health")
async def health():
    return {"message": "ok"}   