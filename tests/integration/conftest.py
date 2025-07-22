"""Fixtures for integration tests."""

from datetime import datetime, timezone

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.domain.order_state import StatusPagamento, StatusPedido
from app.models.acompanhamento import ItemPedido
from app.repository.acompanhamento_repository import AcompanhamentoRepository


@pytest_asyncio.fixture
async def test_engine():
    """Create an async SQLite engine for testing."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    await engine.dispose()


@pytest_asyncio.fixture
async def test_session(test_engine):
    """Create an async session for testing."""
    async_session_maker = async_sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session_maker() as session:
        yield session


@pytest_asyncio.fixture
async def repository(test_session):
    """Repository instance configured with test session."""
    return AcompanhamentoRepository(test_session)


@pytest.fixture
def sample_acompanhamento_data():
    """Sample data for testing acompanhamento creation."""
    return {
        "id_pedido": 12345,
        "cpf_cliente": "123.456.789-00",
        "status": StatusPedido.RECEBIDO,
        "status_pagamento": StatusPagamento.PENDENTE,
        "itens": [
            ItemPedido(id_produto=101, quantidade=2),
            ItemPedido(id_produto=102, quantidade=1),
        ],
        "tempo_estimado": "25 min",
        "atualizado_em": datetime.now(timezone.utc),
    }


@pytest.fixture
def sample_acompanhamento_data_alt():
    """Alternative sample data for testing multiple records."""
    return {
        "id_pedido": 67890,
        "cpf_cliente": "987.654.321-00",
        "status": StatusPedido.EM_PREPARACAO,
        "status_pagamento": StatusPagamento.PAGO,
        "itens": [
            ItemPedido(id_produto=201, nome_produto="Produto Alt 1", quantidade=1),
            ItemPedido(id_produto=202, nome_produto="Produto Alt 2", quantidade=3),
        ],
        "tempo_estimado": "15 min",
        "atualizado_em": datetime.now(timezone.utc),
    }
