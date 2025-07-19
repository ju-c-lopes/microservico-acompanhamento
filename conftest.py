# Configuração global para pytest
import pytest

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
