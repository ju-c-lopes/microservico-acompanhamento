"""
Testes para processamento de eventos do AcompanhamentoService
"""

import pytest

from app.domain.order_state import StatusPagamento, StatusPedido


class TestAcompanhamentoServiceEventProcessing:
    """Testa processamento de eventos vindos de outros microserviços"""

    @pytest.mark.anyio
    async def test_processar_evento_pedido_novo(
        self,
        acompanhamento_service,
        mock_repository,
        sample_evento_pedido,
        sample_acompanhamento,
    ):
        """
        Testa criação de novo acompanhamento a partir de evento de pedido.

        Cenário: Microserviço de pedidos envia evento de pedido criado
        Resultado esperado: Novo acompanhamento é criado com tempo calculado
        """
        # Arrange
        mock_repository.buscar_por_id_pedido.return_value = None
        mock_repository.criar.return_value = sample_acompanhamento

        # Act
        resultado = await acompanhamento_service.processar_evento_pedido(
            sample_evento_pedido
        )

        # Assert
        assert resultado == sample_acompanhamento
        mock_repository.buscar_por_id_pedido.assert_called_once_with(12345)
        mock_repository.criar.assert_called_once()

        # Verifica dados do acompanhamento criado
        call_args = mock_repository.criar.call_args[0][0]
        assert call_args.id_pedido == 12345
        assert call_args.status == StatusPedido.RECEBIDO
        assert call_args.status_pagamento == StatusPagamento.PENDENTE
        # Tempo deve ter sido calculado baseado nos itens
        assert (
            call_args.tempo_estimado == "00:21:00"
        )  # 15 base + 6 (2 itens x 3 default)

    @pytest.mark.anyio
    async def test_processar_evento_pedido_existente(
        self,
        acompanhamento_service,
        mock_repository,
        sample_evento_pedido,
        sample_acompanhamento,
    ):
        """
        Testa que não cria acompanhamento duplicado.

        Cenário: Evento de pedido que já tem acompanhamento
        Resultado: Retorna acompanhamento existente sem criar novo
        """
        # Arrange
        mock_repository.buscar_por_id_pedido.return_value = sample_acompanhamento

        # Act
        resultado = await acompanhamento_service.processar_evento_pedido(
            sample_evento_pedido
        )

        # Assert
        assert resultado == sample_acompanhamento
        mock_repository.buscar_por_id_pedido.assert_called_once_with(12345)
        mock_repository.criar.assert_not_called()  # Não deve criar novo

    @pytest.mark.anyio
    async def test_processar_evento_pagamento_aprovado(
        self,
        acompanhamento_service,
        mock_repository,
        sample_evento_pagamento,
        sample_acompanhamento,
    ):
        """
        Testa processamento de pagamento aprovado.

        Regra de negócio: Pagamento PAGO + Status RECEBIDO = Status EM_PREPARACAO
        """
        # Arrange
        mock_repository.buscar_por_id_pedido.return_value = sample_acompanhamento

        acompanhamento_atualizado = sample_acompanhamento.model_copy()
        acompanhamento_atualizado.status = StatusPedido.EM_PREPARACAO
        acompanhamento_atualizado.status_pagamento = StatusPagamento.PAGO

        mock_repository.atualizar.return_value = acompanhamento_atualizado

        # Act
        resultado = await acompanhamento_service.processar_evento_pagamento(
            sample_evento_pagamento
        )

        # Assert
        assert resultado.status == StatusPedido.EM_PREPARACAO
        assert resultado.status_pagamento == StatusPagamento.PAGO
        mock_repository.atualizar.assert_called_once()

    @pytest.mark.anyio
    async def test_processar_evento_pagamento_pedido_inexistente(
        self, acompanhamento_service, mock_repository, sample_evento_pagamento
    ):
        """
        Testa processamento de pagamento para pedido inexistente.

        Cenário: Evento de pagamento chega antes do evento de pedido
        Resultado: Retorna None (não pode processar)
        """
        # Arrange
        mock_repository.buscar_por_id_pedido.return_value = None

        # Act
        resultado = await acompanhamento_service.processar_evento_pagamento(
            sample_evento_pagamento
        )

        # Assert
        assert resultado is None
        mock_repository.atualizar.assert_not_called()

    @pytest.mark.anyio
    async def test_processar_evento_pagamento_status_diferente_pago(
        self, acompanhamento_service, mock_repository, sample_acompanhamento
    ):
        """
        Testa processamento de pagamento com status diferente de PAGO.

        Cenário: Pagamento rejeitado ou pendente
        Resultado: Atualiza status_pagamento mas não muda status do pedido
        """
        # Arrange
        from datetime import datetime

        from app.models.acompanhamento import EventoPagamento

        evento_rejeitado = EventoPagamento(
            id_pagamento=98765,
            id_pedido=12345,
            status=StatusPagamento.FALHOU,
            criado_em=datetime.now(),
        )

        mock_repository.buscar_por_id_pedido.return_value = sample_acompanhamento

        acompanhamento_atualizado = sample_acompanhamento.model_copy()
        acompanhamento_atualizado.status_pagamento = StatusPagamento.FALHOU
        # Status do pedido permanece RECEBIDO

        mock_repository.atualizar.return_value = acompanhamento_atualizado

        # Act
        resultado = await acompanhamento_service.processar_evento_pagamento(
            evento_rejeitado
        )

        # Assert
        assert resultado.status == StatusPedido.RECEBIDO  # Não mudou
        assert resultado.status_pagamento == StatusPagamento.FALHOU  # Mudou
        mock_repository.atualizar.assert_called_once()
