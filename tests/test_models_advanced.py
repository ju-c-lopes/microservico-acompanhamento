import json
from datetime import datetime

import pytest
from pydantic import ValidationError

from app.models.acompanhamento import (Acompanhamento, EventoPagamento,
                                       EventoPedido, ItemPedido)


class TestModelValidation:
    """Advanced validation tests for all models"""

    def test_item_pedido_extreme_values(self):
        """Test ItemPedido with extreme values"""
        # Test maximum integer values
        max_int = 2147483647
        item = ItemPedido(id_produto=max_int, quantidade=max_int)
        assert item.id_produto == max_int
        assert item.quantidade == max_int

        # Test minimum values - but they must be positive according to business rules
        with pytest.raises(ValidationError) as exc_info:
            ItemPedido(id_produto=-2147483648, quantidade=1)
        assert "Product ID must be positive" in str(exc_info.value)

        with pytest.raises(ValidationError) as exc_info:
            ItemPedido(id_produto=1, quantidade=-2147483648)
        assert "Quantity must be positive" in str(exc_info.value)

    def test_evento_pedido_total_precision(self):
        """Test EventoPedido with high precision decimal values"""
        sample_itens = [ItemPedido(id_produto=1, quantidade=1)]

        # Test with high precision float
        evento = EventoPedido(
            id_pedido=1,
            cpf_cliente="123.456.789-00",
            itens=sample_itens,
            total_pedido=123.456789,
            tempo_estimado="30 min",
            status="criado",
            criado_em=datetime.now(),
        )
        assert evento.total_pedido == 123.456789

        # Test with zero value
        evento.total_pedido = 0.0
        assert evento.total_pedido == 0.0

    def test_status_field_empty_string(self):
        """Test models with empty string status"""
        # Test EventoPagamento with empty status
        evento_pagamento = EventoPagamento(
            id_pagamento=1, id_pedido=1, status="", criado_em=datetime.now()
        )
        assert evento_pagamento.status == ""

        # Test Acompanhamento with empty status
        acompanhamento = Acompanhamento(
            id_pedido=1,
            cpf_cliente="123.456.789-00",
            status="",
            status_pagamento="",
            itens=[ItemPedido(id_produto=1, quantidade=1)],
            tempo_estimado="20 min",
            atualizado_em=datetime.now(),
        )
        assert acompanhamento.status == ""
        assert acompanhamento.status_pagamento == ""

    def test_tempo_estimado_edge_cases(self):
        """Test tempo_estimado with various string formats"""
        sample_itens = [ItemPedido(id_produto=1, quantidade=1)]
        tempo_formats = [
            "0 min",
            "999 min",
            "1 hora",
            "2 horas e 30 min",
            "Não disponível",
            "Em breve",
            "",
        ]

        for tempo in tempo_formats:
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

    def test_cpf_field_validation(self):
        """Test CPF field with various formats and edge cases"""
        sample_itens = [ItemPedido(id_produto=1, quantidade=1)]

        # Test various CPF formats
        cpf_values = [
            "123.456.789-00",
            "12345678900",
            "000.000.000-00",
            "11111111111",
            "123456789",  # Invalid length
            "abc.def.ghi-jk",  # Invalid characters
            "",  # Empty string
        ]

        for cpf in cpf_values:
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


class TestModelSerialization:
    """Test serialization and deserialization of models"""

    def test_json_serialization_roundtrip(self):
        """Test JSON serialization and deserialization roundtrip"""
        # Create a complex model
        original_evento = EventoPedido(
            id_pedido=12345,
            cpf_cliente="123.456.789-00",
            itens=[
                ItemPedido(id_produto=1, quantidade=2),
                ItemPedido(id_produto=2, quantidade=1),
            ],
            total_pedido=59.90,
            tempo_estimado="30 min",
            status="criado",
            criado_em=datetime(2024, 1, 15, 10, 30, 0),
        )

        # Serialize to JSON
        json_data = original_evento.model_dump_json()

        # Deserialize from JSON
        dict_data = json.loads(json_data)
        reconstructed_evento = EventoPedido.model_validate(dict_data)

        # Verify they are equal
        assert original_evento == reconstructed_evento

    def test_model_copy_and_update(self):
        """Test model copy and update functionality"""
        original_item = ItemPedido(id_produto=1, quantidade=2)

        # Test copy
        copied_item = original_item.model_copy()
        assert copied_item == original_item
        assert copied_item is not original_item

        # Test copy with update
        updated_item = original_item.model_copy(update={"quantidade": 5})
        assert updated_item.id_produto == 1
        assert updated_item.quantidade == 5
        assert original_item.quantidade == 2  # Original unchanged

    def test_model_fields_info(self):
        """Test model fields information"""
        # Test ItemPedido fields
        item_fields = ItemPedido.model_fields
        assert "id_produto" in item_fields
        assert "quantidade" in item_fields

        # Test EventoPedido fields
        evento_fields = EventoPedido.model_fields
        expected_fields = {
            "id_pedido",
            "cpf_cliente",
            "itens",
            "total_pedido",
            "tempo_estimado",
            "status",
            "criado_em",
        }
        assert expected_fields.issubset(evento_fields.keys())

    def test_exclude_fields_in_serialization(self):
        """Test excluding fields during serialization"""
        acompanhamento = Acompanhamento(
            id_pedido=1,
            cpf_cliente="123.456.789-00",
            status="preparando",
            status_pagamento="pago",
            itens=[ItemPedido(id_produto=1, quantidade=1)],
            tempo_estimado="20 min",
            atualizado_em=datetime.now(),
        )

        # Exclude sensitive fields
        public_data = acompanhamento.model_dump(exclude={"cpf_cliente"})
        assert "cpf_cliente" not in public_data
        assert "id_pedido" in public_data
        assert "status" in public_data

    def test_include_only_specific_fields(self):
        """Test including only specific fields during serialization"""
        acompanhamento = Acompanhamento(
            id_pedido=1,
            cpf_cliente="123.456.789-00",
            status="preparando",
            status_pagamento="pago",
            itens=[ItemPedido(id_produto=1, quantidade=1)],
            tempo_estimado="20 min",
            atualizado_em=datetime.now(),
        )

        # Include only specific fields
        minimal_data = acompanhamento.model_dump(include={"id_pedido", "status"})
        assert len(minimal_data) == 2
        assert minimal_data["id_pedido"] == 1
        assert minimal_data["status"] == "preparando"


class TestModelPerformance:
    """Performance and stress tests for models"""

    def test_large_items_list_performance(self):
        """Test performance with large items list"""
        # Create a large list of items
        large_items_list = [
            ItemPedido(id_produto=i + 1, quantidade=i % 10 + 1) for i in range(1000)
        ]

        # Test EventoPedido with large items list
        evento = EventoPedido(
            id_pedido=1,
            cpf_cliente="123.456.789-00",
            itens=large_items_list,
            total_pedido=9999.99,
            tempo_estimado="60 min",
            status="criado",
            criado_em=datetime.now(),
        )

        assert len(evento.itens) == 1000
        assert evento.itens[0].id_produto == 1
        assert evento.itens[999].id_produto == 1000

    def test_model_validation_performance(self):
        """Test model validation performance"""
        # Create multiple models rapidly - start from 1 to avoid zero id_produto
        models = []
        for i in range(100):
            item = ItemPedido(id_produto=i + 1, quantidade=i % 5 + 1)
            models.append(item)

        assert len(models) == 100
        assert all(isinstance(model, ItemPedido) for model in models)

    def test_serialization_performance(self):
        """Test serialization performance with complex models"""
        # Create a complex model - start from 1 to avoid zero id_produto
        complex_evento = EventoPedido(
            id_pedido=1,
            cpf_cliente="123.456.789-00",
            itens=[ItemPedido(id_produto=i + 1, quantidade=1) for i in range(100)],
            total_pedido=999.99,
            tempo_estimado="45 min",
            status="criado",
            criado_em=datetime.now(),
        )

        # Test multiple serializations
        for _ in range(10):
            serialized = complex_evento.model_dump()
            assert len(serialized["itens"]) == 100


class TestModelConstraints:
    """Test model constraints and business logic"""

    def test_business_logic_status_transitions(self):
        """Test logical status transitions"""
        # Test valid status progression
        valid_transitions = [
            ("criado", "preparando"),
            ("preparando", "pronto"),
            ("pronto", "entregue"),
        ]

        sample_itens = [ItemPedido(id_produto=1, quantidade=1)]

        for from_status, to_status in valid_transitions:
            acompanhamento = Acompanhamento(
                id_pedido=1,
                cpf_cliente="123.456.789-00",
                status=from_status,
                status_pagamento="pago",
                itens=sample_itens,
                tempo_estimado="20 min",
                atualizado_em=datetime.now(),
            )

            # Update status
            updated = acompanhamento.model_copy(update={"status": to_status})
            assert updated.status == to_status

    def test_payment_status_logic(self):
        """Test payment status logic"""
        # Test that certain order statuses should correlate with payment status
        payment_order_correlations = [
            ("aguardando_pagamento", "pendente"),
            ("preparando", "pago"),
            ("pronto", "pago"),
            ("entregue", "pago"),
        ]

        sample_itens = [ItemPedido(id_produto=1, quantidade=1)]

        for order_status, payment_status in payment_order_correlations:
            acompanhamento = Acompanhamento(
                id_pedido=1,
                cpf_cliente="123.456.789-00",
                status=order_status,
                status_pagamento=payment_status,
                itens=sample_itens,
                tempo_estimado="20 min",
                atualizado_em=datetime.now(),
            )

            assert acompanhamento.status == order_status
            assert acompanhamento.status_pagamento == payment_status

    def test_total_calculation_consistency(self):
        """Test that total_pedido is consistent with items (if business logic requires)"""
        # This test demonstrates how you might validate business logic
        # In real application, you might want to calculate total from items

        items = [
            ItemPedido(id_produto=1, quantidade=2),  # Assume product 1 costs 10.00
            ItemPedido(id_produto=2, quantidade=1),  # Assume product 2 costs 15.00
        ]

        # If you had price data, you could validate:
        # expected_total = (2 * 10.00) + (1 * 15.00) = 35.00

        evento = EventoPedido(
            id_pedido=1,
            cpf_cliente="123.456.789-00",
            itens=items,
            total_pedido=35.00,  # This should match calculated total
            tempo_estimado="30 min",
            status="criado",
            criado_em=datetime.now(),
        )

        # Test passes if total is what we expect
        assert evento.total_pedido == 35.00
        assert len(evento.itens) == 2
        assert sum(item.quantidade for item in evento.itens) == 3
