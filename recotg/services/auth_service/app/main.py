from fastapi import FastAPI

app = FastAPI(title="Auth")


@app.get("/health")
async def health():
    return {"message": "ok"}   