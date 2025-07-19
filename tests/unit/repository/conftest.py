"""
Fixtures compartilhadas para testes do repository

Aqui vamos definir objetos de teste que podem ser reutilizados
em vários testes do repository.
"""

from datetime import datetime
from decimal import Decimal

import pytest

from app.domain.order_state import StatusPagamento, StatusPedido
from app.models.acompanhamento import Acompanhamento, ItemPedido


@pytest.fixture
def sample_itens():
    """
    Cria uma lista de itens de exemplo para usar nos testes.
    Estes itens representam produtos típicos de um pedido.
    """
    return [
        ItemPedido(id_produto=1, quantidade=2, preco_unitario=Decimal("15.50")),
        ItemPedido(id_produto=2, quantidade=1, preco_unitario=Decimal("25.90")),
    ]


@pytest.fixture
def sample_acompanhamento(sample_itens):
    """
    Cria um acompanhamento de exemplo para usar nos testes.

    Por que usar fixture?
    - Reutilização: Mesma estrutura em vários testes
    - Consistência: Sempre os mesmos dados de teste
    - Manutenibilidade: Mudança em um lugar só
    """
    return Acompanhamento(
        id_pedido=12345,
        cpf_cliente="123.456.789-00",
        status=StatusPedido.RECEBIDO,
        status_pagamento=StatusPagamento.PENDENTE,
        itens=sample_itens,
        tempo_estimado="25 min",
        atualizado_em=datetime(2024, 1, 15, 10, 30),
    )


@pytest.fixture
def sample_acompanhamento_em_preparacao(sample_itens):
    """
    Acompanhamento em preparação - útil para testar transições de estado
    """
    return Acompanhamento(
        id_pedido=67890,
        cpf_cliente="987.654.321-00",
        status=StatusPedido.EM_PREPARACAO,
        status_pagamento=StatusPagamento.PAGO,
        itens=sample_itens,
        tempo_estimado="15 min",
        atualizado_em=datetime(2024, 1, 15, 11, 00),
    )


@pytest.fixture
def mock_repository():
    """
    Cria um mock do repository para testes unitários.

    Por que mock?
    - Testes isolados: Não dependem de banco de dados
    - Rápidos: Não fazem I/O real
    - Previsíveis: Controlamos exatamente o que retornam
    """
    from unittest.mock import AsyncMock

    mock_repo = AsyncMock()

    # Configuramos comportamentos padrão do mock
    mock_repo.criar.return_value = None
    mock_repo.buscar_por_id.return_value = None
    mock_repo.buscar_por_id_pedido.return_value = None
    mock_repo.buscar_por_cpf_cliente.return_value = []
    mock_repo.buscar_por_status.return_value = []
    mock_repo.atualizar.return_value = None
    mock_repo.listar_todos.return_value = []

    return mock_repo
