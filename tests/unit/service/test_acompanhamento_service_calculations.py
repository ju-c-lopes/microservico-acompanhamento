"""
Testes específicos para cálculos do AcompanhamentoService.

Este módulo testa os algoritmos de cálculo de tempo estimado baseado em diferentes
categorias de produtos e regras de negócio específicas para estimativas.
"""

from typing import List

import pytest

from app.models.acompanhamento import ItemPedido


class TestAcompanhamentoServiceCalculations:
    """Testes para cálculos específicos do serviço de acompanhamento"""

    @pytest.fixture
    def itens_lanche_only(self) -> List[ItemPedido]:
        """Fixture com apenas itens de categoria LANCHE"""
        return [
            {"id_produto": 1, "quantidade": 1, "categoria": "LANCHE"},
            {"id_produto": 2, "quantidade": 2, "categoria": "LANCHE"},
        ]

    @pytest.fixture
    def itens_bebida_only(self) -> List[ItemPedido]:
        """Fixture com apenas itens de categoria BEBIDA"""
        return [
            {"id_produto": 10, "quantidade": 3, "categoria": "BEBIDA"},
            {"id_produto": 11, "quantidade": 1, "categoria": "BEBIDA"},
        ]

    @pytest.fixture
    def itens_acompanhamento_only(self) -> List[ItemPedido]:
        """Fixture com apenas itens de categoria ACOMPANHAMENTO"""
        return [
            {"id_produto": 20, "quantidade": 2, "categoria": "ACOMPANHAMENTO"},
            {"id_produto": 21, "quantidade": 1, "categoria": "ACOMPANHAMENTO"},
        ]

    @pytest.fixture
    def itens_sobremesa_only(self) -> List[ItemPedido]:
        """Fixture com apenas itens de categoria SOBREMESA"""
        return [
            {"id_produto": 30, "quantidade": 1, "categoria": "SOBREMESA"},
            {"id_produto": 31, "quantidade": 2, "categoria": "SOBREMESA"},
        ]

    @pytest.fixture
    def itens_mix_categorias(self) -> List[ItemPedido]:
        """Fixture com mix de diferentes categorias"""
        return [
            {"id_produto": 1, "quantidade": 1, "categoria": "LANCHE"},  # +5 min
            {"id_produto": 10, "quantidade": 2, "categoria": "BEBIDA"},  # +2 min (2x1)
            {
                "id_produto": 20,
                "quantidade": 1,
                "categoria": "ACOMPANHAMENTO",
            },  # +2 min
            {"id_produto": 30, "quantidade": 1, "categoria": "SOBREMESA"},  # +3 min
        ]

    @pytest.fixture
    def itens_categoria_desconhecida(self) -> List[ItemPedido]:
        """Fixture com categorias não mapeadas"""
        return [
            {"id_produto": 40, "quantidade": 1, "categoria": "CATEGORIA_NOVA"},
            {"id_produto": 41, "quantidade": 1, "categoria": ""},
            {"id_produto": 42, "quantidade": 1},  # Sem categoria
        ]

    def test_calcular_tempo_apenas_lanches(
        self, acompanhamento_service, itens_lanche_only
    ):
        """
        Testa cálculo com apenas itens de categoria LANCHE.

        Regra: LANCHE = +5 minutos por quantidade
        """
        # Act
        tempo_estimado = acompanhamento_service.calcular_tempo_estimado_por_itens(
            itens_lanche_only
        )

        # Assert
        # Tempo base (15 min) + LANCHE: (1*5) + (2*5) = 15 minutos = 30 minutos = "00:30:00"
        assert tempo_estimado == "00:30:00"

    def test_calcular_tempo_apenas_bebidas(
        self, acompanhamento_service, itens_bebida_only
    ):
        """
        Testa cálculo com apenas itens de categoria BEBIDA.

        Regra: BEBIDA = +1 minuto por quantidade
        """
        # Act
        tempo_estimado = acompanhamento_service.calcular_tempo_estimado_por_itens(
            itens_bebida_only
        )

        # Assert
        # Tempo base (15 min) + BEBIDA: (3*1) + (1*1) = 4 minutos = 19 minutos = "00:19:00"
        assert tempo_estimado == "00:19:00"

    def test_calcular_tempo_apenas_acompanhamentos(
        self, acompanhamento_service, itens_acompanhamento_only
    ):
        """
        Testa cálculo com apenas itens de categoria ACOMPANHAMENTO.

        Regra: ACOMPANHAMENTO = +2 minutos por quantidade
        """
        # Act
        tempo_estimado = acompanhamento_service.calcular_tempo_estimado_por_itens(
            itens_acompanhamento_only
        )

        # Assert
        # Tempo base (15 min) + ACOMPANHAMENTO: (2*2) + (1*2) = 6 minutos = 21 minutos = "00:21:00"
        assert tempo_estimado == "00:21:00"

    def test_calcular_tempo_apenas_sobremesas(
        self, acompanhamento_service, itens_sobremesa_only
    ):
        """
        Testa cálculo com apenas itens de categoria SOBREMESA.

        Regra: SOBREMESA = +3 minutos por quantidade
        """
        # Act
        tempo_estimado = acompanhamento_service.calcular_tempo_estimado_por_itens(
            itens_sobremesa_only
        )

        # Assert
        # Tempo base (15 min) + SOBREMESA: (1*3) + (2*3) = 9 minutos = 24 minutos = "00:24:00"
        assert tempo_estimado == "00:24:00"

    def test_calcular_tempo_mix_categorias(
        self, acompanhamento_service, itens_mix_categorias
    ):
        """
        Testa cálculo com mix de diferentes categorias.

        Regra: Soma tempo específico de cada categoria por quantidade
        """
        # Act
        tempo_estimado = acompanhamento_service.calcular_tempo_estimado_por_itens(
            itens_mix_categorias
        )

        # Assert
        # Tempo base: 15 min
        # + LANCHE: 1*5 = 5 min
        # + BEBIDA: 2*1 = 2 min
        # + ACOMPANHAMENTO: 1*2 = 2 min
        # + SOBREMESA: 1*3 = 3 min
        # Total: 15 + 5 + 2 + 2 + 3 = 27 minutos = "00:27:00"
        assert tempo_estimado == "00:27:00"

    def test_calcular_tempo_categorias_desconhecidas(
        self, acompanhamento_service, itens_categoria_desconhecida
    ):
        """
        Testa cálculo com categorias não mapeadas.

        Regra: Categoria desconhecida = +3 minutos (padrão)
        """
        # Act
        tempo_estimado = acompanhamento_service.calcular_tempo_estimado_por_itens(
            itens_categoria_desconhecida
        )

        # Assert
        # Tempo base (15 min) + 3 itens desconhecidos * 3 min (padrão) = 24 minutos = "00:24:00"
        assert tempo_estimado == "00:24:00"

    def test_calcular_tempo_lista_vazia(self, acompanhamento_service):
        """
        Testa cálculo com lista vazia de itens.

        Regra: Apenas tempo base deve ser retornado
        """
        # Act
        tempo_estimado = acompanhamento_service.calcular_tempo_estimado_por_itens([])

        # Assert
        # Apenas tempo base: 15 minutos = "00:15:00"
        assert tempo_estimado == "00:15:00"

    def test_calcular_tempo_quantidade_alta(self, acompanhamento_service):
        """
        Testa cálculo com quantidades altas de itens.

        Cenário: Pedido grande para validar escalonamento por quantidade
        """
        # Arrange
        itens_grande_quantidade = [
            {
                "id_produto": 1,
                "quantidade": 10,
                "categoria": "LANCHE",
            },  # 10*5 = +50 min
            {
                "id_produto": 2,
                "quantidade": 5,
                "categoria": "SOBREMESA",
            },  # 5*3 = +15 min
        ]

        # Act
        tempo_estimado = acompanhamento_service.calcular_tempo_estimado_por_itens(
            itens_grande_quantidade
        )

        # Assert
        # Tempo base (15 min) + LANCHE(50) + SOBREMESA(15) = 80 minutos = "01:20:00"
        assert tempo_estimado == "01:20:00"

    def test_calcular_tempo_case_insensitive_categorias(self, acompanhamento_service):
        """
        Testa se categorias em diferentes cases são tratadas corretamente.

        Regra: Categorias devem ser case-insensitive (convertidas para maiúscula)
        """
        # Arrange
        itens_mixed_case = [
            {"id_produto": 1, "quantidade": 1, "categoria": "lanche"},  # minúscula
            {"id_produto": 2, "quantidade": 1, "categoria": "Bebida"},  # título
            {
                "id_produto": 3,
                "quantidade": 1,
                "categoria": "ACOMPANHAMENTO",
            },  # maiúscula
        ]

        # Act
        tempo_estimado = acompanhamento_service.calcular_tempo_estimado_por_itens(
            itens_mixed_case
        )

        # Assert
        # Tempo base (15 min) + LANCHE(5) + BEBIDA(1) + ACOMPANHAMENTO(2) = 23 minutos = "00:23:00"
        assert tempo_estimado == "00:23:00"

    def test_calcular_tempo_formato_horas_minutos(self, acompanhamento_service):
        """
        Testa se o formato de saída está correto para tempos > 60 minutos.

        Regra: Formato HH:MM:SS sempre
        """
        # Arrange
        # Criando muitos produtos para ultrapassar 60 minutos
        itens_tempo_longo = [
            {
                "id_produto": i,
                "quantidade": 2,
                "categoria": "LANCHE",
            }  # 2*5 = +10 min cada
            for i in range(1, 11)  # 10 produtos * 10 min = 100 min + 15 base = 115 min
        ]

        # Act
        tempo_estimado = acompanhamento_service.calcular_tempo_estimado_por_itens(
            itens_tempo_longo
        )

        # Assert
        # Tempo base (15 min) + 10 produtos * (2 unidades * 5 min) = 115 minutos = "01:55:00"
        assert tempo_estimado == "01:55:00"

        # Verifica formato
        partes = tempo_estimado.split(":")
        assert len(partes) == 3  # HH:MM:SS
        assert len(partes[0]) == 2  # Sempre 2 dígitos para horas
        assert len(partes[1]) == 2  # Sempre 2 dígitos para minutos
        assert len(partes[2]) == 2  # Sempre 2 dígitos para segundos
        assert partes[2] == "00"  # Segundos sempre zero
