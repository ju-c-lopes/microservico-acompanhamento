from datetime import datetime

import pytest
from pydantic import ValidationError

from app.models.acompanhamento import (Acompanhamento, EventoPagamento,
                                       EventoPedido, ItemPedido)


class TestSchemaValidation:
    """Unit tests for schema validation and constraints"""

    def test_item_pedido_business_constraints(self):
        """Test ItemPedido business constraints"""
        # Valid item
        item = ItemPedido(id_produto=1, quantidade=1)
        assert item.id_produto == 1
        assert item.quantidade == 1

        # Test boundary values - id_produto and quantidade should not accept zero values according to business logic
        with pytest.raises(ValidationError) as exc_info:
            ItemPedido(id_produto=0, quantidade=1)
        assert "Product ID must be positive" in str(exc_info.value)

        with pytest.raises(ValidationError) as exc_info:
            ItemPedido(id_produto=1, quantidade=0)
        assert "Quantity must be positive" in str(exc_info.value)

        with pytest.raises(ValidationError) as exc_info:
            ItemPedido(id_produto=0, quantidade=0)
        assert "Product ID must be positive" in str(exc_info.value)

    def test_cpf_format_validation(self):
        """Test CPF format validation"""
        sample_itens = [ItemPedido(id_produto=1, quantidade=1)]

        # Test various CPF formats
        valid_cpfs = [
            "123.456.789-00",
            "12345678900",
            "000.000.000-00",
            "999.999.999-99",
        ]

        for cpf in valid_cpfs:
            acompanhamento = Acompanhamento(
                id_pedido=1,
                cpf_cliente=cpf,
                status="preparando",
                status_pagamento="pago",
                itens=sample_itens,
                tempo_estimado="20 min",
                atualizado_em=datetime.now(),
            )
            assert acompanhamento.cpf_cliente == cpf

    def test_status_enum_validation(self):
        """Test status field validation"""
        sample_itens = [ItemPedido(id_produto=1, quantidade=1)]

        # Test valid statuses
        valid_statuses = ["aguardando_pagamento", "preparando", "pronto", "entregue"]

        for status in valid_statuses:
            acompanhamento = Acompanhamento(
                id_pedido=1,
                cpf_cliente="123.456.789-00",
                status=status,
                status_pagamento="pago",
                itens=sample_itens,
                tempo_estimado="20 min",
                atualizado_em=datetime.now(),
            )
            assert acompanhamento.status == status

    def test_payment_status_validation(self):
        """Test payment status validation"""
        sample_itens = [ItemPedido(id_produto=1, quantidade=1)]

        # Test valid payment statuses
        valid_payment_statuses = ["pago", "pendente", "falhou"]

        for status_pagamento in valid_payment_statuses:
            acompanhamento = Acompanhamento(
                id_pedido=1,
                cpf_cliente="123.456.789-00",
                status="preparando",
                status_pagamento=status_pagamento,
                itens=sample_itens,
                tempo_estimado="20 min",
                atualizado_em=datetime.now(),
            )
            assert acompanhamento.status_pagamento == status_pagamento

    def test_datetime_validation(self):
        """Test datetime field validation"""
        sample_itens = [ItemPedido(id_produto=1, quantidade=1)]

        # Test with valid datetime
        valid_datetime = datetime(2024, 1, 15, 10, 30, 0)

        acompanhamento = Acompanhamento(
            id_pedido=1,
            cpf_cliente="123.456.789-00",
            status="preparando",
            status_pagamento="pago",
            itens=sample_itens,
            tempo_estimado="20 min",
            atualizado_em=valid_datetime,
        )
        assert acompanhamento.atualizado_em == valid_datetime

    def test_empty_itens_list(self):
        """Test empty items list validation - should not be allowed"""
        with pytest.raises(ValidationError):
            EventoPedido(
                id_pedido=1,
                cpf_cliente="123.456.789-00",
                itens=[],  # Empty list should not be allowed
                total_pedido=0.0,
                tempo_estimado="0 min",
                status="criado",
                criado_em=datetime.now(),
            )

    def test_id_field_validation(self):
        """Test ID field validation"""
        # Test various ID values
        valid_ids = [1, 999, 12345, 999999]

        for id_value in valid_ids:
            evento = EventoPagamento(
                id_pagamento=id_value,
                id_pedido=id_value,
                status="pago",
                criado_em=datetime.now(),
            )
            assert evento.id_pagamento == id_value
            assert evento.id_pedido == id_value

    def test_tempo_estimado_format(self):
        """Test tempo_estimado format validation"""
        sample_itens = [ItemPedido(id_produto=1, quantidade=1)]

        # Test various time formats
        valid_tempos = ["10 min", "30 minutes", "1 hour", "45 mins", "Ready now", None]

        for tempo in valid_tempos:
            acompanhamento = Acompanhamento(
                id_pedido=1,
                cpf_cliente="123.456.789-00",
                status="preparando",
                status_pagamento="pago",
                itens=sample_itens,
                tempo_estimado=tempo,
                atualizado_em=datetime.now(),
            )
            assert acompanhamento.tempo_estimado == tempo
