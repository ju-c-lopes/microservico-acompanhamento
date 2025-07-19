from datetime import datetime

import pytest

from app.domain.order_state import StatusPagamento, StatusPedido
from app.models.acompanhamento import (
    Acompanhamento,
    EventoPagamento,
    EventoPedido,
    ItemPedido,
)


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
            status=StatusPedido.EM_PREPARACAO,
            status_pagamento=StatusPagamento.PAGO,
            itens=sample_itens,
            tempo_estimado="25 min",
            atualizado_em=sample_datetime,
        )
        assert acompanhamento.id_pedido == 12345
        assert acompanhamento.cpf_cliente == "123.456.789-00"
        assert acompanhamento.status == StatusPedido.EM_PREPARACAO
        assert acompanhamento.status_pagamento == StatusPagamento.PAGO
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
            status=StatusPedido.EM_PREPARACAO,
            status_pagamento=StatusPagamento.PAGO,
            itens=sample_itens,
            tempo_estimado=None,
            atualizado_em=sample_datetime,
        )
        assert acompanhamento.tempo_estimado is None

    def test_acompanhamento_status_combinations(self, sample_datetime, sample_itens):
        """Test Acompanhamento with different status combinations"""
        status_combinations = [
            (StatusPedido.RECEBIDO, StatusPagamento.PENDENTE),
            (StatusPedido.EM_PREPARACAO, StatusPagamento.PAGO),
            (StatusPedido.PRONTO, StatusPagamento.PAGO),
            (StatusPedido.FINALIZADO, StatusPagamento.PAGO),
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
            status=StatusPedido.EM_PREPARACAO,
            status_pagamento=StatusPagamento.PAGO,
            itens=sample_itens,
            tempo_estimado="25 min",
            atualizado_em=sample_datetime,
        )

        serialized = acompanhamento.model_dump()
        assert serialized["id_pedido"] == 12345
        assert serialized["cpf_cliente"] == "123.456.789-00"
        assert serialized["status"] == "Em preparação"  # Valor do enum
        assert serialized["status_pagamento"] == "pago"  # Valor do enum
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
                status=StatusPedido.EM_PREPARACAO,
                status_pagamento=StatusPagamento.PAGO,
                itens=sample_itens,
                tempo_estimado="20 min",
                atualizado_em=sample_datetime,
            )
            assert acompanhamento.cpf_cliente == cpf

    def test_acompanhamento_with_valor_pago(self, sample_datetime, sample_itens):
        """Test Acompanhamento with valor_pago field"""
        acompanhamento = Acompanhamento(
            id_pedido=1,
            cpf_cliente="12345678900",
            status=StatusPedido.EM_PREPARACAO,
            status_pagamento=StatusPagamento.PAGO,
            itens=sample_itens,
            valor_pago=25.50,
            tempo_estimado="20 min",
            atualizado_em=sample_datetime,
        )

        assert acompanhamento.valor_pago is not None
        assert abs(acompanhamento.valor_pago - 25.50) < 0.01

    def test_acompanhamento_valor_pago_optional(self, sample_datetime, sample_itens):
        """Test that valor_pago is optional"""
        acompanhamento = Acompanhamento(
            id_pedido=1,
            cpf_cliente="12345678900",
            status=StatusPedido.RECEBIDO,
            status_pagamento=StatusPagamento.PENDENTE,
            itens=sample_itens,
            tempo_estimado="20 min",
            atualizado_em=sample_datetime,
        )

        assert acompanhamento.valor_pago is None


class TestEventoPedido:
    """Unit tests for EventoPedido model"""

    @pytest.fixture
    def sample_itens(self):
        """Sample items for testing"""
        return [
            ItemPedido(id_produto=1, quantidade=2),
            ItemPedido(id_produto=2, quantidade=1),
        ]

    def test_create_valid_evento_pedido(self, sample_itens):
        """Test creating a valid EventoPedido"""
        evento = EventoPedido(
            id_pedido=123,
            cpf_cliente="12345678900",
            itens=sample_itens,
            total_pedido=25.50,
            tempo_estimado="00:15:00",
            status="criado",
            criado_em=datetime(2024, 1, 15, 10, 30, 0),
        )

        assert evento.id_pedido == 123
        assert evento.cpf_cliente == "12345678900"
        assert len(evento.itens) == 2
        assert abs(evento.total_pedido - 25.50) < 0.01
        assert evento.status == "criado"
        assert evento.tempo_estimado == "00:15:00"

    def test_evento_pedido_tempo_estimado_optional(self, sample_itens):
        """Test that tempo_estimado is optional in EventoPedido"""
        evento = EventoPedido(
            id_pedido=123,
            cpf_cliente="12345678900",
            itens=sample_itens,
            total_pedido=25.50,
            status="criado",
            criado_em=datetime.now(),
        )

        assert evento.tempo_estimado is None


class TestEventoPagamento:
    """Unit tests for EventoPagamento model"""

    def test_create_valid_evento_pagamento(self):
        """Test creating a valid EventoPagamento"""
        evento = EventoPagamento(
            id_pagamento=456,
            id_pedido=123,
            status=StatusPagamento.PAGO,
            criado_em=datetime(2024, 1, 15, 10, 35, 0),
        )

        assert evento.id_pagamento == 456
        assert evento.id_pedido == 123
        assert evento.status == StatusPagamento.PAGO

    def test_evento_pagamento_invalid_status(self):
        """Test that invalid status is rejected"""
        with pytest.raises(ValueError) as exc_info:
            EventoPagamento(
                id_pagamento=456,
                id_pedido=123,
                status="status_invalido",  # type: ignore # Status inválido para teste
                criado_em=datetime.now(),
            )

        assert "Input should be" in str(exc_info.value)


class TestEnumValidation:
    """Tests for enum validation in models"""

    @pytest.fixture
    def sample_itens(self):
        """Sample items for testing"""
        return [ItemPedido(id_produto=1, quantidade=2)]

    def test_acompanhamento_invalid_status_pedido(self, sample_itens):
        """Test that invalid StatusPedido is rejected"""
        with pytest.raises(ValueError) as exc_info:
            Acompanhamento(
                id_pedido=123,
                cpf_cliente="12345678900",
                status="status_invalido",  # type: ignore # Status inválido para teste
                status_pagamento=StatusPagamento.PAGO,
                itens=sample_itens,
                tempo_estimado="15 min",
                atualizado_em=datetime.now(),
            )

        assert "Input should be" in str(exc_info.value)
        assert "Recebido" in str(exc_info.value)

    def test_acompanhamento_invalid_status_pagamento(self, sample_itens):
        """Test that invalid StatusPagamento is rejected"""
        with pytest.raises(ValueError) as exc_info:
            Acompanhamento(
                id_pedido=123,
                cpf_cliente="12345678900",
                status=StatusPedido.RECEBIDO,
                status_pagamento="status_invalido",  # type: ignore # Status inválido para teste
                itens=sample_itens,
                tempo_estimado="15 min",
                atualizado_em=datetime.now(),
            )

        assert "Input should be" in str(exc_info.value)
        assert "pendente" in str(exc_info.value)

    def test_enum_values_serialization(self, sample_itens):
        """Test that enums serialize to their string values"""
        acompanhamento = Acompanhamento(
            id_pedido=123,
            cpf_cliente="12345678900",
            status=StatusPedido.PRONTO,
            status_pagamento=StatusPagamento.PAGO,
            itens=sample_itens,
            tempo_estimado="15 min",
            atualizado_em=datetime.now(),
        )

        serialized = acompanhamento.model_dump()

        # Os enums devem ser serializados como strings
        assert serialized["status"] == "Pronto"
        assert serialized["status_pagamento"] == "pago"
        assert isinstance(serialized["status"], str)
        assert isinstance(serialized["status_pagamento"], str)
