"""
Testes para regras de negócio do AcompanhamentoService.

Este módulo testa as regras de negócio específicas como transições de status,
validações de estado e lógica de negócios específicos do domínio.
"""

from datetime import datetime

import pytest

from app.domain.order_state import StatusPedido


class TestAcompanhamentoServiceBusinessRules:
    """Testes para regras de negócio do serviço de acompanhamento"""

    @pytest.mark.anyio
    async def test_atualizar_status_pedido_transicao_valida(
        self, acompanhamento_service, mock_repository, sample_acompanhamento
    ):
        """
        Testa transição válida de status do pedido.

        Regra: RECEBIDO -> EM_PREPARACAO -> PRONTO -> FINALIZADO
        """
        # Arrange
        mock_repository.buscar_por_id_pedido.return_value = sample_acompanhamento

        acompanhamento_atualizado = sample_acompanhamento.model_copy()
        acompanhamento_atualizado.status = StatusPedido.EM_PREPARACAO
        acompanhamento_atualizado.atualizado_em = datetime.now()

        mock_repository.atualizar.return_value = acompanhamento_atualizado

        # Act
        resultado = await acompanhamento_service.atualizar_status_pedido(
            12345, StatusPedido.EM_PREPARACAO
        )

        # Assert
        assert resultado.status == StatusPedido.EM_PREPARACAO
        mock_repository.atualizar.assert_called_once()

    @pytest.mark.anyio
    async def test_calcular_tempo_estimado_por_itens(
        self, acompanhamento_service, sample_itens_list
    ):
        """
        Testa cálculo de tempo estimado baseado nos itens do pedido.

        Regra: Tempo base + tempo por categoria de item
        """
        # Act
        tempo_estimado = acompanhamento_service.calcular_tempo_estimado_por_itens(
            sample_itens_list
        )

        # Assert
        # Tempo base (15 min) + itens sem categoria: (2+1+3)*3 = 18 min = 33 minutos = "00:33:00"
        assert tempo_estimado == "00:33:00"

    @pytest.mark.anyio
    async def test_buscar_fila_pedidos(self, acompanhamento_service, mock_repository):
        """
        Testa busca da fila de pedidos (Em preparação e Pronto).

        Linguagem ubíqua: fila_pedidos
        """
        # Arrange
        mock_repository.buscar_por_status.return_value = []

        # Act
        resultado = await acompanhamento_service.buscar_fila_pedidos()

        # Assert
        assert resultado == []
        mock_repository.buscar_por_status.assert_called_once_with(
            [StatusPedido.EM_PREPARACAO, StatusPedido.PRONTO]
        )
