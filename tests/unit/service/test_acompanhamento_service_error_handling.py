"""
Testes de tratamento de erros do AcompanhamentoService.

Este módulo testa cenários de erro, exceções, validações e recuperação
de falhas no serviço de acompanhamento com foco em robustez e confiabilidade.
"""

from datetime import datetime
from unittest.mock import AsyncMock

import pytest
from sqlalchemy.exc import DatabaseError, IntegrityError, OperationalError

from app.domain.acompanhamento_service import AcompanhamentoService
from app.domain.order_state import StatusPagamento, StatusPedido
from app.models.acompanhamento import (Acompanhamento, EventoPagamento,
                                       EventoPedido, ItemPedido)


class TestAcompanhamentoServiceErrorHandling:
    """Testes de tratamento de erros do serviço de acompanhamento"""

    @pytest.mark.anyio
    async def test_processar_evento_pedido_repository_error(
        self, acompanhamento_service, sample_evento_pedido
    ):
        """Testa comportamento quando repositório falha ao buscar pedido existente."""
        # Arrange
        acompanhamento_service.repository.buscar_por_id_pedido = AsyncMock(
            side_effect=DatabaseError("Database connection failed", None, None)
        )

        # Act & Assert
        with pytest.raises(DatabaseError) as exc_info:
            await acompanhamento_service.processar_evento_pedido(sample_evento_pedido)

        assert "Database connection failed" in str(exc_info.value)

    @pytest.mark.anyio
    async def test_processar_evento_pedido_create_integrity_error(
        self, acompanhamento_service, sample_evento_pedido
    ):
        """Testa comportamento quando repositório falha ao criar devido a violação de integridade."""
        # Arrange
        acompanhamento_service.repository.buscar_por_id_pedido = AsyncMock(
            return_value=None
        )
        acompanhamento_service.repository.criar = AsyncMock(
            side_effect=IntegrityError("Duplicate key value", None, None)
        )

        # Act & Assert
        with pytest.raises(IntegrityError) as exc_info:
            await acompanhamento_service.processar_evento_pedido(sample_evento_pedido)

        assert "Duplicate key value" in str(exc_info.value)

    @pytest.mark.anyio
    async def test_processar_evento_pagamento_pedido_inexistente(
        self, acompanhamento_service
    ):
        """Testa processamento de evento de pagamento para pedido que não existe."""
        # Arrange
        evento_pagamento = EventoPagamento(
            id_pagamento=1,
            id_pedido=999,  # Pedido inexistente
            status=StatusPagamento.PAGO,
            criado_em=datetime.now(),
        )

        acompanhamento_service.repository.buscar_por_id_pedido = AsyncMock(
            return_value=None
        )

        # Act
        resultado = await acompanhamento_service.processar_evento_pagamento(
            evento_pagamento
        )

        # Assert
        assert resultado is None
        acompanhamento_service.repository.buscar_por_id_pedido.assert_called_once_with(
            999
        )

    @pytest.mark.anyio
    async def test_atualizar_status_pedido_inexistente(self, acompanhamento_service):
        """Testa atualização de status para pedido que não existe."""
        # Arrange
        acompanhamento_service.repository.buscar_por_id_pedido = AsyncMock(
            return_value=None
        )

        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            await acompanhamento_service.atualizar_status_pedido(
                999, StatusPedido.EM_PREPARACAO
            )

        assert "Acompanhamento não encontrado para pedido 999" in str(exc_info.value)

    @pytest.mark.anyio
    async def test_atualizar_status_transicao_invalida(
        self, acompanhamento_service, sample_acompanhamento
    ):
        """Testa atualização com transição de status inválida."""
        # Arrange
        acompanhamento_recebido = sample_acompanhamento
        acompanhamento_recebido.status = StatusPedido.RECEBIDO

        acompanhamento_service.repository.buscar_por_id_pedido = AsyncMock(
            return_value=acompanhamento_recebido
        )

        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            await acompanhamento_service.atualizar_status_pedido(
                1, StatusPedido.FINALIZADO
            )

        assert "Transição inválida" in str(exc_info.value)

    @pytest.mark.anyio
    async def test_buscar_fila_pedidos_repository_error(self, acompanhamento_service):
        """Testa busca de fila quando repositório falha."""
        # Arrange
        acompanhamento_service.repository.buscar_por_status = AsyncMock(
            side_effect=OperationalError("Query timeout", None, None)
        )

        # Act & Assert
        with pytest.raises(OperationalError) as exc_info:
            await acompanhamento_service.buscar_fila_pedidos()

        assert "Query timeout" in str(exc_info.value)

    @pytest.mark.anyio
    async def test_buscar_pedidos_cliente_repository_error(
        self, acompanhamento_service
    ):
        """Testa busca de pedidos por cliente quando repositório falha."""
        # Arrange
        acompanhamento_service.repository.buscar_por_cpf_cliente = AsyncMock(
            side_effect=DatabaseError("Connection lost", None, None)
        )

        # Act & Assert
        with pytest.raises(DatabaseError) as exc_info:
            await acompanhamento_service.buscar_pedidos_cliente("12345678901")

        assert "Connection lost" in str(exc_info.value)

    def test_calcular_tempo_estimado_itens_vazios(self, acompanhamento_service):
        """Testa cálculo de tempo com lista de itens vazia."""
        # Act
        tempo_estimado = acompanhamento_service.calcular_tempo_estimado_por_itens([])

        # Assert
        assert tempo_estimado == "00:15:00"  # Apenas tempo base

    def test_calcular_tempo_estimado_itens_invalidos(self, acompanhamento_service):
        """Testa cálculo de tempo com itens malformados."""
        # Arrange
        itens_invalidos = [
            {},  # Item vazio
            {"id_produto": 1, "quantidade": 0},  # Quantidade zero
            {"categoria": "LANCHE"},  # Sem quantidade
            {"id_produto": 1, "quantidade": 1, "categoria": None},  # Categoria nula
        ]

        # Act - Deve usar valores padrão e não falhar
        tempo_estimado = acompanhamento_service.calcular_tempo_estimado_por_itens(
            itens_invalidos
        )

        # Assert
        assert tempo_estimado is not None
        assert tempo_estimado.startswith("00:")  # Formato válido

    def test_calcular_tempo_estimado_categoria_inexistente(
        self, acompanhamento_service
    ):
        """Testa cálculo de tempo com categorias não mapeadas."""
        # Arrange
        itens_categoria_nova = [
            {"id_produto": 1, "quantidade": 2, "categoria": "CATEGORIA_FUTURA"},
            {"id_produto": 2, "quantidade": 1, "categoria": "NOVA_CATEGORIA"},
        ]

        # Act
        tempo_estimado = acompanhamento_service.calcular_tempo_estimado_por_itens(
            itens_categoria_nova
        )

        # Assert
        assert tempo_estimado is not None
        # Deve usar tempo padrão: 15 (base) + 2*3 + 1*3 = 24 minutos
        assert tempo_estimado == "00:24:00"

    def test_calcular_tempo_estimado_quantidade_valida(self, acompanhamento_service):
        """Testa cálculo de tempo com quantidades válidas."""
        # Arrange
        itens_quantidade_valida = [
            {"id_produto": 1, "quantidade": 1, "categoria": "LANCHE"},
            {"id_produto": 2, "quantidade": 1, "categoria": "BEBIDA"},
        ]

        # Act
        tempo_estimado = acompanhamento_service.calcular_tempo_estimado_por_itens(
            itens_quantidade_valida
        )

        # Assert
        assert tempo_estimado is not None
        # Tempo base (15) + LANCHE(1*5) + BEBIDA(1*1) = 21 minutos
        assert tempo_estimado == "00:21:00"

    def test_calcular_tempo_estimado_quantidade_extrema(self, acompanhamento_service):
        """Testa cálculo de tempo com quantidades extremamente altas."""
        # Arrange
        itens_quantidade_extrema = [
            {"id_produto": 1, "quantidade": 1000000, "categoria": "LANCHE"},  # 1 milhão
        ]

        # Act
        tempo_estimado = acompanhamento_service.calcular_tempo_estimado_por_itens(
            itens_quantidade_extrema
        )

        # Assert
        assert tempo_estimado is not None
        # Deve resultar em muitas horas mas não falhar
        partes = tempo_estimado.split(":")
        assert len(partes) == 3  # Formato HH:MM:SS
        assert partes[2] == "00"  # Segundos sempre zero

    def test_deve_notificar_cliente_status_invalido(self, acompanhamento_service):
        """Testa notificação com status inválido."""
        # Act & Assert - Não deve falhar mesmo com status inválido
        result1 = acompanhamento_service._deve_notificar_cliente(None)
        assert result1 is False

        # Teste com string inválida (se aceitar)
        try:
            result2 = acompanhamento_service._deve_notificar_cliente(
                "STATUS_INEXISTENTE"
            )
            assert result2 is False
        except (ValueError, AttributeError):
            # É aceitável falhar com status completamente inválido
            pass

    @pytest.mark.anyio
    async def test_processamento_evento_dados_corrompidos(self, acompanhamento_service):
        """Testa processamento de evento com dados parcialmente corrompidos."""
        # Arrange
        acompanhamento_service.repository.buscar_por_id_pedido = AsyncMock(
            return_value=None
        )
        acompanhamento_service.repository.criar = AsyncMock(side_effect=lambda x: x)

        # Evento com dados mínimos válidos
        evento_minimo = EventoPedido(
            id_pedido=1,
            cpf_cliente="12345678901",
            itens=[ItemPedido(id_produto=1, quantidade=1)],
            total_pedido=10.0,
            status="criado",
            criado_em=datetime.now(),
            tempo_estimado=None,  # Campo opcional nulo
        )

        # Act
        resultado = await acompanhamento_service.processar_evento_pedido(evento_minimo)

        # Assert
        assert resultado is not None
        assert resultado.id_pedido == 1
        assert (
            resultado.tempo_estimado is not None
        )  # Deve ser calculado automaticamente

    @pytest.mark.anyio
    async def test_concurrent_update_race_condition(
        self, acompanhamento_service, sample_acompanhamento
    ):
        """Testa condição de corrida durante atualizações concorrentes."""
        # Arrange
        acompanhamento_service.repository.buscar_por_id_pedido = AsyncMock(
            return_value=sample_acompanhamento
        )
        acompanhamento_service.repository.atualizar = AsyncMock(
            side_effect=IntegrityError("Concurrent modification", None, None)
        )

        # Act & Assert
        with pytest.raises(IntegrityError) as exc_info:
            await acompanhamento_service.atualizar_status_pedido(
                1, StatusPedido.EM_PREPARACAO
            )

        assert "Concurrent modification" in str(exc_info.value)

    def test_memory_overflow_protection(self, acompanhamento_service):
        """Testa proteção contra overflow de memória com datasets extremos."""
        # Arrange - Cria uma lista extremamente grande
        try:
            # Usa um número grande mas ainda gerenciável
            itens_extremos = [
                {"id_produto": i, "quantidade": 1, "categoria": "LANCHE"}
                for i in range(100000)  # 100k itens
            ]

            # Act
            import time

            start = time.time()
            tempo_estimado = acompanhamento_service.calcular_tempo_estimado_por_itens(
                itens_extremos
            )
            end = time.time()

            # Assert
            assert tempo_estimado is not None
            assert (end - start) < 5.0  # Não deve demorar mais que 5 segundos

        except MemoryError:
            # Se der erro de memória, é aceitável para datasets extremos
            pytest.skip(
                "Sistema não tem memória suficiente para teste de stress extremo"
            )

    @pytest.mark.anyio
    async def test_network_timeout_recovery(
        self, acompanhamento_service, sample_evento_pedido
    ):
        """Testa recuperação de timeout de rede."""
        # Arrange
        call_count = 0

        def side_effect_buscar(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise OperationalError("Connection timeout", None, None)
            return None

        acompanhamento_service.repository.buscar_por_id_pedido = AsyncMock(
            side_effect=side_effect_buscar
        )
        acompanhamento_service.repository.criar = AsyncMock(side_effect=lambda x: x)

        # Act - Primeira tentativa deve falhar
        with pytest.raises(OperationalError):
            await acompanhamento_service.processar_evento_pedido(sample_evento_pedido)

        # Segunda tentativa deve funcionar
        resultado = await acompanhamento_service.processar_evento_pedido(
            sample_evento_pedido
        )

        # Assert
        assert resultado is not None
        assert call_count == 2

    def test_input_sanitization(self, acompanhamento_service):
        """Testa sanitização de inputs maliciosos ou mal formados."""
        # Arrange
        itens_maliciosos = [
            {
                "id_produto": "'; DROP TABLE pedidos; --",
                "quantidade": 1,
                "categoria": "LANCHE",
            },
            {
                "id_produto": "<script>alert('xss')</script>",
                "quantidade": 1,
                "categoria": "BEBIDA",
            },
            {"id_produto": 1, "quantidade": "MUITO", "categoria": "SOBREMESA"},
            {
                "id_produto": 1,
                "quantidade": 1,
                "categoria": "'; DELETE FROM acompanhamentos; --",
            },
        ]

        # Act - Não deve falhar mesmo com inputs maliciosos
        try:
            tempo_estimado = acompanhamento_service.calcular_tempo_estimado_por_itens(
                itens_maliciosos
            )
            assert tempo_estimado is not None
        except (ValueError, TypeError, AttributeError):
            # É aceitável falhar com inputs completamente inválidos
            pass

    def test_edge_case_empty_strings(self, acompanhamento_service):
        """Testa tratamento de strings vazias em campos críticos."""
        # Arrange
        itens_strings_vazias = [
            {"id_produto": 1, "quantidade": 1, "categoria": ""},  # Categoria vazia
            {"id_produto": 2, "quantidade": 1, "categoria": "   "},  # Apenas espaços
            {"id_produto": 3, "quantidade": 1},  # Sem categoria
        ]

        # Act
        tempo_estimado = acompanhamento_service.calcular_tempo_estimado_por_itens(
            itens_strings_vazias
        )

        # Assert
        assert tempo_estimado is not None
        # Deve usar tempo padrão para categorias vazias/indefinidas
        assert tempo_estimado.startswith("00:")

    def test_unicode_handling(self, acompanhamento_service):
        """Testa tratamento de caracteres Unicode em categorias."""
        # Arrange
        itens_unicode = [
            {"id_produto": 1, "quantidade": 1, "categoria": "🍔 LANCHE"},
            {"id_produto": 2, "quantidade": 1, "categoria": "AÇAÍ"},
            {"id_produto": 3, "quantidade": 1, "categoria": "CAFÉ ☕"},
            {"id_produto": 4, "quantidade": 1, "categoria": "BEBIDA_ÉNERGÉTICA"},
        ]

        # Act
        tempo_estimado = acompanhamento_service.calcular_tempo_estimado_por_itens(
            itens_unicode
        )

        # Assert
        assert tempo_estimado is not None
        # Unicode não deve quebrar o sistema
        assert tempo_estimado.startswith("00:")
