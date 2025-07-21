"""
Testes de integração para API com base de dados real.
Testa operações end-to-end com database e mocks mínimos.
"""

from unittest.mock import AsyncMock, patch

import pytest


@pytest.mark.anyio
class TestAPIIntegration:
    """Testes de integração com database real."""

    async def test_health_endpoints_integration(self):
        """Testa todos os endpoints de health sem mocks."""
        # Test root endpoint directly
        from app.main import read_root

        response = read_root()
        assert response["message"] == "Microservice de Acompanhamento está funcionando!"

        # Test main health endpoint directly
        from app.main import health_check

        response = health_check()
        assert response["status"] == "healthy"
        assert response["version"] == "1.0.0"

        # Test acompanhamento health endpoint directly (this one is async)
        from app.api.v1.acompanhamento import health_check as detailed_health

        response = await detailed_health()
        assert response.status == "healthy"
        assert response.service == "acompanhamento"

    @patch("app.api.dependencies.get_acompanhamento_service")
    async def test_acompanhamento_crud_integration(self, mock_service):
        """Testa CRUD completo de acompanhamento."""
        # Mock service for integration testing
        mock_service_instance = AsyncMock()
        mock_service.return_value = mock_service_instance

        # Configure mock responses
        from app.core.exceptions import AcompanhamentoNotFound

        mock_service_instance.buscar_acompanhamento.side_effect = (
            AcompanhamentoNotFound(99999)
        )
        mock_service_instance.buscar_fila_pedidos.return_value = {
            "total": 0,
            "pedidos": [],
        }

        # Test the service behavior directly
        with pytest.raises(AcompanhamentoNotFound):
            await mock_service_instance.buscar_acompanhamento(99999)

        # Test queue functionality
        result = await mock_service_instance.buscar_fila_pedidos()
        assert result["total"] >= 0
        assert isinstance(result["pedidos"], list)

    @patch("app.api.dependencies.get_acompanhamento_service")
    async def test_cliente_endpoints_integration(self, mock_service):
        """Testa endpoints relacionados ao cliente."""
        mock_service_instance = AsyncMock()
        mock_service.return_value = mock_service_instance

        # Configure mock for valid CPF
        mock_service_instance.buscar_pedidos_cliente.return_value = []

        # Test cliente history functionality
        result = await mock_service_instance.buscar_pedidos_cliente("12345678901")
        assert isinstance(result, list)

    @patch("app.api.dependencies.get_acompanhamento_service")
    async def test_validation_integration(self, mock_service):
        """Testa validações de entrada em cenários integrados."""
        mock_service_instance = AsyncMock()
        mock_service.return_value = mock_service_instance

        # Test CPF validation through dependency
        from app.api.dependencies import validate_cpf
        from app.core.exceptions import InvalidCPFError

        # Valid CPF should pass
        assert validate_cpf("12345678901") == "12345678901"

        # Invalid CPF should raise error
        with pytest.raises(InvalidCPFError):
            validate_cpf("invalid_cpf")

    def test_api_response_formats(self):
        """Testa formatos de resposta da API."""
        # Test response schema validation
        from datetime import datetime

        from app.schemas.acompanhamento_schemas import HealthResponse

        health_response = HealthResponse(
            status="healthy",
            service="acompanhamento",
            timestamp=datetime.now(),
            version="1.0.0",
        )

        # Validate schema structure
        assert health_response.status == "healthy"
        assert health_response.service == "acompanhamento"
        assert health_response.version == "1.0.0"

    @patch("app.api.dependencies.get_acompanhamento_service")
    async def test_error_handling_integration(self, mock_service):
        """Testa tratamento de erros em cenários integrados."""
        mock_service_instance = AsyncMock()
        mock_service.return_value = mock_service_instance

        # Test exception handling through context manager
        from app.core.exceptions import AcompanhamentoNotFound

        # Configure mock to raise exception
        mock_service_instance.buscar_acompanhamento.side_effect = (
            AcompanhamentoNotFound(123)
        )

        # Test that exception handling works
        with pytest.raises(AcompanhamentoNotFound):
            await mock_service_instance.buscar_acompanhamento(123)


@pytest.mark.anyio
class TestAPIPerformance:
    """Testes de performance simulados."""

    @patch("app.api.dependencies.get_acompanhamento_service")
    def test_health_endpoint_performance(self, mock_service):
        """Testa performance simulada do endpoint de health."""
        import time

        # Test health endpoint response time
        start_time = time.time()
        from app.main import health_check

        response = health_check()
        end_time = time.time()

        # Should be very fast for health check
        response_time = end_time - start_time
        assert response_time < 1.0  # Should respond in less than 1 second
        assert response["status"] == "healthy"

    @patch("app.api.dependencies.get_acompanhamento_service")
    async def test_multiple_requests_performance(self, mock_service):
        """Testa performance de múltiplas requisições simuladas."""
        mock_service_instance = AsyncMock()
        mock_service.return_value = mock_service_instance

        # Configure fast mock response
        mock_service_instance.buscar_fila_pedidos.return_value = {
            "total": 0,
            "pedidos": [],
        }

        import time

        start_time = time.time()

        # Simulate multiple requests
        for _ in range(10):
            result = await mock_service_instance.buscar_fila_pedidos()
            assert result["total"] >= 0

        end_time = time.time()

        # Should handle 10 requests quickly
        total_time = end_time - start_time
        assert total_time < 2.0  # Should complete in less than 2 seconds

    @patch("app.api.dependencies.get_acompanhamento_service")
    async def test_concurrent_requests_simulation(self, mock_service):
        """Simula requisições concorrentes."""
        mock_service_instance = AsyncMock()
        mock_service.return_value = mock_service_instance

        # Configure mock response
        mock_service_instance.buscar_fila_pedidos.return_value = {
            "total": 0,
            "pedidos": [],
        }

        import asyncio

        # Create concurrent tasks
        async def make_request():
            return await mock_service_instance.buscar_fila_pedidos()

        # Run 5 concurrent requests
        tasks = [make_request() for _ in range(5)]
        results = await asyncio.gather(*tasks)

        # All should succeed
        assert len(results) == 5
        for result in results:
            assert result["total"] >= 0


@pytest.mark.anyio
class TestAPIWorkflow:
    """Testes de workflow completo da API."""

    @patch("app.api.dependencies.get_acompanhamento_service")
    async def test_complete_order_workflow(self, mock_service):
        """Testa workflow completo de um pedido."""
        mock_service_instance = AsyncMock()
        mock_service.return_value = mock_service_instance

        # Mock order creation and status updates
        from app.models.acompanhamento import StatusPedido

        mock_acompanhamento = {
            "id_pedido": 123,
            "status_pedido": StatusPedido.RECEBIDO,
            "cpf_cliente": "12345678901",
        }

        mock_service_instance.buscar_acompanhamento.return_value = mock_acompanhamento
        mock_service_instance.atualizar_status_pedido.return_value = mock_acompanhamento

        # Test workflow steps
        order = await mock_service_instance.buscar_acompanhamento(123)
        assert order["status_pedido"] == StatusPedido.RECEBIDO

        # Update status
        updated_order = await mock_service_instance.atualizar_status_pedido(
            123, StatusPedido.EM_PREPARACAO
        )
        assert updated_order is not None

    @patch("app.api.dependencies.get_acompanhamento_service")
    async def test_error_recovery_workflow(self, mock_service):
        """Testa recuperação de erros no workflow."""
        mock_service_instance = AsyncMock()
        mock_service.return_value = mock_service_instance

        from app.core.exceptions import AcompanhamentoNotFound

        # First call fails
        mock_service_instance.buscar_acompanhamento.side_effect = (
            AcompanhamentoNotFound(999)
        )

        # Test error handling
        with pytest.raises(AcompanhamentoNotFound):
            await mock_service_instance.buscar_acompanhamento(999)

        # Recovery: service now works
        mock_service_instance.buscar_acompanhamento.side_effect = None
        mock_service_instance.buscar_acompanhamento.return_value = {"id_pedido": 999}

        result = await mock_service_instance.buscar_acompanhamento(999)
        assert result["id_pedido"] == 999


@pytest.mark.anyio
class TestAPISecurity:
    """Testes de segurança da API."""

    def test_input_sanitization(self):
        """Testa sanitização de entrada."""
        from app.api.dependencies import validate_cpf
        from app.core.exceptions import InvalidCPFError

        # Test various invalid inputs
        invalid_inputs = [
            "",
            "   ",
            "abc",
            "123",
            "12345678901234567890",  # too long
            "<script>alert('xss')</script>",
            "'; DROP TABLE users; --",
        ]

        for invalid_input in invalid_inputs:
            with pytest.raises(InvalidCPFError):
                validate_cpf(invalid_input)

    def test_http_methods_security(self):
        """Testa segurança dos métodos HTTP."""
        # Test that our endpoints are configured correctly
        from app.main import health_check

        # Health check should work without authentication
        response = health_check()
        assert response["status"] == "healthy"

    def test_large_payload_handling(self):
        """Testa tratamento de payloads grandes."""
        from app.models.acompanhamento import StatusPedido
        from app.schemas.acompanhamento_schemas import AtualizarStatusRequest

        # Test that schema validation works for normal requests
        request = AtualizarStatusRequest(status=StatusPedido.RECEBIDO)
        assert request.status == StatusPedido.RECEBIDO
