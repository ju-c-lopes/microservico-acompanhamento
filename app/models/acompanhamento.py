from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class ItemPedido(BaseModel):
    id_produto: int
    quantidade: int


class EventoPedido(BaseModel):
    id_pedido: int
    cpf_cliente: str
    itens: List[ItemPedido]
    total_pedido: float
    tempo_estimado: Optional[str]
    status: str  # Ex: "criado", "preparando", "pronto", "entregue"
    criado_em: datetime


class EventoPagamento(BaseModel):
    id_pagamento: int
    id_pedido: int
    status: str  # Ex: "pago", "pendente", "falhou"
    criado_em: datetime


class Acompanhamento(BaseModel):
    id_pedido: int
    cpf_cliente: str
    status: str  # Ex: "aguardando_pagamento", "preparando", "pronto", "entregue"
    status_pagamento: str  # Ex: "pago", "pendente"
    itens: List[ItemPedido]
    tempo_estimado: Optional[str]
    atualizado_em: datetime
