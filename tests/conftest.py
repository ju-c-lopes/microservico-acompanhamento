from datetime import datetime
from typing import List

import pytest

from app.models.acompanhamento import ItemPedido


@pytest.fixture
def sample_datetime():
    """Fixed datetime for consistent testing"""
    return datetime(2024, 1, 15, 10, 30, 0)


@pytest.fixture
def sample_item_pedido():
    """Sample ItemPedido for testing"""
    return ItemPedido(id_produto=1, quantidade=2)


@pytest.fixture
def sample_itens_list() -> List[ItemPedido]:
    """Sample list of ItemPedido for testing"""
    return [
        ItemPedido(id_produto=1, quantidade=2),
        ItemPedido(id_produto=2, quantidade=1),
        ItemPedido(id_produto=3, quantidade=3),
    ]


@pytest.fixture
def sample_cpf():
    """Fixture providing a sample CPF for testing"""
    return "123.456.789-00"


@pytest.fixture
def sample_id_pedido():
    """Fixture providing a sample order ID for testing"""
    return 12345


@pytest.fixture
def sample_itens():
    """Fixture providing a simple list of sample items for testing"""
    return [
        ItemPedido(id_produto=1, quantidade=2),
        ItemPedido(id_produto=2, quantidade=1),
    ]


@pytest.fixture
def sample_order_statuses():
    """Sample order statuses for testing"""
    return ["criado", "preparando", "pronto", "entregue"]


@pytest.fixture
def sample_payment_statuses():
    """Sample payment statuses for testing"""
    return ["pago", "pendente", "falhou"]


@pytest.fixture
def sample_acompanhamento_statuses():
    """Sample acompanhamento statuses for testing"""
    return ["aguardando_pagamento", "preparando", "pronto", "entregue"]


# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line("markers", "unit: mark test as unit test")
    config.addinivalue_line("markers", "integration: mark test as integration test")
    config.addinivalue_line("markers", "performance: mark test as performance test")
    config.addinivalue_line("markers", "validation: mark test as validation test")
