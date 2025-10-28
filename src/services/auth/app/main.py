from fastapi import FastAPI
from .routers import auth as auth_router

app = FastAPI(title="Auth Service")

app.include_router(auth_router.router)

@app.get("/health")
async def health():
    return {"message": "ok"}   