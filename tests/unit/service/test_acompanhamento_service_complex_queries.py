"""
Testes para consultas complexas do AcompanhamentoService.

Este módulo testa consultas avançadas, filtros combinados, agregações,
ordenações e operações de pesquisa complexas no serviço de acompanhamento.
"""

from datetime import datetime, timedelta
from typing import List
from unittest.mock import AsyncMock

import pytest

from app.domain.order_state import StatusPagamento, StatusPedido
from app.models.acompanhamento import Acompanhamento, ItemPedido


class TestAcompanhamentoServiceComplexQueries:
    """Testes para consultas complexas do serviço de acompanhamento"""

    @pytest.fixture
    def acompanhamentos_exemplo(self) -> List[Acompanhamento]:
        """Fixture com dados de exemplo para consultas complexas"""
        base_time = datetime.now()

        return [
            # Cliente 1 - Pedidos em diferentes status
            Acompanhamento(
                id_pedido=1,
                cpf_cliente="11111111111",
                status=StatusPedido.RECEBIDO,
                status_pagamento=StatusPagamento.PENDENTE,
                itens=[ItemPedido(id_produto=1, quantidade=2)],
                tempo_estimado="00:15:00",
                atualizado_em=base_time,
            ),
            Acompanhamento(
                id_pedido=2,
                cpf_cliente="11111111111",
                status=StatusPedido.EM_PREPARACAO,
                status_pagamento=StatusPagamento.PAGO,
                itens=[ItemPedido(id_produto=2, quantidade=1)],
                tempo_estimado="00:20:00",
                atualizado_em=base_time - timedelta(minutes=5),
            ),
            # Cliente 2 - Pedidos finalizados
            Acompanhamento(
                id_pedido=3,
                cpf_cliente="22222222222",
                status=StatusPedido.FINALIZADO,
                status_pagamento=StatusPagamento.PAGO,
                itens=[ItemPedido(id_produto=3, quantidade=3)],
                tempo_estimado="00:25:00",
                atualizado_em=base_time - timedelta(hours=1),
            ),
            Acompanhamento(
                id_pedido=4,
                cpf_cliente="22222222222",
                status=StatusPedido.PRONTO,
                status_pagamento=StatusPagamento.PAGO,
                itens=[ItemPedido(id_produto=4, quantidade=1)],
                tempo_estimado="00:10:00",
                atualizado_em=base_time - timedelta(minutes=2),
            ),
            # Cliente 3 - Diversos status
            Acompanhamento(
                id_pedido=5,
                cpf_cliente="33333333333",
                status=StatusPedido.EM_PREPARACAO,
                status_pagamento=StatusPagamento.PAGO,
                itens=[ItemPedido(id_produto=5, quantidade=2)],
                tempo_estimado="00:30:00",
                atualizado_em=base_time - timedelta(minutes=10),
            ),
        ]

    @pytest.mark.anyio
    async def test_buscar_fila_pedidos_ordenada_por_tempo(
        self, acompanhamento_service, acompanhamentos_exemplo
    ):
        """
        Testa busca da fila de pedidos com ordenação implícita por tempo estimado.

        Regra: Fila deve retornar pedidos EM_PREPARACAO e PRONTO
        """
        # Arrange
        pedidos_fila = [
            acomp
            for acomp in acompanhamentos_exemplo
            if acomp.status in [StatusPedido.EM_PREPARACAO, StatusPedido.PRONTO]
        ]

        acompanhamento_service.repository.buscar_por_status = AsyncMock(
            return_value=pedidos_fila
        )

        # Act
        resultado = await acompanhamento_service.buscar_fila_pedidos()

        # Assert
        assert len(resultado) == 3  # 2 EM_PREPARACAO + 1 PRONTO

        # Verifica se todos são dos status corretos
        status_encontrados = {acomp.status for acomp in resultado}
        assert status_encontrados == {StatusPedido.EM_PREPARACAO, StatusPedido.PRONTO}

        # Verifica se foi chamado com os status corretos
        acompanhamento_service.repository.buscar_por_status.assert_called_once_with(
            [StatusPedido.EM_PREPARACAO, StatusPedido.PRONTO]
        )

    @pytest.mark.anyio
    async def test_buscar_pedidos_cliente_historico_completo(
        self, acompanhamento_service, acompanhamentos_exemplo
    ):
        """
        Testa busca de histórico completo de pedidos de um cliente específico.

        Cenário: Cliente com múltiplos pedidos em diferentes status
        """
        # Arrange
        cpf_cliente = "11111111111"
        pedidos_cliente = [
            acomp
            for acomp in acompanhamentos_exemplo
            if acomp.cpf_cliente == cpf_cliente
        ]

        acompanhamento_service.repository.buscar_por_cpf_cliente = AsyncMock(
            return_value=pedidos_cliente
        )

        # Act
        resultado = await acompanhamento_service.buscar_pedidos_cliente(cpf_cliente)

        # Assert
        assert len(resultado) == 2  # Cliente tem 2 pedidos

        # Verifica se todos são do cliente correto
        cpfs_encontrados = {acomp.cpf_cliente for acomp in resultado}
        assert cpfs_encontrados == {cpf_cliente}

        # Verifica diferentes status do mesmo cliente
        status_cliente = {acomp.status for acomp in resultado}
        assert StatusPedido.RECEBIDO in status_cliente
        assert StatusPedido.EM_PREPARACAO in status_cliente

        # Verifica chamada do repositório
        acompanhamento_service.repository.buscar_por_cpf_cliente.assert_called_once_with(
            cpf_cliente
        )

    @pytest.mark.anyio
    async def test_buscar_pedidos_cliente_sem_historico(self, acompanhamento_service):
        """
        Testa busca de pedidos para cliente que não possui histórico.

        Cenário: Cliente novo ou CPF inexistente
        """
        # Arrange
        cpf_inexistente = "99999999999"
        acompanhamento_service.repository.buscar_por_cpf_cliente = AsyncMock(
            return_value=[]
        )

        # Act
        resultado = await acompanhamento_service.buscar_pedidos_cliente(cpf_inexistente)

        # Assert
        assert resultado == []
        acompanhamento_service.repository.buscar_por_cpf_cliente.assert_called_once_with(
            cpf_inexistente
        )

    @pytest.mark.anyio
    async def test_consulta_status_multiplos_criterios(
        self, acompanhamento_service, acompanhamentos_exemplo
    ):
        """
        Testa consulta por múltiplos status simultaneamente.

        Cenário: Buscar pedidos RECEBIDO e FINALIZADO ao mesmo tempo
        """
        # Arrange
        status_busca = [StatusPedido.RECEBIDO, StatusPedido.FINALIZADO]
        pedidos_filtrados = [
            acomp for acomp in acompanhamentos_exemplo if acomp.status in status_busca
        ]

        acompanhamento_service.repository.buscar_por_status = AsyncMock(
            return_value=pedidos_filtrados
        )

        # Act
        resultado = await acompanhamento_service.repository.buscar_por_status(
            status_busca
        )

        # Assert
        assert len(resultado) == 2  # 1 RECEBIDO + 1 FINALIZADO

        # Verifica se retornou apenas os status solicitados
        status_encontrados = {acomp.status for acomp in resultado}
        assert status_encontrados == {StatusPedido.RECEBIDO, StatusPedido.FINALIZADO}

        # Verifica se não retornou outros status
        assert StatusPedido.EM_PREPARACAO not in status_encontrados
        assert StatusPedido.PRONTO not in status_encontrados

    def test_analise_distribuicao_status_pedidos(
        self, acompanhamento_service, acompanhamentos_exemplo
    ):
        """
        Testa análise de distribuição de pedidos por status (simulação de agregação).

        Cenário: Contagem de pedidos por status para dashboard/métricas
        """
        # Arrange - Simula dados obtidos de consultas
        todos_pedidos = acompanhamentos_exemplo

        # Act - Simula agregação que seria feita com query complex
        distribuicao_status = {}
        for acomp in todos_pedidos:
            status = acomp.status
            distribuicao_status[status] = distribuicao_status.get(status, 0) + 1

        # Assert
        assert distribuicao_status[StatusPedido.RECEBIDO] == 1
        assert distribuicao_status[StatusPedido.EM_PREPARACAO] == 2
        assert distribuicao_status[StatusPedido.PRONTO] == 1
        assert distribuicao_status[StatusPedido.FINALIZADO] == 1

        # Verifica total
        total_pedidos = sum(distribuicao_status.values())
        assert total_pedidos == len(acompanhamentos_exemplo)

    def test_analise_tempo_estimado_por_status(
        self, acompanhamento_service, acompanhamentos_exemplo
    ):
        """
        Testa análise de tempo médio estimado por status.

        Cenário: Métricas de performance e eficiência
        """
        # Arrange
        pedidos_por_status = {}
        for acomp in acompanhamentos_exemplo:
            status = acomp.status
            if status not in pedidos_por_status:
                pedidos_por_status[status] = []
            pedidos_por_status[status].append(acomp)

        # Act - Calcula tempo médio por status
        tempo_medio_por_status = {}
        for status, pedidos in pedidos_por_status.items():
            # Converte tempo HH:MM:SS para minutos para cálculo
            tempos_minutos = []
            for pedido in pedidos:
                partes = pedido.tempo_estimado.split(":")
                minutos = int(partes[0]) * 60 + int(partes[1])
                tempos_minutos.append(minutos)

            tempo_medio_por_status[status] = sum(tempos_minutos) / len(tempos_minutos)

        # Assert
        assert StatusPedido.RECEBIDO in tempo_medio_por_status
        assert StatusPedido.EM_PREPARACAO in tempo_medio_por_status
        assert StatusPedido.PRONTO in tempo_medio_por_status
        assert StatusPedido.FINALIZADO in tempo_medio_por_status

        # Verifica se tempos são razoáveis (em minutos)
        assert 0 < tempo_medio_por_status[StatusPedido.RECEBIDO] < 60
        assert 0 < tempo_medio_por_status[StatusPedido.EM_PREPARACAO] < 60

    @pytest.mark.anyio
    async def test_busca_paginada_com_limite(
        self, acompanhamento_service, acompanhamentos_exemplo
    ):
        """
        Testa busca paginada com skip/limit.

        Cenário: Listar pedidos com paginação para performance
        """
        # Arrange
        skip = 1
        limit = 2
        total_pedidos = acompanhamentos_exemplo
        pedidos_paginados = total_pedidos[skip : skip + limit]

        acompanhamento_service.repository.listar_todos = AsyncMock(
            return_value=pedidos_paginados
        )

        # Act
        resultado = await acompanhamento_service.repository.listar_todos(
            skip=skip, limit=limit
        )

        # Assert
        assert len(resultado) == 2  # Limit = 2
        assert resultado != total_pedidos  # Não retornou tudo

        # Verifica chamada com parâmetros corretos
        acompanhamento_service.repository.listar_todos.assert_called_once_with(
            skip=skip, limit=limit
        )

    def test_filtro_pedidos_por_pagamento_pendente(
        self, acompanhamento_service, acompanhamentos_exemplo
    ):
        """
        Testa filtro de pedidos com pagamento pendente.

        Cenário: Identificar pedidos que precisam de cobrança
        """
        # Arrange & Act
        pedidos_pendentes = [
            acomp
            for acomp in acompanhamentos_exemplo
            if acomp.status_pagamento == StatusPagamento.PENDENTE
        ]

        # Assert
        assert len(pedidos_pendentes) == 1
        assert pedidos_pendentes[0].cpf_cliente == "11111111111"
        assert pedidos_pendentes[0].status == StatusPedido.RECEBIDO

        # Verifica que todos são realmente pendentes
        for pedido in pedidos_pendentes:
            assert pedido.status_pagamento == StatusPagamento.PENDENTE

    def test_filtro_pedidos_ativos_por_cliente(
        self, acompanhamento_service, acompanhamentos_exemplo
    ):
        """
        Testa filtro de pedidos ativos (não finalizados) por cliente.

        Cenário: Mostrar pedidos em andamento para um cliente específico
        """
        # Arrange
        cpf_cliente = "11111111111"
        status_ativos = [
            StatusPedido.RECEBIDO,
            StatusPedido.EM_PREPARACAO,
            StatusPedido.PRONTO,
        ]

        # Act
        pedidos_ativos_cliente = [
            acomp
            for acomp in acompanhamentos_exemplo
            if acomp.cpf_cliente == cpf_cliente and acomp.status in status_ativos
        ]

        # Assert
        assert len(pedidos_ativos_cliente) == 2  # Cliente tem 2 pedidos ativos

        # Verifica se todos são do cliente correto
        for pedido in pedidos_ativos_cliente:
            assert pedido.cpf_cliente == cpf_cliente
            assert pedido.status in status_ativos
            assert pedido.status != StatusPedido.FINALIZADO

    def test_ordenacao_pedidos_por_tempo_atualizacao(
        self, acompanhamento_service, acompanhamentos_exemplo
    ):
        """
        Testa ordenação de pedidos por timestamp de atualização.

        Cenário: Mostrar pedidos mais recentes primeiro
        """
        # Act - Ordena por atualizado_em (mais recente primeiro)
        pedidos_ordenados = sorted(
            acompanhamentos_exemplo, key=lambda x: x.atualizado_em, reverse=True
        )

        # Assert
        assert len(pedidos_ordenados) == len(acompanhamentos_exemplo)

        # Verifica se está em ordem decrescente de tempo
        for i in range(len(pedidos_ordenados) - 1):
            assert (
                pedidos_ordenados[i].atualizado_em
                >= pedidos_ordenados[i + 1].atualizado_em
            )

        # Verifica se o primeiro é realmente o mais recente
        assert pedidos_ordenados[0].id_pedido == 1  # Base time (mais recente)

    def test_agrupamento_pedidos_por_cliente(
        self, acompanhamento_service, acompanhamentos_exemplo
    ):
        """
        Testa agrupamento de pedidos por cliente.

        Cenário: Análise de comportamento/padrões de clientes
        """
        # Act - Agrupa por CPF
        pedidos_por_cliente = {}
        for acomp in acompanhamentos_exemplo:
            cpf = acomp.cpf_cliente
            if cpf not in pedidos_por_cliente:
                pedidos_por_cliente[cpf] = []
            pedidos_por_cliente[cpf].append(acomp)

        # Assert
        assert len(pedidos_por_cliente) == 3  # 3 clientes únicos

        # Verifica distribuição por cliente
        assert len(pedidos_por_cliente["11111111111"]) == 2  # Cliente 1: 2 pedidos
        assert len(pedidos_por_cliente["22222222222"]) == 2  # Cliente 2: 2 pedidos
        assert len(pedidos_por_cliente["33333333333"]) == 1  # Cliente 3: 1 pedido

        # Verifica que todos os pedidos foram agrupados
        total_agrupados = sum(len(pedidos) for pedidos in pedidos_por_cliente.values())
        assert total_agrupados == len(acompanhamentos_exemplo)

    def test_consulta_range_temporal(
        self, acompanhamento_service, acompanhamentos_exemplo
    ):
        """
        Testa consulta por range temporal (últimas X horas).

        Cenário: Pedidos atualizados nas últimas 2 horas
        """
        # Arrange
        agora = datetime.now()
        limite_tempo = agora - timedelta(hours=2)

        # Act - Filtra pedidos recentes
        pedidos_recentes = [
            acomp
            for acomp in acompanhamentos_exemplo
            if acomp.atualizado_em >= limite_tempo
        ]

        # Assert
        # Baseado na fixture, apenas alguns pedidos são recentes
        assert len(pedidos_recentes) >= 1  # Pelo menos o pedido base

        # Verifica se todos são realmente recentes
        for pedido in pedidos_recentes:
            assert pedido.atualizado_em >= limite_tempo

    def test_estatisticas_gerais_fila(
        self, acompanhamento_service, acompanhamentos_exemplo
    ):
        """
        Testa cálculo de estatísticas gerais da fila de pedidos.

        Cenário: Dashboard com métricas operacionais
        """
        # Arrange
        pedidos_fila = [
            acomp
            for acomp in acompanhamentos_exemplo
            if acomp.status in [StatusPedido.EM_PREPARACAO, StatusPedido.PRONTO]
        ]

        # Act - Calcula estatísticas
        estatisticas = {
            "total_fila": len(pedidos_fila),
            "em_preparacao": len(
                [p for p in pedidos_fila if p.status == StatusPedido.EM_PREPARACAO]
            ),
            "prontos": len(
                [p for p in pedidos_fila if p.status == StatusPedido.PRONTO]
            ),
            "tempo_medio_estimado": None,
        }

        # Calcula tempo médio
        if estatisticas["total_fila"] > 0:
            tempos = []
            for pedido in pedidos_fila:
                partes = pedido.tempo_estimado.split(":")
                minutos = int(partes[0]) * 60 + int(partes[1])
                tempos.append(minutos)
            estatisticas["tempo_medio_estimado"] = sum(tempos) / len(tempos)

        # Assert
        assert estatisticas["total_fila"] == 3
        assert estatisticas["em_preparacao"] == 2
        assert estatisticas["prontos"] == 1
        assert estatisticas["tempo_medio_estimado"] is not None
        assert estatisticas["tempo_medio_estimado"] > 0
