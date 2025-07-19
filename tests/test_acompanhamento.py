from datetime import datetime, timedelta

import pytest
from pydantic import ValidationError

from app.domain.order_state import StatusPagamento, StatusPedido
from app.models.acompanhamento import (Acompanhamento, EventoPagamento,
                                       EventoPedido, ItemPedido)
from app.models.events import EventoAcompanhamento


class TestItemPedido:
    """Test suite for ItemPedido model"""

    def test_create_valid_item_pedido(self):
        """Test creating a valid ItemPedido"""
        item = ItemPedido(id_produto=123, quantidade=2)
        assert item.id_produto == 123
        assert item.quantidade == 2

    def test_item_pedido_serialization(self):
        """Test ItemPedido serialization to dict"""
        item = ItemPedido(id_produto=456, quantidade=1)
        expected = {"id_produto": 456, "quantidade": 1}
        assert item.model_dump() == expected

    def test_item_pedido_from_dict(self):
        """Test creating ItemPedido from dictionary"""
        data = {"id_produto": 789, "quantidade": 5}
        item = ItemPedido.model_validate(data)
        assert item.id_produto == 789
        assert item.quantidade == 5

    def test_item_pedido_invalid_types(self):
        """Test ItemPedido with invalid data types"""
        with pytest.raises(ValidationError):
            ItemPedido(id_produto="invalid", quantidade=1)

        with pytest.raises(ValidationError):
            ItemPedido(id_produto=123, quantidade="invalid")

    def test_item_pedido_missing_required_fields(self):
        """Test ItemPedido with missing required fields"""
        with pytest.raises(ValidationError):
            ItemPedido(id_produto=123)

        with pytest.raises(ValidationError):
            ItemPedido(quantidade=1)

    def test_item_pedido_negative_values(self):
        """Test ItemPedido validation with negative values (should fail)"""
        # These should be validated according to business rules
        with pytest.raises(ValidationError) as exc_info:
            ItemPedido(id_produto=-1, quantidade=-5)
        assert "Product ID must be positive" in str(exc_info.value)

    def test_item_pedido_zero_quantity(self):
        """Test ItemPedido validation with zero quantity (should fail)"""
        with pytest.raises(ValidationError) as exc_info:
            ItemPedido(id_produto=123, quantidade=0)
        assert "Quantity must be positive" in str(exc_info.value)


class TestEventoPedido:
    """Test suite for EventoPedido model"""

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

    def test_create_valid_evento_pedido(self, sample_datetime, sample_itens):
        """Test creating a valid EventoPedido"""
        evento = EventoPedido(
            id_pedido=12345,
            cpf_cliente="123.456.789-00",
            itens=sample_itens,
            total_pedido=59.90,
            tempo_estimado="30 min",
            status=StatusPedido.RECEBIDO,
            criado_em=sample_datetime,
        )
        assert evento.id_pedido == 12345
        assert evento.cpf_cliente == "123.456.789-00"
        assert len(evento.itens) == 2
        assert evento.total_pedido == 59.90
        assert evento.tempo_estimado == "30 min"
        assert evento.status == StatusPedido.RECEBIDO
        assert evento.criado_em == sample_datetime

    def test_evento_pedido_optional_tempo_estimado(self, sample_datetime, sample_itens):
        """Test EventoPedido with optional tempo_estimado as None"""
        evento = EventoPedido(
            id_pedido=12345,
            cpf_cliente="123.456.789-00",
            itens=sample_itens,
            total_pedido=59.90,
            tempo_estimado=None,
            status=StatusPedido.RECEBIDO,
            criado_em=sample_datetime,
        )
        assert evento.tempo_estimado is None

    def test_evento_pedido_empty_itens_list(self, sample_datetime):
        """Test EventoPedido with empty items list - should not be allowed"""
        with pytest.raises(ValidationError):
            EventoPedido(
                id_pedido=12345,
                cpf_cliente="123.456.789-00",
                itens=[],  # Empty items list should not be allowed
                total_pedido=0.0,
                tempo_estimado=None,
                status=StatusPedido.RECEBIDO,
                criado_em=sample_datetime,
            )

    def test_evento_pedido_invalid_total_pedido(self, sample_datetime, sample_itens):
        """Test EventoPedido with invalid total_pedido"""
        with pytest.raises(ValidationError):
            EventoPedido(
                id_pedido=12345,
                cpf_cliente="123.456.789-00",
                itens=sample_itens,
                total_pedido="invalid",
                tempo_estimado="30 min",
                status=StatusPedido.RECEBIDO,
                criado_em=sample_datetime,
            )

    def test_evento_pedido_status_variations(self, sample_datetime, sample_itens):
        """Test EventoPedido with different status values"""
        valid_statuses = ["criado", "preparando", "pronto", "entregue"]

        for status in valid_statuses:
            evento = EventoPedido(
                id_pedido=12345,
                cpf_cliente="123.456.789-00",
                itens=sample_itens,
                total_pedido=59.90,
                tempo_estimado="30 min",
                status=status,
                criado_em=sample_datetime,
            )
            assert evento.status == status

    def test_evento_pedido_serialization(self, sample_datetime, sample_itens):
        """Test EventoPedido serialization"""
        evento = EventoPedido(
            id_pedido=12345,
            cpf_cliente="123.456.789-00",
            itens=sample_itens,
            total_pedido=59.90,
            tempo_estimado="30 min",
            status=StatusPedido.RECEBIDO,
            criado_em=sample_datetime,
        )

        serialized = evento.model_dump()
        assert serialized["id_pedido"] == 12345
        assert serialized["cpf_cliente"] == "123.456.789-00"
        assert len(serialized["itens"]) == 2
        assert serialized["total_pedido"] == 59.90
        assert serialized["tempo_estimado"] == "30 min"
        assert serialized["status"] == "Recebido"
        assert serialized["criado_em"] == sample_datetime


class TestEventoPagamento:
    """Test suite for EventoPagamento model"""

    @pytest.fixture
    def sample_datetime(self):
        """Sample datetime for testing"""
        return datetime(2024, 1, 15, 10, 30, 0)

    def test_create_valid_evento_pagamento(self, sample_datetime):
        """Test creating a valid EventoPagamento"""
        evento = EventoPagamento(
            id_pagamento=999,
            id_pedido=12345,
            status=StatusPagamento.PAGO,
            criado_em=sample_datetime,
        )
        assert evento.id_pagamento == 999
        assert evento.id_pedido == 12345
        assert evento.status == "pago"
        assert evento.criado_em == sample_datetime

    def test_evento_pagamento_status_variations(self, sample_datetime):
        """Test EventoPagamento with different status values"""
        valid_statuses = ["pago", "pendente", "falhou"]

        for status in valid_statuses:
            evento = EventoPagamento(
                id_pagamento=999,
                id_pedido=12345,
                status=status,
                criado_em=sample_datetime,
            )
            assert evento.status == status

    def test_evento_pagamento_missing_fields(self, sample_datetime):
        """Test EventoPagamento with missing required fields"""
        with pytest.raises(ValidationError):
            EventoPagamento(
                id_pedido=12345, status=StatusPagamento.PAGO, criado_em=sample_datetime
            )

    def test_evento_pagamento_serialization(self, sample_datetime):
        """Test EventoPagamento serialization"""
        evento = EventoPagamento(
            id_pagamento=999,
            id_pedido=12345,
            status=StatusPagamento.PAGO,
            criado_em=sample_datetime,
        )

        serialized = evento.model_dump()
        expected = {
            "id_pagamento": 999,
            "id_pedido": 12345,
            "status": "pago",
            "criado_em": sample_datetime,
        }
        assert serialized == expected


class TestAcompanhamento:
    """Test suite for Acompanhamento model"""

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
        assert serialized["status"] == StatusPedido.EM_PREPARACAO
        assert serialized["status_pagamento"] == "pago"
        assert len(serialized["itens"]) == 2
        assert serialized["tempo_estimado"] == "25 min"
        assert serialized["atualizado_em"] == sample_datetime


class TestEventoAcompanhamento:
    """Test suite for EventoAcompanhamento model from events.py"""

    @pytest.fixture
    def sample_datetime(self):
        """Sample datetime for testing"""
        return datetime(2024, 1, 15, 10, 30, 0)

    def test_create_valid_evento_acompanhamento(self, sample_datetime):
        """Test creating a valid EventoAcompanhamento"""
        evento = EventoAcompanhamento(
            id_pedido=12345,
            status=StatusPedido.EM_PREPARACAO,
            status_pagamento=StatusPagamento.PAGO,
            tempo_estimado="20 min",
            atualizado_em=sample_datetime,
        )
        assert evento.id_pedido == 12345
        assert evento.status == StatusPedido.EM_PREPARACAO
        assert evento.status_pagamento == "pago"
        assert evento.tempo_estimado == "20 min"
        assert evento.atualizado_em == sample_datetime

    def test_evento_acompanhamento_optional_tempo_estimado(self, sample_datetime):
        """Test EventoAcompanhamento with optional tempo_estimado as None"""
        evento = EventoAcompanhamento(
            id_pedido=12345,
            status=StatusPedido.EM_PREPARACAO,
            status_pagamento=StatusPagamento.PAGO,
            tempo_estimado=None,
            atualizado_em=sample_datetime,
        )
        assert evento.tempo_estimado is None

    def test_evento_acompanhamento_status_variations(self, sample_datetime):
        """Test EventoAcompanhamento with different status values"""
        valid_statuses = ["preparando", "pronto", "entregue"]

        for status in valid_statuses:
            evento = EventoAcompanhamento(
                id_pedido=12345,
                status=status,
                status_pagamento=StatusPagamento.PAGO,
                tempo_estimado="20 min",
                atualizado_em=sample_datetime,
            )
            assert evento.status == status

    def test_evento_acompanhamento_serialization(self, sample_datetime):
        """Test EventoAcompanhamento serialization"""
        evento = EventoAcompanhamento(
            id_pedido=12345,
            status=StatusPedido.EM_PREPARACAO,
            status_pagamento=StatusPagamento.PAGO,
            tempo_estimado="20 min",
            atualizado_em=sample_datetime,
        )

        serialized = evento.model_dump()
        expected = {
            "id_pedido": 12345,
            "status": "Em preparação",
            "status_pagamento": "pago",
            "tempo_estimado": "20 min",
            "atualizado_em": sample_datetime,
        }
        assert serialized == expected


# Integration and Edge Case Tests
class TestModelIntegration:
    """Integration tests and edge cases"""

    def test_datetime_edge_cases(self):
        """Test datetime edge cases"""
        now = datetime.now()
        future_date = now + timedelta(days=1)
        past_date = now - timedelta(days=1)

        # Test with different datetime values
        evento = EventoPagamento(
            id_pagamento=1,
            id_pedido=1,
            status=StatusPagamento.PAGO,
            criado_em=future_date,
        )
        assert evento.criado_em == future_date

        evento.criado_em = past_date
        assert evento.criado_em == past_date

    def test_cpf_format_variations(self):
        """Test different CPF formats"""
        cpf_formats = ["123.456.789-00", "12345678900", "000.000.000-00"]

        sample_itens = [ItemPedido(id_produto=1, quantidade=1)]

        for cpf in cpf_formats:
            acompanhamento = Acompanhamento(
                id_pedido=1,
                cpf_cliente=cpf,
                status=StatusPedido.EM_PREPARACAO,
                status_pagamento=StatusPagamento.PAGO,
                itens=sample_itens,
                tempo_estimado="20 min",
                atualizado_em=datetime.now(),
            )
            assert acompanhamento.cpf_cliente == cpf

    def test_large_item_quantities(self):
        """Test with large item quantities"""
        large_item = ItemPedido(id_produto=1, quantidade=1000000)
        assert large_item.quantidade == 1000000

    def test_unicode_status_fields(self):
        """Test unicode characters in status fields"""
        acompanhamento = Acompanhamento(
            id_pedido=1,
            cpf_cliente="123.456.789-00",
            status=StatusPedido.EM_PREPARACAO,  # Using valid enum
            status_pagamento=StatusPagamento.PAGO,  # Using valid enum
            itens=[ItemPedido(id_produto=1, quantidade=1)],
            tempo_estimado="20 min ⏰",  # Unicode allowed in tempo_estimado
            atualizado_em=datetime.now(),
        )
        # Test that enums work correctly
        assert acompanhamento.status == StatusPedido.EM_PREPARACAO
        assert acompanhamento.status_pagamento == StatusPagamento.PAGO
        assert acompanhamento.tempo_estimado and "⏰" in acompanhamento.tempo_estimado

    def test_model_equality(self):
        """Test model equality comparison"""
        item1 = ItemPedido(id_produto=1, quantidade=2)
        item2 = ItemPedido(id_produto=1, quantidade=2)
        item3 = ItemPedido(id_produto=2, quantidade=2)

        assert item1 == item2
        assert item1 != item3
