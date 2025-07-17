from datetime import datetime

import pytest

from app.models.acompanhamento import Acompanhamento, ItemPedido


class TestAcompanhamento:
    """Unit tests for Acompanhamento model"""

    @pytest.fixture
    def sample_datetime(self):
        """Sample datetime for testing"""
        return datetime(2024, 1, 15, 10, 30, 0)

    @pytest.fixture
    def sample_itens(self):
        """Sample items for testing"""
        return [
            ItemPedido(id_produto=1, quantidade=2),
            ItemPedido(id_produto=2, quantidade=1),
        ]

    def test_create_valid_acompanhamento(self, sample_datetime, sample_itens):
        """Test creating a valid Acompanhamento"""
        acompanhamento = Acompanhamento(
            id_pedido=12345,
            cpf_cliente="123.456.789-00",
            status="preparando",
            status_pagamento="pago",
            itens=sample_itens,
            tempo_estimado="25 min",
            atualizado_em=sample_datetime,
        )
        assert acompanhamento.id_pedido == 12345
        assert acompanhamento.cpf_cliente == "123.456.789-00"
        assert acompanhamento.status == "preparando"
        assert acompanhamento.status_pagamento == "pago"
        assert len(acompanhamento.itens) == 2
        assert acompanhamento.tempo_estimado == "25 min"
        assert acompanhamento.atualizado_em == sample_datetime

    def test_acompanhamento_optional_tempo_estimado(
        self, sample_datetime, sample_itens
    ):
        """Test Acompanhamento with optional tempo_estimado as None"""
        acompanhamento = Acompanhamento(
            id_pedido=12345,
            cpf_cliente="123.456.789-00",
            status="preparando",
            status_pagamento="pago",
            itens=sample_itens,
            tempo_estimado=None,
            atualizado_em=sample_datetime,
        )
        assert acompanhamento.tempo_estimado is None

    def test_acompanhamento_status_combinations(self, sample_datetime, sample_itens):
        """Test Acompanhamento with different status combinations"""
        status_combinations = [
            ("aguardando_pagamento", "pendente"),
            ("preparando", "pago"),
            ("pronto", "pago"),
            ("entregue", "pago"),
        ]

        for status, status_pagamento in status_combinations:
            acompanhamento = Acompanhamento(
                id_pedido=12345,
                cpf_cliente="123.456.789-00",
                status=status,
                status_pagamento=status_pagamento,
                itens=sample_itens,
                tempo_estimado="25 min",
                atualizado_em=sample_datetime,
            )
            assert acompanhamento.status == status
            assert acompanhamento.status_pagamento == status_pagamento

    def test_acompanhamento_serialization(self, sample_datetime, sample_itens):
        """Test Acompanhamento serialization"""
        acompanhamento = Acompanhamento(
            id_pedido=12345,
            cpf_cliente="123.456.789-00",
            status="preparando",
            status_pagamento="pago",
            itens=sample_itens,
            tempo_estimado="25 min",
            atualizado_em=sample_datetime,
        )

        serialized = acompanhamento.model_dump()
        assert serialized["id_pedido"] == 12345
        assert serialized["cpf_cliente"] == "123.456.789-00"
        assert serialized["status"] == "preparando"
        assert serialized["status_pagamento"] == "pago"
        assert len(serialized["itens"]) == 2
        assert serialized["tempo_estimado"] == "25 min"
        assert serialized["atualizado_em"] == sample_datetime

    def test_acompanhamento_cpf_format_variations(self, sample_datetime, sample_itens):
        """Test Acompanhamento with different CPF formats"""
        cpf_formats = ["123.456.789-00", "12345678900", "000.000.000-00"]

        for cpf in cpf_formats:
            acompanhamento = Acompanhamento(
                id_pedido=1,
                cpf_cliente=cpf,
                status="preparando",
                status_pagamento="pago",
                itens=sample_itens,
                tempo_estimado="20 min",
                atualizado_em=sample_datetime,
            )
            assert acompanhamento.cpf_cliente == cpf
