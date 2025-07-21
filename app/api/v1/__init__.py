"""
API v1 Router Configuration.
Centraliza todos os endpoints da versão 1 da API seguindo Clean Architecture.
"""

from fastapi import APIRouter

from app.api.v1.acompanhamento import router as acompanhamento_router

# Router principal da API v1
api_router = APIRouter()

# Inclui todos os routers dos módulos
api_router.include_router(acompanhamento_router)

# Exporta o router principal para uso no main.py
__all__ = ["api_router"]
