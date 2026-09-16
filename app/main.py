from fastapi import FastAPI

app = FastAPI(
    title="Lumen Property Registry API",
    version="0.1.0",
)


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "lumen-property-registry-backend",
    }