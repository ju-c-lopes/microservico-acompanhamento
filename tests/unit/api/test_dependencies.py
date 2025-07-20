"""
Testes unitários para o sistema de dependências da API.
Valida injeção de dependências, validação de entrada e tratamento de exceções.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import (get_acompanhamento_repository,
                                  get_acompanhamento_service, get_db_session,
                                  get_validated_cpf, handle_service_exceptions,
                                  validate_cpf, validate_id_pedido)
from app.core.exceptions import (AcompanhamentoException,
                                 DatabaseConnectionError, InvalidCPFError)
from app.domain.acompanhamento_service import AcompanhamentoService
from app.repository.acompanhamento_repository import AcompanhamentoRepository


class TestGetDbSession:
    """Testes para a função get_db_session."""

    @pytest.mark.anyio
    async def test_get_db_session_success(self):
        """Testa obtenção bem-sucedida de sessão do banco."""
        mock_session = AsyncMock(spec=AsyncSession)

        with patch("app.api.dependencies.async_session") as mock_async_session:
            mock_async_session.return_value.__aenter__.return_value = mock_session
            mock_async_session.return_value.__aexit__.return_value = None

            # Testa o gerador
            async_gen = get_db_session()
            session = await async_gen.__anext__()

            assert session is mock_session
            mock_async_session.assert_called_once()

    @pytest.mark.anyio
    async def test_get_db_session_sqlalchemy_error(self):
        """Testa tratamento de erro de SQLAlchemy."""
        with patch("app.api.dependencies.async_session") as mock_async_session:
            mock_async_session.side_effect = SQLAlchemyError("Connection failed")

            with pytest.raises(DatabaseConnectionError) as exc_info:
                async_gen = get_db_session()
                await async_gen.__anext__()

            assert exc_info.value.operation == "session_creation"
            assert "Connection failed" in str(exc_info.value.original_error)


class TestGetAcompanhamentoRepository:
    """Testes para a função get_acompanhamento_repository."""

    def test_get_acompanhamento_repository_creation(self):
        """Testa criação do repositório com sessão."""
        mock_session = MagicMock(spec=AsyncSession)

        repository = get_acompanhamento_repository(mock_session)

        assert isinstance(repository, AcompanhamentoRepository)
        assert repository.session is mock_session

    def test_get_acompanhamento_repository_injection(self):
        """Testa que a função é configurada para injeção de dependência."""
        # Verifica se a função tem anotação Depends
        import inspect

        signature = inspect.signature(get_acompanhamento_repository)
        session_param = signature.parameters["session"]

        # Verifica se tem valor padrão (Depends)
        assert session_param.default is not None


class TestGetAcompanhamentoService:
    """Testes para a função get_acompanhamento_service."""

    def test_get_acompanhamento_service_creation(self):
        """Testa criação do serviço com repositório."""
        mock_repository = MagicMock(spec=AcompanhamentoRepository)

        service = get_acompanhamento_service(mock_repository)

        assert isinstance(service, AcompanhamentoService)
        assert service.repository is mock_repository

    def test_get_acompanhamento_service_injection(self):
        """Testa que a função é configurada para injeção de dependência."""
        import inspect

        signature = inspect.signature(get_acompanhamento_service)
        repository_param = signature.parameters["repository"]

        # Verifica se tem valor padrão (Depends)
        assert repository_param.default is not None


class TestHandleServiceExceptions:
    """Testes para o context manager handle_service_exceptions."""

    @pytest.mark.anyio
    async def test_handle_service_exceptions_no_error(self):
        """Testa context manager sem erros."""
        result_value = "test_result"

        async with handle_service_exceptions():
            result = result_value

        assert result == result_value

    @pytest.mark.anyio
    async def test_handle_service_exceptions_acompanhamento_exception(self):
        """Testa tratamento de AcompanhamentoException."""
        custom_exception = AcompanhamentoException("Test error")

        with patch("app.api.dependencies.get_http_status_for_exception") as mock_status:
            mock_status.return_value = 404

            with patch("app.api.dependencies.create_error_response") as mock_response:
                mock_response.return_value = {"error": "test"}

                with pytest.raises(HTTPException) as exc_info:
                    async with handle_service_exceptions():
                        raise custom_exception

                assert exc_info.value.status_code == 404
                assert exc_info.value.detail == {"error": "test"}
                mock_status.assert_called_once_with(custom_exception)
                mock_response.assert_called_once_with(custom_exception)

    @pytest.mark.anyio
    async def test_handle_service_exceptions_generic_exception(self):
        """Testa tratamento de exceção genérica."""
        generic_exception = ValueError("Generic error")

        with pytest.raises(HTTPException) as exc_info:
            async with handle_service_exceptions():
                raise generic_exception

        assert exc_info.value.status_code == 500
        assert "Erro interno do servidor" in exc_info.value.detail["detail"]
        assert exc_info.value.detail["error_code"] == "INTERNAL_SERVER_ERROR"
        assert exc_info.value.detail["error_type"] == "ValueError"


class TestValidateCpf:
    """Testes para a função validate_cpf."""

    def test_validate_cpf_valid_clean(self):
        """Testa validação de CPF válido sem formatação."""
        cpf_limpo = "12345678901"

        result = validate_cpf(cpf_limpo)

        assert result == cpf_limpo

    def test_validate_cpf_valid_formatted(self):
        """Testa validação de CPF válido com formatação."""
        cpf_formatado = "123.456.789-01"
        cpf_esperado = "12345678901"

        result = validate_cpf(cpf_formatado)

        assert result == cpf_esperado

    def test_validate_cpf_with_spaces(self):
        """Testa validação de CPF com espaços."""
        cpf_com_espacos = " 123 456 789 01 "
        cpf_esperado = "12345678901"

        result = validate_cpf(cpf_com_espacos)

        assert result == cpf_esperado

    def test_validate_cpf_invalid_length_short(self):
        """Testa validação de CPF muito curto."""
        cpf_curto = "123456789"

        with pytest.raises(InvalidCPFError) as exc_info:
            validate_cpf(cpf_curto)

        assert exc_info.value.cpf == cpf_curto

    def test_validate_cpf_invalid_length_long(self):
        """Testa validação de CPF muito longo."""
        cpf_longo = "123456789012"

        with pytest.raises(InvalidCPFError) as exc_info:
            validate_cpf(cpf_longo)

        assert exc_info.value.cpf == cpf_longo

    def test_validate_cpf_all_same_digits(self):
        """Testa validação de CPF com todos os dígitos iguais."""
        cpfs_invalidos = [
            "11111111111",
            "22222222222",
            "33333333333",
            "00000000000",
        ]

        for cpf in cpfs_invalidos:
            with pytest.raises(InvalidCPFError) as exc_info:
                validate_cpf(cpf)

            assert exc_info.value.cpf == cpf

    def test_validate_cpf_empty_string(self):
        """Testa validação de CPF vazio."""
        with pytest.raises(InvalidCPFError):
            validate_cpf("")

    def test_validate_cpf_only_letters(self):
        """Testa validação de CPF apenas com letras."""
        with pytest.raises(InvalidCPFError):
            validate_cpf("abcdefghijk")

    def test_validate_cpf_mixed_characters(self):
        """Testa validação de CPF com caracteres especiais."""
        cpf_com_caracteres = "123#456@789$01"
        cpf_esperado = "12345678901"

        result = validate_cpf(cpf_com_caracteres)

        assert result == cpf_esperado


class TestValidateIdPedido:
    """Testes para a função validate_id_pedido."""

    def test_validate_id_pedido_valid_positive(self):
        """Testa validação de ID de pedido positivo válido."""
        valid_ids = [1, 10, 100, 999999]

        for id_pedido in valid_ids:
            result = validate_id_pedido(id_pedido)
            assert result == id_pedido

    def test_validate_id_pedido_zero(self):
        """Testa validação de ID de pedido zero."""
        with pytest.raises(HTTPException) as exc_info:
            validate_id_pedido(0)

        assert exc_info.value.status_code == 400
        assert "número positivo" in exc_info.value.detail["detail"]
        assert exc_info.value.detail["error_code"] == "INVALID_ORDER_ID"

    def test_validate_id_pedido_negative(self):
        """Testa validação de ID de pedido negativo."""
        invalid_ids = [-1, -10, -999]

        for id_pedido in invalid_ids:
            with pytest.raises(HTTPException) as exc_info:
                validate_id_pedido(id_pedido)

            assert exc_info.value.status_code == 400
            assert "número positivo" in exc_info.value.detail["detail"]
            assert exc_info.value.detail["error_code"] == "INVALID_ORDER_ID"
            assert exc_info.value.detail["error_type"] == "ValidationError"


class TestGetValidatedCpf:
    """Testes para a função get_validated_cpf (dependency)."""

    def test_get_validated_cpf_success(self):
        """Testa dependency de validação de CPF com sucesso."""
        cpf_valido = "123.456.789-01"
        cpf_esperado = "12345678901"

        result = get_validated_cpf(cpf_valido)

        assert result == cpf_esperado

    def test_get_validated_cpf_invalid_raises_http_exception(self):
        """Testa dependency de validação de CPF inválido."""
        cpf_invalido = "123"

        with patch("app.api.dependencies.get_http_status_for_exception") as mock_status:
            mock_status.return_value = 400

            with patch("app.api.dependencies.create_error_response") as mock_response:
                mock_response.return_value = {"error": "Invalid CPF"}

                with pytest.raises(HTTPException) as exc_info:
                    get_validated_cpf(cpf_invalido)

                assert exc_info.value.status_code == 400
                assert exc_info.value.detail == {"error": "Invalid CPF"}


class TestDependencyIntegration:
    """Testes de integração das dependências."""

    @pytest.mark.anyio
    async def test_full_dependency_chain(self):
        """Testa cadeia completa de dependências."""
        mock_session = AsyncMock(spec=AsyncSession)

        # Testa criação do repositório
        repository = get_acompanhamento_repository(mock_session)
        assert isinstance(repository, AcompanhamentoRepository)
        assert repository.session is mock_session

        # Testa criação do serviço com repositório
        service = get_acompanhamento_service(repository)
        assert isinstance(service, AcompanhamentoService)
        assert service.repository is repository

    def test_cpf_validation_chain(self):
        """Testa cadeia de validação de CPF."""
        # CPF válido formatado
        cpf_input = "123.456.789-01"

        # Validação básica
        cpf_clean = validate_cpf(cpf_input)
        assert cpf_clean == "12345678901"

        # Dependency wrapper
        cpf_dependency = get_validated_cpf(cpf_input)
        assert cpf_dependency == cpf_clean

    @pytest.mark.anyio
    async def test_exception_handling_chain(self):
        """Testa cadeia de tratamento de exceções."""
        # Testa que diferentes tipos de exceção são tratados adequadamente

        # 1. Exceção customizada
        custom_exception = AcompanhamentoException("Custom error")

        with patch("app.api.dependencies.get_http_status_for_exception") as mock_status:
            mock_status.return_value = 404

            with patch("app.api.dependencies.create_error_response") as mock_response:
                mock_response.return_value = {"error": "custom"}

                with pytest.raises(HTTPException):
                    async with handle_service_exceptions():
                        raise custom_exception

        # 2. Exceção genérica
        with pytest.raises(HTTPException) as exc_info:
            async with handle_service_exceptions():
                raise ValueError("Generic error")

        assert exc_info.value.status_code == 500


@pytest.mark.integration
class TestDependencyInjection:
    """Testes de integração do sistema de injeção de dependências."""

    def test_dependencies_have_correct_annotations(self):
        """Testa que as funções têm anotações corretas para FastAPI."""
        import inspect

        from fastapi import Depends

        # Testa get_acompanhamento_repository
        repo_sig = inspect.signature(get_acompanhamento_repository)
        session_param = repo_sig.parameters["session"]
        assert session_param.annotation == AsyncSession
        # Note: O valor padrão seria Depends(get_db_session)

        # Testa get_acompanhamento_service
        service_sig = inspect.signature(get_acompanhamento_service)
        repo_param = service_sig.parameters["repository"]
        assert repo_param.annotation == AcompanhamentoRepository

    def test_dependency_chain_types(self):
        """Testa tipos retornados pela cadeia de dependências."""
        mock_session = MagicMock(spec=AsyncSession)

        # Repositório
        repository = get_acompanhamento_repository(mock_session)
        assert isinstance(repository, AcompanhamentoRepository)

        # Serviço
        service = get_acompanhamento_service(repository)
        assert isinstance(service, AcompanhamentoService)

        # Verificações de tipo
        assert hasattr(repository, "session")
        assert hasattr(service, "repository")

    @pytest.mark.anyio
    async def test_database_session_lifecycle(self):
        """Testa ciclo de vida da sessão do banco."""
        mock_session = AsyncMock(spec=AsyncSession)

        with patch("app.api.dependencies.async_session") as mock_async_session:
            # Configura o context manager
            mock_async_session.return_value.__aenter__.return_value = mock_session
            mock_async_session.return_value.__aexit__.return_value = None

            # Testa o gerador de sessão
            session_gen = get_db_session()

            # Obtém a sessão
            session = await session_gen.__anext__()
            assert session is mock_session

            # Verifica que foi chamado corretamente
            mock_async_session.assert_called_once()


class TestErrorHandlingScenarios:
    """Testes de cenários específicos de tratamento de erros."""

    @pytest.mark.anyio
    async def test_database_connection_error_propagation(self):
        """Testa propagação de erro de conexão com banco."""
        connection_error = SQLAlchemyError("Database unavailable")

        with patch("app.api.dependencies.async_session") as mock_session:
            mock_session.side_effect = connection_error

            with pytest.raises(DatabaseConnectionError) as exc_info:
                session_gen = get_db_session()
                await session_gen.__anext__()

            assert exc_info.value.operation == "session_creation"
            assert "Database unavailable" in str(exc_info.value.original_error)

    def test_cpf_error_conversion_to_http(self):
        """Testa conversão de erro de CPF para HTTPException."""
        invalid_cpf = "invalid"

        with patch("app.api.dependencies.get_http_status_for_exception") as mock_status:
            mock_status.return_value = 400

            with patch("app.api.dependencies.create_error_response") as mock_response:
                mock_response.return_value = {
                    "detail": "CPF inválido",
                    "error_code": "INVALID_CPF",
                }

                with pytest.raises(HTTPException) as exc_info:
                    get_validated_cpf(invalid_cpf)

                assert exc_info.value.status_code == 400
                assert exc_info.value.detail["error_code"] == "INVALID_CPF"

    @pytest.mark.anyio
    async def test_service_exception_context_manager(self):
        """Testa context manager para exceções de serviço."""
        # Testa múltiplos tipos de exceção
        test_cases = [
            (AcompanhamentoException("Domain error"), 400),
            (ValueError("Generic error"), 500),
            (RuntimeError("Runtime error"), 500),
        ]

        for exception, expected_status in test_cases:
            with patch(
                "app.api.dependencies.get_http_status_for_exception"
            ) as mock_status:
                if isinstance(exception, AcompanhamentoException):
                    mock_status.return_value = expected_status
                    with patch(
                        "app.api.dependencies.create_error_response"
                    ) as mock_response:
                        mock_response.return_value = {"error": "domain"}

                        with pytest.raises(HTTPException) as exc_info:
                            async with handle_service_exceptions():
                                raise exception

                        assert exc_info.value.status_code == expected_status
                else:
                    with pytest.raises(HTTPException) as exc_info:
                        async with handle_service_exceptions():
                            raise exception

                    assert exc_info.value.status_code == expected_status

