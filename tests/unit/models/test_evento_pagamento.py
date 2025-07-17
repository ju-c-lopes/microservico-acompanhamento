from datetime import datetime, timedelta

import pytest
from pydantic import ValidationError

from app.models.acompanhamento import EventoPagamento


class TestEventoPagamento:
    """Unit tests for EventoPagamento model"""

    @pytest.fixture
    def sample_datetime(self):
        """Sample datetime for testing"""
        return datetime(2024, 1, 15, 10, 30, 0)

    def test_create_valid_evento_pagamento(self, sample_datetime):
        """Test creating a valid EventoPagamento"""
        evento = EventoPagamento(
            id_pagamento=999, id_pedido=12345, status="pago", criado_em=sample_datetime
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
        # Missing id_pagamento
        with pytest.raises(ValidationError):
            EventoPagamento(id_pedido=12345, status="pago", criado_em=sample_datetime)

        # Missing id_pedido
        with pytest.raises(ValidationError):
            EventoPagamento(id_pagamento=999, status="pago", criado_em=sample_datetime)

        # Missing status
        with pytest.raises(ValidationError):
            EventoPagamento(
                id_pagamento=999, id_pedido=12345, criado_em=sample_datetime
            )

    def test_evento_pagamento_serialization(self, sample_datetime):
        """Test EventoPagamento serialization"""
        evento = EventoPagamento(
            id_pagamento=999, id_pedido=12345, status="pago", criado_em=sample_datetime
        )

        serialized = evento.model_dump()
        expected = {
            "id_pagamento": 999,
            "id_pedido": 12345,
            "status": "pago",
            "criado_em": sample_datetime,
        }
        assert serialized == expected

    def test_evento_pagamento_datetime_edge_cases(self):
        """Test EventoPagamento with datetime edge cases"""
        now = datetime.now()
        future_date = now + timedelta(days=1)
        past_date = now - timedelta(days=1)

        # Test with different datetime values
        evento = EventoPagamento(
            id_pagamento=1, id_pedido=1, status="pago", criado_em=future_date
        )
        assert evento.criado_em == future_date

        evento.criado_em = past_date
        assert evento.criado_em == past_date
