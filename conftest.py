# Configuração global para pytest
import os

import pytest

# Configura variáveis de ambiente necessárias para os testes ANTES de qualquer importação
os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///test.db")
os.environ.setdefault("APP_NAME", "Test Acompanhamento Service")
os.environ.setdefault("SECRET_KEY", "test-secret-key")
os.environ.setdefault("DEBUG", "true")

# Força só asyncio, desabilitando trio que tem problemas de compatibilidade
pytest_plugins = ["anyio"]


def pytest_configure(config):
    """Configuração global do pytest"""
    # Força uso apenas do backend asyncio
    config.option.anyio_backends = ["asyncio"]


@pytest.fixture(scope="session")
def anyio_backend():
    """Força uso apenas do backend asyncio"""
    return "asyncio"
