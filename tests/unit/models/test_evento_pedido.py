from datetime import datetime, timedelta

import pytest
from pydantic import ValidationError

from app.models.acompanhamento import EventoPedido, ItemPedido


class TestEventoPedido:
    """Unit tests for EventoPedido model"""

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
            status="criado",
            criado_em=sample_datetime,
        )
        assert evento.id_pedido == 12345
        assert evento.cpf_cliente == "123.456.789-00"
        assert len(evento.itens) == 2
        assert abs(evento.total_pedido - 59.90) < 0.01
        assert evento.tempo_estimado == "30 min"
        assert evento.status == "criado"
        assert evento.criado_em == sample_datetime

    def test_evento_pedido_optional_tempo_estimado(self, sample_datetime, sample_itens):
        """Test EventoPedido with optional tempo_estimado as None"""
        evento = EventoPedido(
            id_pedido=12345,
            cpf_cliente="123.456.789-00",
            itens=sample_itens,
            total_pedido=59.90,
            tempo_estimado=None,
            status="criado",
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
                status="criado",
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
                status="criado",
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
            status="criado",
            criado_em=sample_datetime,
        )

        serialized = evento.model_dump()
        assert serialized["id_pedido"] == 12345
        assert serialized["cpf_cliente"] == "123.456.789-00"
        assert len(serialized["itens"]) == 2
        assert abs(serialized["total_pedido"] - 59.90) < 0.01
        assert serialized["tempo_estimado"] == "30 min"
        assert serialized["status"] == "criado"
        assert serialized["criado_em"] == sample_datetime

    def test_evento_pedido_datetime_edge_cases(self, sample_itens):
        """Test EventoPedido with datetime edge cases"""
        now = datetime.now()
        future_date = now + timedelta(days=1)
        past_date = now - timedelta(days=1)

        # Test with different datetime values
        evento = EventoPedido(
            id_pedido=1,
            cpf_cliente="123.456.789-00",
            itens=sample_itens,
            total_pedido=59.90,
            tempo_estimado="30 min",
            status="criado",
            criado_em=future_date,
        )
        assert evento.criado_em == future_date

        evento.criado_em = past_date
        assert evento.criado_em == past_date
