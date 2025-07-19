"""
Testes para funções auxiliares e utilitárias do AcompanhamentoService.

Este módulo testa as funções de apoio, conversões de formato, validações
e utilitários que suportam as operações principais do serviço.
"""

from datetime import datetime

from app.domain.order_state import (OrderStateManager, StatusPagamento,
                                    StatusPedido, get_estimated_time_minutes)
from app.models.acompanhamento import Acompanhamento


class TestAcompanhamentoServiceHelpers:
    """Testes para funções auxiliares do serviço de acompanhamento"""

    def test_calcular_tempo_estimado_recebido(self, acompanhamento_service):
        """
        Testa cálculo de tempo baseado no status RECEBIDO.

        Regra: Status RECEBIDO = 5 minutos
        """
        # Arrange
        from app.models.acompanhamento import ItemPedido

        acompanhamento = Acompanhamento(
            id_pedido=1,
            cpf_cliente="12345678901",
            status=StatusPedido.RECEBIDO,
            status_pagamento=StatusPagamento.PENDENTE,
            itens=[ItemPedido(id_produto=1, quantidade=1)],
            tempo_estimado="00:05:00",
            atualizado_em=datetime.now(),
        )

        # Act
        tempo_estimado = acompanhamento_service.calcular_tempo_estimado(acompanhamento)

        # Assert
        assert tempo_estimado == "00:05:00"

    def test_calcular_tempo_estimado_em_preparacao(self, acompanhamento_service):
        """
        Testa cálculo de tempo baseado no status EM_PREPARACAO.

        Regra: Status EM_PREPARACAO = 15 minutos
        """
        # Arrange
        from app.models.acompanhamento import ItemPedido

        acompanhamento = Acompanhamento(
            id_pedido=1,
            cpf_cliente="12345678901",
            status=StatusPedido.EM_PREPARACAO,
            status_pagamento=StatusPagamento.PAGO,
            itens=[ItemPedido(id_produto=1, quantidade=1)],
            tempo_estimado="00:15:00",
            atualizado_em=datetime.now(),
        )

        # Act
        tempo_estimado = acompanhamento_service.calcular_tempo_estimado(acompanhamento)

        # Assert
        assert tempo_estimado == "00:15:00"

    def test_calcular_tempo_estimado_pronto(self, acompanhamento_service):
        """
        Testa cálculo de tempo baseado no status PRONTO.

        Regra: Status PRONTO = 10 minutos
        """
        # Arrange
        from app.models.acompanhamento import ItemPedido

        acompanhamento = Acompanhamento(
            id_pedido=1,
            cpf_cliente="12345678901",
            status=StatusPedido.PRONTO,
            status_pagamento=StatusPagamento.PAGO,
            itens=[ItemPedido(id_produto=1, quantidade=1)],
            tempo_estimado="00:10:00",
            atualizado_em=datetime.now(),
        )

        # Act
        tempo_estimado = acompanhamento_service.calcular_tempo_estimado(acompanhamento)

        # Assert
        assert tempo_estimado == "00:10:00"

    def test_calcular_tempo_estimado_finalizado(self, acompanhamento_service):
        """
        Testa cálculo de tempo baseado no status FINALIZADO.

        Regra: Status FINALIZADO = 0 minutos
        """
        # Arrange
        from app.models.acompanhamento import ItemPedido

        acompanhamento = Acompanhamento(
            id_pedido=1,
            cpf_cliente="12345678901",
            status=StatusPedido.FINALIZADO,
            status_pagamento=StatusPagamento.PAGO,
            itens=[ItemPedido(id_produto=1, quantidade=1)],
            tempo_estimado="00:00:00",
            atualizado_em=datetime.now(),
        )

        # Act
        tempo_estimado = acompanhamento_service.calcular_tempo_estimado(acompanhamento)

        # Assert
        assert tempo_estimado == "00:00:00"

    def test_deve_notificar_cliente_status_pronto(self, acompanhamento_service):
        """
        Testa se cliente deve ser notificado quando pedido fica PRONTO.

        Regra: Notificar quando status = PRONTO
        """
        # Act
        deve_notificar = acompanhamento_service._deve_notificar_cliente(
            StatusPedido.PRONTO
        )

        # Assert
        assert deve_notificar is True

    def test_deve_notificar_cliente_status_finalizado(self, acompanhamento_service):
        """
        Testa se cliente deve ser notificado quando pedido é FINALIZADO.

        Regra: Notificar quando status = FINALIZADO
        """
        # Act
        deve_notificar = acompanhamento_service._deve_notificar_cliente(
            StatusPedido.FINALIZADO
        )

        # Assert
        assert deve_notificar is True

    def test_nao_deve_notificar_cliente_status_recebido(self, acompanhamento_service):
        """
        Testa se cliente NÃO deve ser notificado quando pedido está RECEBIDO.

        Regra: Não notificar para status intermediários
        """
        # Act
        deve_notificar = acompanhamento_service._deve_notificar_cliente(
            StatusPedido.RECEBIDO
        )

        # Assert
        assert deve_notificar is False

    def test_nao_deve_notificar_cliente_status_em_preparacao(
        self, acompanhamento_service
    ):
        """
        Testa se cliente NÃO deve ser notificado quando pedido está EM_PREPARACAO.

        Regra: Não notificar para status intermediários
        """
        # Act
        deve_notificar = acompanhamento_service._deve_notificar_cliente(
            StatusPedido.EM_PREPARACAO
        )

        # Assert
        assert deve_notificar is False


class TestOrderStateManagerHelpers:
    """Testes para funções auxiliares do OrderStateManager"""

    def test_can_transition_recebido_para_em_preparacao(self):
        """
        Testa transição válida: RECEBIDO → EM_PREPARACAO.

        Regra: Esta é uma transição válida no fluxo
        """
        # Act
        pode_transicionar = OrderStateManager.can_transition(
            StatusPedido.RECEBIDO, StatusPedido.EM_PREPARACAO
        )

        # Assert
        assert pode_transicionar is True

    def test_can_transition_em_preparacao_para_pronto(self):
        """
        Testa transição válida: EM_PREPARACAO → PRONTO.

        Regra: Esta é uma transição válida no fluxo
        """
        # Act
        pode_transicionar = OrderStateManager.can_transition(
            StatusPedido.EM_PREPARACAO, StatusPedido.PRONTO
        )

        # Assert
        assert pode_transicionar is True

    def test_can_transition_pronto_para_finalizado(self):
        """
        Testa transição válida: PRONTO → FINALIZADO.

        Regra: Esta é uma transição válida no fluxo
        """
        # Act
        pode_transicionar = OrderStateManager.can_transition(
            StatusPedido.PRONTO, StatusPedido.FINALIZADO
        )

        # Assert
        assert pode_transicionar is True

    def test_cannot_transition_recebido_para_pronto(self):
        """
        Testa transição inválida: RECEBIDO → PRONTO (pula etapa).

        Regra: Não pode pular etapas no fluxo
        """
        # Act
        pode_transicionar = OrderStateManager.can_transition(
            StatusPedido.RECEBIDO, StatusPedido.PRONTO
        )

        # Assert
        assert pode_transicionar is False

    def test_cannot_transition_finalizado_para_qualquer(self):
        """
        Testa que pedido FINALIZADO não pode transicionar para nenhum estado.

        Regra: FINALIZADO é estado terminal
        """
        # Act & Assert
        assert (
            OrderStateManager.can_transition(
                StatusPedido.FINALIZADO, StatusPedido.RECEBIDO
            )
            is False
        )

        assert (
            OrderStateManager.can_transition(
                StatusPedido.FINALIZADO, StatusPedido.EM_PREPARACAO
            )
            is False
        )

        assert (
            OrderStateManager.can_transition(
                StatusPedido.FINALIZADO, StatusPedido.PRONTO
            )
            is False
        )

    def test_get_next_valid_states_recebido(self):
        """
        Testa próximos estados válidos para RECEBIDO.

        Regra: RECEBIDO pode ir apenas para EM_PREPARACAO
        """
        # Act
        proximos_estados = OrderStateManager.get_next_valid_states(
            StatusPedido.RECEBIDO
        )

        # Assert
        assert proximos_estados == [StatusPedido.EM_PREPARACAO]

    def test_get_next_valid_states_em_preparacao(self):
        """
        Testa próximos estados válidos para EM_PREPARACAO.

        Regra: EM_PREPARACAO pode ir apenas para PRONTO
        """
        # Act
        proximos_estados = OrderStateManager.get_next_valid_states(
            StatusPedido.EM_PREPARACAO
        )

        # Assert
        assert proximos_estados == [StatusPedido.PRONTO]

    def test_get_next_valid_states_pronto(self):
        """
        Testa próximos estados válidos para PRONTO.

        Regra: PRONTO pode ir apenas para FINALIZADO
        """
        # Act
        proximos_estados = OrderStateManager.get_next_valid_states(StatusPedido.PRONTO)

        # Assert
        assert proximos_estados == [StatusPedido.FINALIZADO]

    def test_get_next_valid_states_finalizado(self):
        """
        Testa próximos estados válidos para FINALIZADO.

        Regra: FINALIZADO não pode ir para nenhum estado (terminal)
        """
        # Act
        proximos_estados = OrderStateManager.get_next_valid_states(
            StatusPedido.FINALIZADO
        )

        # Assert
        assert proximos_estados == []

    def test_should_update_from_payment_pago(self):
        """
        Testa se deve atualizar pedido quando pagamento é PAGO.

        Regra: Pagamento PAGO deve atualizar status do pedido
        """
        # Act
        deve_atualizar = OrderStateManager.should_update_from_payment(
            StatusPagamento.PAGO
        )

        # Assert
        assert deve_atualizar is True

    def test_should_not_update_from_payment_pendente(self):
        """
        Testa se NÃO deve atualizar pedido quando pagamento é PENDENTE.

        Regra: Pagamento PENDENTE não deve atualizar status do pedido
        """
        # Act
        deve_atualizar = OrderStateManager.should_update_from_payment(
            StatusPagamento.PENDENTE
        )

        # Assert
        assert deve_atualizar is False

    def test_should_not_update_from_payment_falhou(self):
        """
        Testa se NÃO deve atualizar pedido quando pagamento FALHOU.

        Regra: Pagamento FALHOU não deve atualizar status do pedido
        """
        # Act
        deve_atualizar = OrderStateManager.should_update_from_payment(
            StatusPagamento.FALHOU
        )

        # Assert
        assert deve_atualizar is False


class TestTimeUtilityHelpers:
    """Testes para funções auxiliares de tempo"""

    def test_get_estimated_time_minutes_recebido(self):
        """
        Testa tempo estimado em minutos para status RECEBIDO.

        Regra: RECEBIDO = 5 minutos
        """
        # Act
        tempo_minutos = get_estimated_time_minutes(StatusPedido.RECEBIDO)

        # Assert
        assert tempo_minutos == 5

    def test_get_estimated_time_minutes_em_preparacao(self):
        """
        Testa tempo estimado em minutos para status EM_PREPARACAO.

        Regra: EM_PREPARACAO = 15 minutos
        """
        # Act
        tempo_minutos = get_estimated_time_minutes(StatusPedido.EM_PREPARACAO)

        # Assert
        assert tempo_minutos == 15

    def test_get_estimated_time_minutes_pronto(self):
        """
        Testa tempo estimado em minutos para status PRONTO.

        Regra: PRONTO = 10 minutos
        """
        # Act
        tempo_minutos = get_estimated_time_minutes(StatusPedido.PRONTO)

        # Assert
        assert tempo_minutos == 10

    def test_get_estimated_time_minutes_finalizado(self):
        """
        Testa tempo estimado em minutos para status FINALIZADO.

        Regra: FINALIZADO = 0 minutos
        """
        # Act
        tempo_minutos = get_estimated_time_minutes(StatusPedido.FINALIZADO)

        # Assert
        assert tempo_minutos == 0

    def test_get_estimated_time_minutes_status_inexistente(self):
        """
        Testa tempo estimado para status não mapeado.

        Regra: Status não mapeado retorna 0 por padrão
        """
        # Act
        # Criando um status "fake" não mapeado
        tempo_minutos = get_estimated_time_minutes("STATUS_INEXISTENTE")

        # Assert
        assert tempo_minutos == 0


class TestFormatConversionHelpers:
    """Testes para funções auxiliares de conversão de formato"""

    def test_conversao_minutos_para_hh_mm_ss_menos_de_uma_hora(
        self, acompanhamento_service
    ):
        """
        Testa conversão de minutos para formato HH:MM:SS com tempo < 60 min.

        Verifica se função interna de conversão funciona corretamente
        """
        # Arrange
        from app.models.acompanhamento import ItemPedido

        acompanhamento = Acompanhamento(
            id_pedido=1,
            cpf_cliente="12345678901",
            status=StatusPedido.EM_PREPARACAO,  # 15 minutos
            status_pagamento=StatusPagamento.PAGO,
            itens=[ItemPedido(id_produto=1, quantidade=1)],
            tempo_estimado="00:15:00",
            atualizado_em=datetime.now(),
        )

        # Act
        tempo_formatado = acompanhamento_service.calcular_tempo_estimado(acompanhamento)

        # Assert
        assert tempo_formatado == "00:15:00"
        assert len(tempo_formatado.split(":")) == 3  # HH:MM:SS
        assert tempo_formatado.endswith(":00")  # Segundos sempre zero

    def test_conversao_minutos_para_hh_mm_ss_mais_de_uma_hora(
        self, acompanhamento_service
    ):
        """
        Testa conversão de minutos para formato HH:MM:SS com tempo > 60 min.

        Usando calcular_tempo_estimado_por_itens para gerar tempo > 60 min
        """
        # Arrange - Criando itens que resultam em mais de 60 minutos
        itens_tempo_longo = [
            {
                "id_produto": i,
                "quantidade": 3,
                "categoria": "LANCHE",
            }  # 3*5 = 15 min cada
            for i in range(1, 6)  # 5 produtos * 15 min = 75 min + 15 base = 90 min
        ]

        # Act
        tempo_formatado = acompanhamento_service.calcular_tempo_estimado_por_itens(
            itens_tempo_longo
        )

        # Assert
        assert tempo_formatado == "01:30:00"  # 90 minutos = 1h30min

        # Verifica formato
        partes = tempo_formatado.split(":")
        assert len(partes) == 3
        assert partes[0] == "01"  # 1 hora
        assert partes[1] == "30"  # 30 minutos
        assert partes[2] == "00"  # 0 segundos

    def test_conversao_zero_minutos(self, acompanhamento_service):
        """
        Testa conversão de 0 minutos para formato HH:MM:SS.

        Verifica edge case de tempo zero
        """
        # Arrange
        from app.models.acompanhamento import ItemPedido

        acompanhamento = Acompanhamento(
            id_pedido=1,
            cpf_cliente="12345678901",
            status=StatusPedido.FINALIZADO,  # 0 minutos
            status_pagamento=StatusPagamento.PAGO,
            itens=[ItemPedido(id_produto=1, quantidade=1)],
            tempo_estimado="00:00:00",
            atualizado_em=datetime.now(),
        )

        # Act
        tempo_formatado = acompanhamento_service.calcular_tempo_estimado(acompanhamento)

        # Assert
        assert tempo_formatado == "00:00:00"
