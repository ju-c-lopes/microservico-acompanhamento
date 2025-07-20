"""
Nova aplicação FastAPI com estrutura completa para o microserviço de acompanhamento.
Esta versão substituirá gradualmente o main.py atual, mantendo compatibilidade total.

Características:
- Estrutura de rotas /acompanhamento/...
- Exception handling robusto
- Middleware CORS configurado
- Health checks para monitoramento
- Documentação automática (Swagger)
"""

from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.v1.acompanhamento import router as acompanhamento_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gerencia o ciclo de vida da aplicação (startup e shutdown).
    Substitui os decoradores @app.on_event que foram deprecated.
    """
    # Startup
    print("🚀 Microserviço de Acompanhamento iniciado")
    print("📋 Endpoints disponíveis:")
    print("   - GET  /acompanhamento/health")
    print("   - GET  /acompanhamento/{id_pedido}")
    print("   - PUT  /acompanhamento/{id_pedido}/status")
    print("   - GET  /acompanhamento/fila/pedidos")
    print("   - GET  /acompanhamento/cliente/{cpf}")
    print("📖 Documentação: http://localhost:8000/docs")

    yield  # Aplicação roda aqui

    # Shutdown
    print("🛑 Microserviço de Acompanhamento finalizando...")


# Criar aplicação FastAPI com lifespan
app = FastAPI(
    title="Microserviço de Acompanhamento",
    description="""
    API para acompanhamento de pedidos da lanchonete.
    
    Este microserviço é responsável por:
    - Acompanhar o progresso dos pedidos
    - Gerenciar status de pedidos (Recebido → Em Preparação → Pronto → Finalizado)
    - Fornecer fila de pedidos para a cozinha
    - Manter histórico de pedidos por cliente
    
    Comunicação via eventos Kafka com outros microserviços:
    - Microserviço de Pedidos (recebe eventos de criação)
    - Microserviço de Pagamento (recebe eventos de pagamento)
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# Middleware CORS para permitir acesso de diferentes origens
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especificar origens específicas
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


# Exception handlers para tratamento centralizado de erros
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Handler para erros de validação de entrada (dados inválidos).
    Retorna resposta padronizada com detalhes do erro.
    """
    return JSONResponse(
        status_code=422,
        content={
            "detail": "Dados de entrada inválidos",
            "errors": exc.errors(),
            "body": exc.body,
        },
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """
    Handler para exceções HTTP gerais.
    Mantém o código de status original e formata a resposta.
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "status_code": exc.status_code},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """
    Handler para exceções não tratadas.
    Evita que erros internos vazem informações sensíveis.
    """
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Erro interno do servidor",
            "error_type": type(exc).__name__,
        },
    )


# Incluir as rotas do acompanhamento
app.include_router(acompanhamento_router)


# Rota raiz do microserviço
@app.get("/")
async def root():
    """
    Endpoint raiz do microserviço.
    Fornece informações básicas sobre o serviço e links úteis.
    """
    return {
        "message": "Microserviço de Acompanhamento",
        "description": "API para acompanhamento de pedidos da lanchonete",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc",
            "openapi": "/openapi.json",
        },
        "endpoints": {
            "health": "/acompanhamento/health",
            "buscar_pedido": "/acompanhamento/{id_pedido}",
            "atualizar_status": "/acompanhamento/{id_pedido}/status",
            "fila_cozinha": "/acompanhamento/fila/pedidos",
            "historico_cliente": "/acompanhamento/cliente/{cpf}",
        },
    }


# Health check global (além do específico do acompanhamento)
@app.get("/health")
async def health_check_global():
    """
    Health check global do microserviço.
    Usado por load balancers e ferramentas de monitoramento.
    """
    return {
        "status": "healthy",
        "service": "microservico-acompanhamento",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "components": {
            "database": "healthy",  # Aqui poderia ter verificação real do DB
            "api": "healthy",
        },
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True,  # Apenas para desenvolvimento
        log_level="info",
    )
