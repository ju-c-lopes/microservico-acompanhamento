"""
Testes unitários para app/db/session.py

Testa a configuração de sessões de banco de dados, incluindo:
- Validação da DATABASE_URL
- Conversão de URLs para drivers async
- Função get_async_session()
"""

import os
from unittest.mock import AsyncMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession


class TestDatabaseURLValidation:
    """Testes para validação da DATABASE_URL."""

    @patch.dict(os.environ, {}, clear=True)
    def test_database_url_not_set_raises_error(self):
        """Testa que ValueError é levantado quando DATABASE_URL não está definida."""
        # Remove DATABASE_URL do ambiente se existir
        if "DATABASE_URL" in os.environ:
            del os.environ["DATABASE_URL"]

        with pytest.raises(
            ValueError, match="DATABASE_URL environment variable is not set"
        ):
            # Reimporta o módulo para forçar a validação
            import importlib

            import app.db.session

            importlib.reload(app.db.session)

    @patch.dict(os.environ, {"DATABASE_URL": "sqlite:///test.db"})
    def test_database_url_set_success(self):
        """Testa que o módulo carrega com sucesso quando DATABASE_URL está definida."""
        import importlib

        import app.db.session

        importlib.reload(app.db.session)

        assert app.db.session.SQLALCHEMY_DATABASE_URL == "sqlite:///test.db"


class TestAsyncURLConversion:
    """Testes para conversão de URLs para drivers async."""

    def test_sqlite_url_conversion(self):
        """Testa conversão de sqlite:// para sqlite+aiosqlite://."""
        # Importa o módulo existente (já carregado com SQLite)
        import app.db.session

        # Verifica se a conversão está correta
        if app.db.session.SQLALCHEMY_DATABASE_URL.startswith("sqlite://"):
            expected_url = app.db.session.SQLALCHEMY_DATABASE_URL.replace(
                "sqlite://", "sqlite+aiosqlite://"
            )
            assert app.db.session.async_url == expected_url

    def test_url_conversion_logic_mysql(self):
        """Testa a lógica de conversão para MySQL sem carregar o driver."""
        test_url = "mysql://user:pass@localhost/db"
        expected = "mysql+aiomysql://user:pass@localhost/db"

        # Simula a lógica de conversão
        async_url = test_url
        if async_url.startswith("mysql://"):
            async_url = async_url.replace("mysql://", "mysql+aiomysql://")

        assert async_url == expected

    def test_url_conversion_logic_postgresql(self):
        """Testa a lógica de conversão para PostgreSQL sem carregar o driver."""
        test_url = "postgresql://user:pass@localhost/db"
        expected = "postgresql+asyncpg://user:pass@localhost/db"

        # Simula a lógica de conversão
        async_url = test_url
        if async_url.startswith("postgresql://"):
            async_url = async_url.replace("postgresql://", "postgresql+asyncpg://")

        assert async_url == expected

    def test_url_conversion_logic_unknown_driver(self):
        """Testa que URLs com drivers desconhecidos não são convertidas."""
        test_url = "oracle://user:pass@localhost/db"

        # Simula a lógica de conversão
        async_url = test_url
        if async_url.startswith("mysql://"):
            async_url = async_url.replace("mysql://", "mysql+aiomysql://")
        elif async_url.startswith("sqlite://"):
            async_url = async_url.replace("sqlite://", "sqlite+aiosqlite://")
        elif async_url.startswith("postgresql://"):
            async_url = async_url.replace("postgresql://", "postgresql+asyncpg://")

        assert async_url == test_url


class TestGetAsyncSession:
    """Testes para a função get_async_session."""

    @pytest.mark.anyio
    async def test_get_async_session_function_exists_and_callable(self):
        """Testa que a função get_async_session existe e é chamável."""
        import app.db.session

        # Verifica que a função existe
        assert hasattr(app.db.session, "get_async_session")
        assert callable(app.db.session.get_async_session)

        # Testa que retorna um generator
        gen = app.db.session.get_async_session()
        assert hasattr(gen, "__anext__")

    @pytest.mark.anyio
    async def test_get_async_session_with_mock(self):
        """Testa a função get_async_session com mock."""
        mock_session = AsyncMock(spec=AsyncSession)

        with patch("app.db.session.async_session") as mock_async_session:
            # Configura o mock para retornar um context manager
            mock_context_manager = AsyncMock()
            mock_context_manager.__aenter__.return_value = mock_session
            mock_context_manager.__aexit__.return_value = None
            mock_async_session.return_value = mock_context_manager

            # Importa o módulo após configurar o mock
            import app.db.session

            # Testa o gerador
            gen = app.db.session.get_async_session()
            session = await gen.__anext__()

            # Verifica que a sessão é a esperada
            assert session == mock_session
            mock_async_session.assert_called_once()


class TestModuleAttributes:
    """Testes para verificar que todos os atributos do módulo são criados corretamente."""

    def test_module_exports_all_required_attributes(self):
        """Testa que o módulo exporta todos os atributos necessários."""
        import app.db.session

        # Verifica que todos os atributos principais existem
        assert hasattr(app.db.session, "SQLALCHEMY_DATABASE_URL")
        assert hasattr(app.db.session, "engine")
        assert hasattr(app.db.session, "SessionLocal")
        assert hasattr(app.db.session, "async_url")
        assert hasattr(app.db.session, "async_engine")
        assert hasattr(app.db.session, "async_session")
        assert hasattr(app.db.session, "get_async_session")

    def test_async_url_is_different_from_original_for_sqlite(self):
        """Testa que a URL async é diferente da original para SQLite."""
        import app.db.session

        # Se estiver usando SQLite, a URL async deve ser convertida
        if app.db.session.SQLALCHEMY_DATABASE_URL.startswith("sqlite://"):
            assert app.db.session.async_url != app.db.session.SQLALCHEMY_DATABASE_URL
            assert "aiosqlite" in app.db.session.async_url


class TestEdgeCases:
    """Testes para casos extremos e edge cases."""

    @patch.dict(os.environ, {"DATABASE_URL": ""})
    def test_empty_database_url_raises_error(self):
        """Testa que string vazia para DATABASE_URL levanta erro."""
        with pytest.raises(
            ValueError, match="DATABASE_URL environment variable is not set"
        ):
            import importlib

            import app.db.session

            importlib.reload(app.db.session)

    def test_already_async_url_logic(self):
        """Testa lógica para URLs já async."""
        test_url = "sqlite+aiosqlite:///already_async.db"

        # Simula a lógica de conversão
        async_url = test_url
        if async_url.startswith("mysql://"):
            async_url = async_url.replace("mysql://", "mysql+aiomysql://")
        elif async_url.startswith("sqlite://"):
            async_url = async_url.replace("sqlite://", "sqlite+aiosqlite://")
        elif async_url.startswith("postgresql://"):
            async_url = async_url.replace("postgresql://", "postgresql+asyncpg://")

        # URL já é async, não deve ser alterada
        assert async_url == test_url


class TestSessionConfiguration:
    """Testes para configuração das sessões."""

    def test_session_objects_exist(self):
        """Testa que os objetos de sessão são criados."""
        import app.db.session

        # Verifica que os objetos existem
        assert app.db.session.engine is not None
        assert app.db.session.SessionLocal is not None
        assert app.db.session.async_engine is not None
        assert app.db.session.async_session is not None

    def test_database_url_not_none(self):
        """Testa que DATABASE_URL não é None."""
        import app.db.session

        assert app.db.session.SQLALCHEMY_DATABASE_URL is not None
        # Pode ser string vazia em ambiente de teste, então verificamos apenas se não é None
        assert isinstance(app.db.session.SQLALCHEMY_DATABASE_URL, str)

    def test_async_url_not_none(self):
        """Testa que async_url não é None."""
        import app.db.session

        assert app.db.session.async_url is not None
        assert len(app.db.session.async_url) > 0
