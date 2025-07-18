from datetime import datetime

import pytest
from pydantic import ValidationError

from app.models.events import EventoAcompanhamento


class TestEventoAcompanhamento:
    """Unit tests for EventoAcompanhamento model from events.py"""

    @pytest.fixture
    def sample_datetime(self):
        """Sample datetime for testing"""
        return datetime(2024, 1, 15, 10, 30, 0)

    def test_create_valid_evento_acompanhamento(self, sample_datetime):
        """Test creating a valid EventoAcompanhamento"""
        evento = EventoAcompanhamento(
            id_pedido=12345,
            status="preparando",
            status_pagamento="pago",
            tempo_estimado="20 min",
            atualizado_em=sample_datetime,
        )
        assert evento.id_pedido == 12345
        assert evento.status == "preparando"
        assert evento.status_pagamento == "pago"
        assert evento.tempo_estimado == "20 min"
        assert evento.atualizado_em == sample_datetime

    def test_evento_acompanhamento_optional_tempo_estimado(self, sample_datetime):
        """Test EventoAcompanhamento with optional tempo_estimado as None"""
        evento = EventoAcompanhamento(
            id_pedido=12345,
            status="preparando",
            status_pagamento="pago",
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
                status_pagamento="pago",
                tempo_estimado="20 min",
                atualizado_em=sample_datetime,
            )
            assert evento.status == status

    def test_evento_acompanhamento_serialization(self, sample_datetime):
        """Test EventoAcompanhamento serialization"""
        evento = EventoAcompanhamento(
            id_pedido=12345,
            status="preparando",
            status_pagamento="pago",
            tempo_estimado="20 min",
            atualizado_em=sample_datetime,
        )

        serialized = evento.model_dump()
        expected = {
            "id_pedido": 12345,
            "status": "preparando",
            "status_pagamento": "pago",
            "tempo_estimado": "20 min",
            "atualizado_em": sample_datetime,
        }
        assert serialized == expected
