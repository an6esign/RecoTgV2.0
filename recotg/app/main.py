from fastapi import FastAPI

app = FastAPI(title="RecoTg V2.0")


@app.get("/health")
async def health():
    return {"message": "ok"}        