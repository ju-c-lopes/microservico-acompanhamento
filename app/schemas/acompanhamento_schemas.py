"""
Schemas para request/response da API de acompanhamento.
Define os contratos da API, validação de entrada/saída e documentação automática.
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from app.domain.order_state import StatusPagamento, StatusPedido

# === REQUEST SCHEMAS ===


class AtualizarStatusRequest(BaseModel):
    """Schema para atualização de status do pedido pela cozinha"""

    status: StatusPedido = Field(..., description="Novo status do pedido")


# === RESPONSE SCHEMAS ===


class ItemPedidoResponse(BaseModel):
    """Response para item do pedido"""

    id_produto: int = Field(..., description="ID do produto")
    quantidade: int = Field(..., description="Quantidade do item")


class AcompanhamentoResponse(BaseModel):
    """Response completo do acompanhamento"""

    id_pedido: int = Field(..., description="ID do pedido")
    cpf_cliente: str = Field(..., description="CPF do cliente")
    status: StatusPedido = Field(..., description="Status atual do pedido")
    status_pagamento: StatusPagamento = Field(..., description="Status do pagamento")
    itens: List[ItemPedidoResponse] = Field(..., description="Itens do pedido")
    valor_pago: Optional[float] = Field(None, description="Valor efetivamente pago")
    tempo_estimado: Optional[str] = Field(None, description="Tempo estimado (HH:MM:SS)")
    atualizado_em: datetime = Field(..., description="Data da última atualização")


class AcompanhamentoResumoResponse(BaseModel):
    """Response resumido para listagens (fila da cozinha)"""

    id_pedido: int = Field(..., description="ID do pedido")
    cpf_cliente: str = Field(..., description="CPF do cliente para identificação")
    status: StatusPedido = Field(..., description="Status atual do pedido")
    tempo_estimado: Optional[str] = Field(None, description="Tempo estimado (HH:MM:SS)")
    atualizado_em: datetime = Field(..., description="Data da última atualização")


class FilaPedidosResponse(BaseModel):
    """Response para fila de pedidos (visão da cozinha)"""

    pedidos: List[AcompanhamentoResumoResponse] = Field(
        ..., description="Lista de pedidos na fila"
    )
    total: int = Field(..., description="Total de pedidos na fila")


class SuccessResponse(BaseModel):
    """Response padrão para operações bem-sucedidas"""

    message: str = Field(..., description="Mensagem de sucesso")
    data: Optional[dict] = Field(None, description="Dados adicionais (opcional)")


class ErrorResponse(BaseModel):
    """Response padrão para erros"""

    detail: str = Field(..., description="Descrição do erro")
    error_code: Optional[str] = Field(None, description="Código do erro (opcional)")


class HealthResponse(BaseModel):
    """Response para health check"""

    status: str = Field(..., description="Status do serviço")
    service: str = Field(..., description="Nome do serviço")
    timestamp: datetime = Field(..., description="Timestamp da verificação")
    version: str = Field(..., description="Versão do serviço")
