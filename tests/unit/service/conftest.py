"""
Fixtures compartilhadas para testes do AcompanhamentoService
"""

from datetime import datetime
from unittest.mock import AsyncMock

import pytest

from app.domain.acompanhamento_service import AcompanhamentoService
from app.domain.order_state import StatusPagamento, StatusPedido
from app.models.acompanhamento import (Acompanhamento, EventoPagamento,
                                       EventoPedido, ItemPedido)


@pytest.fixture
def mock_repository():
    """Repository mockado para testes do service"""
    return AsyncMock()


@pytest.fixture
def acompanhamento_service(mock_repository):
    """Service configurado com repository mockado"""
    return AcompanhamentoService(mock_repository)


@pytest.fixture
def sample_item_lanche():
    """Item do tipo LANCHE vindo do microserviço de pedidos"""
    return ItemPedido(id_produto=1, quantidade=1)


@pytest.fixture
def sample_item_bebida():
    """Item do tipo BEBIDA vindo do microserviço de pedidos"""
    return ItemPedido(id_produto=2, quantidade=1)


@pytest.fixture
def sample_evento_pedido(sample_item_lanche, sample_item_bebida):
    """Evento de pedido para testes"""
    return EventoPedido(
        id_pedido=12345,
        cpf_cliente="123.456.789-00",
        status="criado",  # Status do microserviço de pedidos
        itens=[sample_item_lanche, sample_item_bebida],
        total_pedido=20.50,
        tempo_estimado=None,
        criado_em=datetime.now(),
    )


@pytest.fixture
def sample_evento_pagamento():
    """Evento de pagamento para testes"""
    return EventoPagamento(
        id_pagamento=98765,
        id_pedido=12345,
        status=StatusPagamento.PAGO,
        criado_em=datetime.now(),
    )


@pytest.fixture
def sample_acompanhamento(sample_item_lanche) -> Acompanhamento:
    """Fixture com acompanhamento de exemplo para testes"""
    return Acompanhamento(
        id_pedido=12345,
        cpf_cliente="123.456.789-00",
        status=StatusPedido.RECEBIDO,
        status_pagamento=StatusPagamento.PENDENTE,
        itens=[sample_item_lanche],  # Usando item da fixture
        valor_pago=None,
        tempo_estimado="30 minutos",
        atualizado_em=datetime.now(),
    )
