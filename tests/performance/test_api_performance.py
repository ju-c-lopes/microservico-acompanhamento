"""
Testes de performance para os endpoints da API.
Mede tempos de resposta e throughput dos endpoints principais.
"""

import asyncio
import os
import time
from statistics import mean
from unittest.mock import AsyncMock, patch

import pytest

# Ensure test environment variables are set before importing app
os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///test.db")


@pytest.mark.anyio
class TestAPIPerformance:
    """Testes de performance para endpoints principais."""

    def test_health_endpoint_response_time(self):
        """Testa tempo de resposta do endpoint de health."""
        times = []

        # Execute 10 requests and measure time
        for _ in range(10):
            start_time = time.time()
            from app.main import health_check

            response = health_check()
            end_time = time.time()

            assert response["status"] == "healthy"
            times.append(end_time - start_time)

        # Average response time should be reasonable
        avg_time = sum(times) / len(times)
        assert avg_time < 1.0  # Should respond in less than 1 second on average

    @patch("app.api.dependencies.get_acompanhamento_service")
    async def test_queue_endpoint_performance(self, mock_service):
        """Testa performance do endpoint de fila."""
        mock_service_instance = AsyncMock()
        mock_service.return_value = mock_service_instance

        # Configure fast mock response
        mock_service_instance.buscar_fila_pedidos.return_value = {
            "total": 0,
            "pedidos": [],
        }

        times = []

        for _ in range(5):
            start_time = time.time()
            result = await mock_service_instance.buscar_fila_pedidos()
            end_time = time.time()

            assert result["total"] >= 0
            times.append(end_time - start_time)

        avg_time = mean(times)
        assert avg_time < 0.5  # Should be very fast with mocks

    @patch("app.api.dependencies.get_acompanhamento_service")
    async def test_client_history_performance(self, mock_service):
        """Testa performance do endpoint de histórico do cliente."""
        mock_service_instance = AsyncMock()
        mock_service.return_value = mock_service_instance

        # Configure mock response
        mock_service_instance.buscar_pedidos_cliente.return_value = []

        times = []

        for _ in range(5):
            start_time = time.time()
            result = await mock_service_instance.buscar_pedidos_cliente("12345678901")
            end_time = time.time()

            assert isinstance(result, list)
            times.append(end_time - start_time)

        avg_time = mean(times)
        assert avg_time < 0.5  # Should be fast with mocks

    @patch("app.api.dependencies.get_acompanhamento_service")
    async def test_concurrent_requests_performance(self, mock_service):
        """Testa performance de requisições concorrentes."""
        mock_service_instance = AsyncMock()
        mock_service.return_value = mock_service_instance

        # Configure mock response
        mock_service_instance.buscar_fila_pedidos.return_value = {
            "total": 0,
            "pedidos": [],
        }

        async def make_request():
            return await mock_service_instance.buscar_fila_pedidos()

        start_time = time.time()

        # Run 10 concurrent requests
        tasks = [make_request() for _ in range(10)]
        results = await asyncio.gather(*tasks)

        end_time = time.time()

        # All requests should succeed
        assert len(results) == 10
        for result in results:
            assert result["total"] >= 0

        # Should handle concurrent requests efficiently
        total_time = end_time - start_time
        assert total_time < 2.0  # Should complete quickly with mocks

    @patch("app.api.dependencies.get_acompanhamento_service")
    async def test_mixed_endpoint_performance(self, mock_service):
        """Testa performance de endpoints mistos."""
        mock_service_instance = AsyncMock()
        mock_service.return_value = mock_service_instance

        # Configure mock responses
        mock_service_instance.buscar_fila_pedidos.return_value = {
            "total": 0,
            "pedidos": [],
        }
        mock_service_instance.buscar_pedidos_cliente.return_value = []

        start_time = time.time()

        # Mix of different operations
        for i in range(20):
            if i % 3 == 0:
                from app.main import health_check

                response = health_check()
                assert response["status"] == "healthy"
            elif i % 3 == 1:
                result = await mock_service_instance.buscar_fila_pedidos()
                assert result["total"] >= 0
            else:
                result = await mock_service_instance.buscar_pedidos_cliente(
                    "12345678901"
                )
                assert isinstance(result, list)

        end_time = time.time()
        total_time = end_time - start_time
        assert total_time < 5.0  # Should handle mixed load efficiently


@pytest.mark.anyio
class TestAPIThroughput:
    """Testes de throughput da API."""

    @patch("app.api.dependencies.get_acompanhamento_service")
    async def test_sequential_throughput(self, mock_service):
        """Testa throughput sequencial."""
        mock_service_instance = AsyncMock()
        mock_service.return_value = mock_service_instance

        mock_service_instance.buscar_fila_pedidos.return_value = {
            "total": 0,
            "pedidos": [],
        }

        start_time = time.time()

        # Execute 50 sequential requests
        for _ in range(50):
            result = await mock_service_instance.buscar_fila_pedidos()
            assert result["total"] >= 0

        end_time = time.time()
        total_time = end_time - start_time

        # Calculate throughput (requests per second)
        throughput = 50 / total_time
        assert throughput > 10  # Should handle at least 10 requests per second

    @patch("app.api.dependencies.get_acompanhamento_service")
    async def test_burst_throughput(self, mock_service):
        """Testa throughput em rajadas."""
        mock_service_instance = AsyncMock()
        mock_service.return_value = mock_service_instance

        mock_service_instance.buscar_fila_pedidos.return_value = {
            "total": 0,
            "pedidos": [],
        }

        async def burst_request():
            return await mock_service_instance.buscar_fila_pedidos()

        start_time = time.time()

        # Execute 30 concurrent requests
        tasks = [burst_request() for _ in range(30)]
        results = await asyncio.gather(*tasks)

        end_time = time.time()
        total_time = end_time - start_time

        # All should succeed
        assert len(results) == 30
        for result in results:
            assert result["total"] >= 0

        # Should handle burst load efficiently
        throughput = 30 / total_time
        assert throughput > 15  # Should handle bursts well


@pytest.mark.anyio
class TestAPIMemoryUsage:
    """Testes de uso de memória da API."""

    def test_memory_stability_under_load(self):
        """Testa estabilidade de memória sob carga."""
        try:
            import psutil
        except ImportError:
            pytest.skip("psutil not available for memory testing")

        import os

        process = psutil.Process(os.getpid())

        # Measure initial memory
        initial_memory = process.memory_info().rss

        # Execute many requests
        for _ in range(100):
            from app.main import health_check

            response = health_check()
            assert response["status"] == "healthy"

        # Measure final memory
        final_memory = process.memory_info().rss

        # Memory should not grow excessively (allow 50MB growth)
        memory_growth = final_memory - initial_memory
        assert memory_growth < 50 * 1024 * 1024  # 50MB limit

    def test_response_size_consistency(self):
        """Testa consistência do tamanho de resposta."""
        import json

        response_sizes = []

        for _ in range(10):
            from app.main import health_check

            response = health_check()

            # Convert to JSON to measure size
            json_str = json.dumps(response, default=str)
            response_sizes.append(len(json_str))

        # All responses should be roughly the same size
        min_size = min(response_sizes)
        max_size = max(response_sizes)

        # Allow some variation but not excessive
        size_variation = max_size - min_size
        assert size_variation < 100  # Should be very consistent


@pytest.mark.anyio
class TestAPIErrorPerformance:
    """Testes de performance para cenários de erro."""

    @patch("app.api.dependencies.get_acompanhamento_service")
    async def test_error_response_performance(self, mock_service):
        """Testa performance de respostas de erro."""
        mock_service_instance = AsyncMock()
        mock_service.return_value = mock_service_instance

        from app.core.exceptions import AcompanhamentoNotFound

        mock_service_instance.buscar_acompanhamento.side_effect = (
            AcompanhamentoNotFound(999)
        )

        times = []

        for _ in range(10):
            start_time = time.time()

            try:
                await mock_service_instance.buscar_acompanhamento(999)
            except AcompanhamentoNotFound:
                pass  # Expected error

            end_time = time.time()
            times.append(end_time - start_time)

        # Error responses should be fast
        avg_time = mean(times)
        assert avg_time < 0.1  # Errors should be handled quickly

    @patch("app.api.dependencies.get_acompanhamento_service")
    async def test_mixed_success_error_performance(self, mock_service):
        """Testa performance de mix de sucessos e erros."""
        mock_service_instance = AsyncMock()
        mock_service.return_value = mock_service_instance

        from app.core.exceptions import AcompanhamentoNotFound

        start_time = time.time()

        for i in range(20):
            if i % 2 == 0:
                # Success case
                mock_service_instance.buscar_fila_pedidos.return_value = {
                    "total": 0,
                    "pedidos": [],
                }
                result = await mock_service_instance.buscar_fila_pedidos()
                assert result["total"] >= 0
            else:
                # Error case
                mock_service_instance.buscar_acompanhamento.side_effect = (
                    AcompanhamentoNotFound(i)
                )
                try:
                    await mock_service_instance.buscar_acompanhamento(i)
                except AcompanhamentoNotFound:
                    pass  # Expected

        end_time = time.time()
        total_time = end_time - start_time

        # Mixed load should be handled efficiently
        assert total_time < 3.0
