from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, field_validator

from app.domain.order_state import StatusPagamento, StatusPedido


class ItemPedido(BaseModel):
    id_produto: int
    quantidade: int

    @field_validator("id_produto")
    @classmethod
    def validate_id_produto_positive(cls, v):
        if v <= 0:
            raise ValueError("Product ID must be positive")
        return v

    @field_validator("quantidade")
    @classmethod
    def validate_quantidade_positive(cls, v):
        if v <= 0:
            raise ValueError("Quantity must be positive")
        return v


class EventoPedido(BaseModel):
    id_pedido: int
    cpf_cliente: str
    itens: List[ItemPedido]
    total_pedido: float
    tempo_estimado: Optional[str] = None
    status: str  # Ex: "criado", "preparando", "pronto", "entregue" - Status do microserviço de pedidos
    criado_em: datetime

    @field_validator("itens")
    @classmethod
    def validate_itens_not_empty(cls, v):
        if not v or len(v) == 0:
            raise ValueError("Order must have at least one item")
        return v


class EventoPagamento(BaseModel):
    id_pagamento: int
    id_pedido: int
    status: StatusPagamento  # Usando enum para validação automática
    criado_em: datetime


class Acompanhamento(BaseModel):
    id_pedido: int
    cpf_cliente: str
    status: StatusPedido  # Usando enum para validação automática
    status_pagamento: StatusPagamento  # Usando enum para validação automática
    itens: List[ItemPedido]
    valor_pago: Optional[float] = None  # Valor efetivamente pago
    tempo_estimado: Optional[str]
    atualizado_em: datetime

    @field_validator("itens")
    @classmethod
    def validate_itens_not_empty(cls, v):
        if not v or len(v) == 0:
            raise ValueError("Order must have at least one item")
        return v
