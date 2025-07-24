from datetime import datetime

from fastapi import FastAPI

from app.api.v1 import api_router

app = FastAPI(
    title="Microservice de Acompanhamento",
    description="API para acompanhamento de pedidos",
    version="1.0.0",
)

# Inclui o router principal da API v1 (mantém URLs limpas como /acompanhamento/*)
app.include_router(api_router)


@app.get("/")
def read_root():
    return {"message": "Microservice de Acompanhamento está funcionando!"}


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
