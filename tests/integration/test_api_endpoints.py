"""
Testes de integração para endpoints de API do acompanhamento.
Testa todos os endpoints com cenários reais e validação completa.
"""

import os
from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch

import pytest

# Os imports específicos serão feitos dentro dos métodos para evitar problemas de resolução

# Set test environment before imports
os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///test.db")

from app.domain.order_state import StatusPagamento, StatusPedido
from app.models.acompanhamento import Acompanhamento, ItemPedido


@pytest.fixture
def sample_evento_pedido_data():
    """Dados de exemplo para evento de pedido."""
    return {
        "id_pedido": 12345,
        "cpf_cliente": "12345678901",
        "itens": [
            {"id_produto": 101, "quantidade": 2},
            {"id_produto": 102, "quantidade": 1},
        ],
        "total_pedido": 45.90,
        "tempo_estimado": "25 min",
        "status": "criado",
        "criado_em": "2025-07-21T10:00:00Z",
    }


@pytest.fixture
def sample_evento_pagamento_data():
    """Dados de exemplo para evento de pagamento."""
    return {
        "id_pagamento": 789,
        "id_pedido": 12345,
        "status": "pago",
        "criado_em": "2025-07-21T10:05:00Z",
    }


@pytest.fixture
def sample_item_pedido():
    """Item de pedido de exemplo."""
    from app.models.acompanhamento import ItemPedido

    return ItemPedido(
        id_produto=101, nome_produto="Produto Teste", quantidade=2, preco_unitario=12.50
    )


@pytest.fixture
def sample_acompanhamento(sample_item_pedido):
    """Acompanhamento de exemplo para mocks."""
    from app.models.acompanhamento import (Acompanhamento, StatusPagamento,
                                           StatusPedido)

    return Acompanhamento(
        id_pedido=12345,
        cpf_cliente="12345678901",
        status=StatusPedido.RECEBIDO,
        status_pagamento=StatusPagamento.PENDENTE,
        itens=[sample_item_pedido],
        tempo_estimado="25 min",
        atualizado_em=datetime.now(timezone.utc),
    )


class TestHealthEndpoints:
    """Testes dos endpoints de health check."""

    def test_root_endpoint_function(self):
        """Testa função do endpoint raiz diretamente."""
        with patch("app.db.session.async_session"):
            from app.main import read_root

            result = read_root()
            assert (
                result["message"] == "Microservice de Acompanhamento está funcionando!"
            )

    def test_main_health_endpoint_function(self):
        """Testa função do endpoint de health principal."""
        with patch("app.db.session.async_session"):
            from app.main import health_check

            result = health_check()
            assert result["status"] == "healthy"
            assert result["version"] == "1.0.0"

    @pytest.mark.anyio
    async def test_acompanhamento_health_endpoint_function(self):
        """Testa função do endpoint de health específico."""
        with patch("app.db.session.async_session"):
            from app.api.v1.acompanhamento import health_check

            result = await health_check()
            assert result.status == "healthy"
            assert result.service == "acompanhamento"
            assert result.version == "1.0.0"


class TestEventoEndpoints:
    """Testes dos novos endpoints de eventos Kafka."""

    @pytest.mark.anyio
    async def test_evento_pedido_success_function(
        self, sample_evento_pedido_data, sample_acompanhamento
    ):
        """Testa função de processamento de evento de pedido diretamente."""
        with patch("app.db.session.async_session"):
            with patch(
                "app.api.dependencies.get_acompanhamento_service"
            ) as mock_service:
                # Configura mock do service
                mock_service_instance = AsyncMock()
                mock_service.return_value = mock_service_instance
                mock_service_instance.processar_evento_pedido.return_value = (
                    sample_acompanhamento
                )

                # Converte dados para schema
                from app.api.v1.acompanhamento import processar_evento_pedido
                from app.schemas.acompanhamento_schemas import \
                    EventoPedidoRequest

                evento_request = EventoPedidoRequest(**sample_evento_pedido_data)

                # Chama a função diretamente
                result = await processar_evento_pedido(
                    evento_request, mock_service_instance
                )

                # Validações
                assert "processado com sucesso" in result.message
                # Verifica se processamento foi chamado
                mock_service_instance.processar_evento_pedido.assert_called_once()

    @pytest.mark.anyio
    async def test_evento_pedido_dados_invalidos_schema(self):
        """Testa validação do schema EventoPedidoRequest."""
        from app.schemas.acompanhamento_schemas import EventoPedidoRequest

        # Dados inválidos - sem itens
        dados_invalidos = {
            "id_pedido": 12345,
            "cpf_cliente": "12345678901",
            "itens": [],  # Lista vazia
            "total_pedido": 45.90,
            "status": "criado",
            "criado_em": "2025-07-21T10:00:00Z",
        }

        try:
            EventoPedidoRequest(**dados_invalidos)
            assert False, "Deveria ter falhado na validação"
        except Exception as e:
            assert "itens" in str(e).lower() or "validation" in str(e).lower()

    @pytest.mark.anyio
    async def test_evento_pedido_pedido_ja_existe_function(
        self, sample_evento_pedido_data
    ):
        """Testa tratamento quando pedido já existe."""
        with patch("app.db.session.async_session"):
            with patch(
                "app.api.dependencies.get_acompanhamento_service"
            ) as mock_service:
                mock_service_instance = AsyncMock()
                mock_service.return_value = mock_service_instance
                mock_service_instance.processar_evento_pedido.side_effect = ValueError(
                    "Pedido já existe"
                )

                from app.api.v1.acompanhamento import processar_evento_pedido
                from app.schemas.acompanhamento_schemas import \
                    EventoPedidoRequest

                evento_request = EventoPedidoRequest(**sample_evento_pedido_data)

                # Deve lançar exceção
                try:
                    await processar_evento_pedido(evento_request, mock_service_instance)
                    assert False, "Deveria ter lançado exceção"
                except Exception as e:
                    # Verifica se é HTTPException com status 409
                    assert (
                        getattr(e, "status_code", None) == 409
                        or "409" in str(e)
                        or "já existe" in str(e)
                    )

    @pytest.mark.anyio
    async def test_evento_pagamento_success_function(
        self, sample_evento_pagamento_data, sample_acompanhamento
    ):
        """Testa função de processamento de evento de pagamento diretamente."""
        with patch("app.db.session.async_session"):
            with patch(
                "app.api.dependencies.get_acompanhamento_service"
            ) as mock_service:
                # Configura mock do service
                mock_service_instance = AsyncMock()
                mock_service.return_value = mock_service_instance

                # Atualiza acompanhamento com pagamento pago
                acompanhamento_pago = sample_acompanhamento.model_copy()
                acompanhamento_pago.status_pagamento = StatusPagamento.PAGO
                mock_service_instance.processar_evento_pagamento.return_value = (
                    acompanhamento_pago
                )

                # Converte dados para schema
                from app.api.v1.acompanhamento import \
                    processar_evento_pagamento
                from app.schemas.acompanhamento_schemas import \
                    EventoPagamentoRequest

                evento_request = EventoPagamentoRequest(**sample_evento_pagamento_data)

                # Chama a função diretamente
                result = await processar_evento_pagamento(
                    evento_request, mock_service_instance
                )

                # Validações
                assert "processado com sucesso" in result.message
                # Verifica se processamento foi chamado
                mock_service_instance.processar_evento_pagamento.assert_called_once()

    @pytest.mark.anyio
    async def test_evento_pagamento_pedido_nao_encontrado_function(
        self, sample_evento_pagamento_data
    ):
        """Testa tratamento quando pedido não existe."""
        with patch("app.db.session.async_session"):
            with patch(
                "app.api.dependencies.get_acompanhamento_service"
            ) as mock_service:
                mock_service_instance = AsyncMock()
                mock_service.return_value = mock_service_instance
                mock_service_instance.processar_evento_pagamento.side_effect = (
                    ValueError("Pedido não encontrado")
                )

                from app.api.v1.acompanhamento import \
                    processar_evento_pagamento
                from app.schemas.acompanhamento_schemas import \
                    EventoPagamentoRequest

                evento_request = EventoPagamentoRequest(**sample_evento_pagamento_data)

                # Deve lançar exceção
                try:
                    await processar_evento_pagamento(
                        evento_request, mock_service_instance
                    )
                    assert False, "Deveria ter lançado exceção"
                except Exception as e:
                    # Verifica se é HTTPException com status 404
                    assert (
                        getattr(e, "status_code", None) == 404
                        or "404" in str(e)
                        or "não encontrado" in str(e)
                    )

    def test_evento_pagamento_dados_invalidos_schema(self):
        """Testa validação do schema EventoPagamentoRequest."""
        from app.schemas.acompanhamento_schemas import EventoPagamentoRequest

        # Dados inválidos - ID negativo
        dados_invalidos = {
            "id_pagamento": -1,  # Valor inválido
            "id_pedido": 12345,
            "status": "pago",
            "criado_em": "2025-07-21T10:05:00Z",
        }

        try:
            EventoPagamentoRequest(**dados_invalidos)
            assert False, "Deveria ter falhado na validação"
        except Exception as e:
            assert "validation" in str(e).lower() or "id_pagamento" in str(e)


class TestExistingEndpointsFunctions:
    """Testes dos endpoints existentes usando funções diretas."""

    @pytest.mark.anyio
    async def test_buscar_pedidos_cliente_function(self, sample_acompanhamento):
        """Testa função de busca por CPF diretamente."""
        with patch("app.db.session.async_session"):
            with patch(
                "app.api.dependencies.get_acompanhamento_service"
            ) as mock_service:
                # Configura mock do service
                mock_service_instance = AsyncMock()
                mock_service.return_value = mock_service_instance
                mock_service_instance.buscar_pedidos_cliente.return_value = [
                    sample_acompanhamento
                ]

                from app.api.v1.acompanhamento import buscar_pedidos_cliente

                # Chama a função diretamente
                result = await buscar_pedidos_cliente(
                    "12345678901", mock_service_instance
                )

                # Validações
                assert isinstance(result, list)
                assert len(result) == 1
                assert result[0] == sample_acompanhamento
                mock_service_instance.buscar_pedidos_cliente.assert_called_once_with(
                    "12345678901"
                )

    @pytest.mark.anyio
    async def test_buscar_acompanhamento_function(self, sample_acompanhamento):
        """Testa função de busca por ID diretamente."""
        with patch("app.db.session.async_session"):
            with patch(
                "app.api.dependencies.get_acompanhamento_service"
            ) as mock_service:
                # Configura mock do service
                mock_service_instance = AsyncMock()
                mock_service.return_value = mock_service_instance
                mock_service_instance.repository.buscar_por_id_pedido.return_value = (
                    sample_acompanhamento
                )

                from app.api.v1.acompanhamento import buscar_acompanhamento

                # Chama a função diretamente
                result = await buscar_acompanhamento(12345, mock_service_instance)

                # Validações - função retorna diretamente o acompanhamento
                assert result == sample_acompanhamento
                mock_service_instance.repository.buscar_por_id_pedido.assert_called_once_with(
                    12345
                )

    @pytest.mark.anyio
    async def test_buscar_acompanhamento_nao_encontrado_function(self):
        """Testa busca por ID quando pedido não existe."""
        with patch("app.db.session.async_session"):
            with patch(
                "app.api.dependencies.get_acompanhamento_service"
            ) as mock_service:
                mock_service_instance = AsyncMock()
                mock_service.return_value = mock_service_instance
                mock_service_instance.repository.buscar_por_id_pedido.return_value = (
                    None
                )

                from app.api.v1.acompanhamento import buscar_acompanhamento

                # Deve lançar exceção
                try:
                    await buscar_acompanhamento(99999, mock_service_instance)
                    assert False, "Deveria ter lançado exceção"
                except Exception as e:
                    # Verifica se é HTTPException com status 404
                    assert (
                        getattr(e, "status_code", None) == 404
                        or "404" in str(e)
                        or "não encontrado" in str(e)
                    )

    @pytest.mark.anyio
    async def test_buscar_fila_pedidos_function(self, sample_acompanhamento):
        """Testa função de listar fila diretamente."""
        with patch("app.db.session.async_session"):
            with patch(
                "app.api.dependencies.get_acompanhamento_service"
            ) as mock_service:
                # Configura mock do service
                mock_service_instance = AsyncMock()
                mock_service.return_value = mock_service_instance

                mock_service_instance.buscar_fila_pedidos.return_value = [
                    sample_acompanhamento
                ]

                from app.api.v1.acompanhamento import buscar_fila_pedidos

                # Chama a função diretamente
                result = await buscar_fila_pedidos(mock_service_instance)

                # Validações - função retorna FilaPedidosResponse
                from app.schemas.acompanhamento_schemas import \
                    FilaPedidosResponse

                assert isinstance(result, FilaPedidosResponse)
                assert result.total == 1
                mock_service_instance.buscar_fila_pedidos.assert_called_once()

    @pytest.mark.anyio
    async def test_atualizar_status_pedido_function(self, sample_acompanhamento):
        """Testa função de atualizar status diretamente."""
        with patch("app.db.session.async_session"):
            with patch(
                "app.api.dependencies.get_acompanhamento_service"
            ) as mock_service:
                # Configura mock do service
                mock_service_instance = AsyncMock()
                mock_service.return_value = mock_service_instance

                # Acompanhamento atualizado
                acompanhamento_atualizado = sample_acompanhamento.model_copy()
                from app.models.acompanhamento import StatusPedido

                acompanhamento_atualizado.status = StatusPedido.EM_PREPARACAO
                mock_service_instance.atualizar_status_pedido.return_value = (
                    acompanhamento_atualizado
                )

                from app.api.v1.acompanhamento import atualizar_status_pedido

                # Chama a função diretamente
                result = await atualizar_status_pedido(
                    12345, sample_acompanhamento, mock_service_instance
                )

                # Validações - função retorna diretamente o acompanhamento atualizado
                assert result == acompanhamento_atualizado
                mock_service_instance.atualizar_status_pedido.assert_called_once()
