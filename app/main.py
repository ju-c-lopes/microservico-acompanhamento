from datetime import datetime

from fastapi import FastAPI

from app.models.acompanhamento import Acompanhamento

app = FastAPI(
    title="Microservice de Acompanhamento",
    description="API para acompanhamento de pedidos",
    version="1.0.0",
)


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


@app.post("/acompanhamento", response_model=Acompanhamento)
def criar_acompanhamento(acompanhamento: Acompanhamento):
    """Criar um novo acompanhamento de pedido"""
    return acompanhamento


@app.get("/acompanhamento/{id_pedido}")
def obter_acompanhamento(id_pedido: int):
    """Obter acompanhamento de um pedido específico"""
    return {
        "id_pedido": id_pedido,
        "status": "em_preparo",
        "tempo_estimado": "20 minutos",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
