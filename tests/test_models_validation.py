from datetime import datetime, timedelta

import pytest
from pydantic import ValidationError

from app.domain.order_state import StatusPagamento, StatusPedido
from app.models.acompanhamento import (Acompanhamento, EventoPagamento,
                                       EventoPedido, ItemPedido)


class TestModelConstraintsAndValidators:
    """Test suite for model constraints and potential custom validators"""

    def test_item_pedido_business_constraints(self):
        """Test business constraints for ItemPedido"""
        # Test that quantities should be positive (business rule enforced)
        with pytest.raises(ValidationError) as exc_info:
            ItemPedido(id_produto=1, quantidade=0)
        assert "Quantity must be positive" in str(exc_info.value)

        # Test with negative quantity (should be rejected)
        with pytest.raises(ValidationError) as exc_info:
            ItemPedido(id_produto=1, quantidade=-5)
        assert "Quantity must be positive" in str(exc_info.value)

        # Test with very large quantities (should work)
        item = ItemPedido(id_produto=1, quantidade=1000000)
        assert item.quantidade == 1000000

    def test_cpf_format_validation(self):
        """Test CPF format validation (could be enhanced with custom validator)"""
        valid_cpfs = ["123.456.789-00", "12345678900", "000.000.000-00"]

        invalid_cpfs = [
            "123.456.789-0",  # Missing digit
            "123.456.789-000",  # Extra digit
            "abc.def.ghi-jk",  # Invalid characters
            "123-456-789-00",  # Wrong format
            "",  # Empty string
        ]

        sample_itens = [ItemPedido(id_produto=1, quantidade=1)]

        # Test valid CPFs (currently all pass)
        for cpf in valid_cpfs:
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

        # Test invalid CPFs (currently all pass - might need validation)
        for cpf in invalid_cpfs:
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

    def test_status_enum_validation(self):
        """Test status field validation using enums"""
        valid_order_statuses = [
            StatusPedido.RECEBIDO,
            StatusPedido.EM_PREPARACAO,
            StatusPedido.PRONTO,
            StatusPedido.FINALIZADO,
        ]
        invalid_order_statuses = ["cancelado", "em_pausa", "invalid_status"]

        sample_itens = [ItemPedido(id_produto=1, quantidade=1)]

        # Test valid statuses
        for status in valid_order_statuses:
            acompanhamento = Acompanhamento(
                id_pedido=1,
                cpf_cliente="123.456.789-00",
                status=status,
                status_pagamento=StatusPagamento.PAGO,
                itens=sample_itens,
                tempo_estimado="20 min",
                atualizado_em=datetime.now(),
            )
            assert acompanhamento.status == status

        # Test invalid statuses (should raise ValidationError)
        for status in invalid_order_statuses:
            with pytest.raises(ValidationError):
                Acompanhamento(
                    id_pedido=1,
                    cpf_cliente="123.456.789-00",
                    status=status,
                    status_pagamento=StatusPagamento.PAGO,
                    itens=sample_itens,
                    tempo_estimado="20 min",
                    atualizado_em=datetime.now(),
                )

    def test_payment_status_validation(self):
        """Test payment status validation"""
        valid_payment_statuses = ["pago", "pendente", "falhou"]
        invalid_payment_statuses = ["processando", "cancelado", "reembolsado"]

        # Test valid payment statuses
        for status in valid_payment_statuses:
            evento = EventoPagamento(
                id_pagamento=1, id_pedido=1, status=status, criado_em=datetime.now()
            )
            assert evento.status == status

        # Test invalid payment statuses (should raise ValidationError)
        for status in invalid_payment_statuses:
            with pytest.raises(ValidationError):
                EventoPagamento(
                    id_pagamento=1, id_pedido=1, status=status, criado_em=datetime.now()
                )

    def test_datetime_validation(self):
        """Test datetime validation constraints"""
        now = datetime.now()
        future_date = now + timedelta(days=1)
        past_date = now - timedelta(days=365)

        # Test with future date (might need validation for business logic)
        evento = EventoPagamento(
            id_pagamento=1,
            id_pedido=1,
            status=StatusPagamento.PAGO,
            criado_em=future_date,
        )
        assert evento.criado_em == future_date

        # Test with very old date
        evento = EventoPagamento(
            id_pagamento=1,
            id_pedido=1,
            status=StatusPagamento.PAGO,
            criado_em=past_date,
        )
        assert evento.criado_em == past_date

    def test_total_pedido_validation(self):
        """Test total_pedido validation constraints"""
        sample_itens = [ItemPedido(id_produto=1, quantidade=1)]

        # Test with zero total
        evento = EventoPedido(
            id_pedido=1,
            cpf_cliente="123.456.789-00",
            itens=sample_itens,
            total_pedido=0.0,
            tempo_estimado="30 min",
            status=StatusPedido.RECEBIDO,
            criado_em=datetime.now(),
        )
        assert evento.total_pedido == 0.0

        # Test with negative total (might need validation)
        evento = EventoPedido(
            id_pedido=1,
            cpf_cliente="123.456.789-00",
            itens=sample_itens,
            total_pedido=-10.50,
            tempo_estimado="30 min",
            status=StatusPedido.RECEBIDO,
            criado_em=datetime.now(),
        )
        assert evento.total_pedido == -10.50

        # Test with very large total
        evento = EventoPedido(
            id_pedido=1,
            cpf_cliente="123.456.789-00",
            itens=sample_itens,
            total_pedido=999999.99,
            tempo_estimado="30 min",
            status=StatusPedido.RECEBIDO,
            criado_em=datetime.now(),
        )
        assert evento.total_pedido == 999999.99

    def test_empty_itens_list(self):
        """Test validation of empty items list (should fail per business rules)"""
        # Test with empty items list - should raise ValidationError
        with pytest.raises(ValidationError) as exc_info:
            EventoPedido(
                id_pedido=1,
                cpf_cliente="123.456.789-00",
                itens=[],
                total_pedido=0.0,
                tempo_estimado="30 min",
                status=StatusPedido.RECEBIDO,
                criado_em=datetime.now(),
            )
        assert "Order must have at least one item" in str(exc_info.value)

        # Test Acompanhamento with empty items - should also fail
        with pytest.raises(ValidationError) as exc_info:
            Acompanhamento(
                id_pedido=1,
                cpf_cliente="123.456.789-00",
                status=StatusPedido.EM_PREPARACAO,
                status_pagamento=StatusPagamento.PAGO,
                itens=[],
                tempo_estimado="20 min",
                atualizado_em=datetime.now(),
            )
        assert "Order must have at least one item" in str(exc_info.value)

    def test_id_field_validation(self):
        """Test ID field validation"""
        # Test with zero IDs (should be rejected for ItemPedido per business rules)
        with pytest.raises(ValidationError) as exc_info:
            ItemPedido(id_produto=0, quantidade=1)
        assert "Product ID must be positive" in str(exc_info.value)

        # Test with negative IDs (might need validation for other models, but allowed for EventoPagamento)
        evento = EventoPagamento(
            id_pagamento=-1,
            id_pedido=-1,
            status=StatusPagamento.PAGO,
            criado_em=datetime.now(),
        )
        assert evento.id_pagamento == -1
        assert evento.id_pedido == -1

    def test_tempo_estimado_format(self):
        """Test tempo_estimado format validation"""
        sample_itens = [ItemPedido(id_produto=1, quantidade=1)]

        # Test various time formats
        time_formats = [
            "30 min",
            "1 hora",
            "2 horas",
            "45 minutos",
            "1h 30min",
            "Em breve",
            "Não disponível",
            "0 min",
            "999 min",
        ]

        for tempo in time_formats:
            acompanhamento = Acompanhamento(
                id_pedido=1,
                cpf_cliente="123.456.789-00",
                status=StatusPedido.EM_PREPARACAO,
                status_pagamento=StatusPagamento.PAGO,
                itens=sample_itens,
                tempo_estimado=tempo,
                atualizado_em=datetime.now(),
            )
            assert acompanhamento.tempo_estimado == tempo


class TestModelConsistency:
    """Test consistency between related models"""

    def test_evento_pedido_vs_acompanhamento_consistency(self):
        """Test consistency between EventoPedido and Acompanhamento"""
        # Create EventoPedido
        evento_pedido = EventoPedido(
            id_pedido=12345,
            cpf_cliente="123.456.789-00",
            itens=[ItemPedido(id_produto=1, quantidade=2)],
            total_pedido=59.90,
            tempo_estimado="30 min",
            status=StatusPedido.RECEBIDO,
            criado_em=datetime.now(),
        )

        # Create corresponding Acompanhamento
        acompanhamento = Acompanhamento(
            id_pedido=evento_pedido.id_pedido,
            cpf_cliente=evento_pedido.cpf_cliente,
            status=StatusPedido.EM_PREPARACAO,  # Status progressed
            status_pagamento=StatusPagamento.PAGO,
            itens=evento_pedido.itens,
            tempo_estimado="25 min",  # Time updated
            atualizado_em=datetime.now(),
        )

        # Verify consistency
        assert acompanhamento.id_pedido == evento_pedido.id_pedido
        assert acompanhamento.cpf_cliente == evento_pedido.cpf_cliente
        assert acompanhamento.itens == evento_pedido.itens

    def test_evento_pagamento_vs_acompanhamento_consistency(self):
        """Test consistency between EventoPagamento and Acompanhamento"""
        # Create EventoPagamento
        evento_pagamento = EventoPagamento(
            id_pagamento=999,
            id_pedido=12345,
            status=StatusPagamento.PAGO,
            criado_em=datetime.now(),
        )

        # Create corresponding Acompanhamento
        acompanhamento = Acompanhamento(
            id_pedido=evento_pagamento.id_pedido,
            cpf_cliente="123.456.789-00",
            status=StatusPedido.EM_PREPARACAO,
            status_pagamento=evento_pagamento.status,
            itens=[ItemPedido(id_produto=1, quantidade=1)],
            tempo_estimado="20 min",
            atualizado_em=datetime.now(),
        )

        # Verify consistency
        assert acompanhamento.id_pedido == evento_pagamento.id_pedido
        assert acompanhamento.status_pagamento == evento_pagamento.status

    def test_model_state_transitions(self):
        """Test logical state transitions"""
        sample_itens = [ItemPedido(id_produto=1, quantidade=1)]

        # Test order status progression
        status_progression = [
            StatusPedido.RECEBIDO,
            StatusPedido.EM_PREPARACAO,
            StatusPedido.PRONTO,
            StatusPedido.FINALIZADO,
        ]

        payment_progression = [
            StatusPagamento.PENDENTE,
            StatusPagamento.PAGO,
            StatusPagamento.PAGO,
            StatusPagamento.PAGO,
        ]

        for i, (order_status, payment_status) in enumerate(
            zip(status_progression, payment_progression)
        ):
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

    def test_business_rule_violations(self):
        """Test potential business rule violations"""
        sample_itens = [ItemPedido(id_produto=1, quantidade=1)]

        # Test potentially invalid combinations
        invalid_combinations = [
            (
                StatusPedido.FINALIZADO,
                StatusPagamento.PENDENTE,
            ),  # Delivered but not paid
            (
                StatusPedido.RECEBIDO,
                StatusPagamento.PAGO,
            ),  # Waiting payment but already paid
        ]

        for order_status, payment_status in invalid_combinations:
            # Currently these are allowed but might need validation
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


class TestModelExtensions:
    """Test potential model extensions and enhancements"""

    def test_model_with_additional_methods(self):
        """Test how models could be extended with additional methods"""
        # Example: ItemPedido could have a method to calculate line total
        item = ItemPedido(id_produto=1, quantidade=3)

        # If we had price information, we could add methods like:
        # def calculate_line_total(self, price_per_unit: float) -> float:
        #     return self.quantidade * price_per_unit

        # For now, just test the basic functionality
        assert item.quantidade == 3
        assert item.id_produto == 1

    def test_model_with_computed_properties(self):
        """Test how models could include computed properties"""
        evento = EventoPedido(
            id_pedido=1,
            cpf_cliente="123.456.789-00",
            itens=[
                ItemPedido(id_produto=1, quantidade=2),
                ItemPedido(id_produto=2, quantidade=1),
            ],
            total_pedido=59.90,
            tempo_estimado="30 min",
            status=StatusPedido.RECEBIDO,
            criado_em=datetime.now(),
        )

        # Example computed properties that could be added:
        # @property
        # def total_items(self) -> int:
        #     return sum(item.quantidade for item in self.itens)

        # @property
        # def unique_products(self) -> int:
        #     return len(set(item.id_produto for item in self.itens))

        # For now, test manual calculations
        total_items = sum(item.quantidade for item in evento.itens)
        unique_products = len(set(item.id_produto for item in evento.itens))

        assert total_items == 3
        assert unique_products == 2

    def test_model_validation_scenarios(self):
        """Test comprehensive validation scenarios"""
        # Test various edge cases that might need custom validation

        # 1. Test maximum string lengths
        long_cpf = "1" * 100  # Very long CPF

        # Test with valid enum instead of long status string
        acompanhamento = Acompanhamento(
            id_pedido=1,
            cpf_cliente=long_cpf,
            status=StatusPedido.RECEBIDO,  # Using valid enum
            status_pagamento=StatusPagamento.PAGO,
            itens=[ItemPedido(id_produto=1, quantidade=1)],
            tempo_estimado="20 min",
            atualizado_em=datetime.now(),
        )

        assert len(acompanhamento.cpf_cliente) == 100
        assert acompanhamento.status == StatusPedido.RECEBIDO

        # 2. Test special characters in fields
        special_chars_cpf = "123.456.789-00@#$%"

        acompanhamento = Acompanhamento(
            id_pedido=1,
            cpf_cliente=special_chars_cpf,
            status=StatusPedido.EM_PREPARACAO,  # Using valid enum
            status_pagamento=StatusPagamento.PAGO,
            itens=[ItemPedido(id_produto=1, quantidade=1)],
            tempo_estimado="20 min 🍕 com ❤️",  # Emojis can be in tempo_estimado field
            atualizado_em=datetime.now(),
        )

        assert "@#$%" in acompanhamento.cpf_cliente
        assert acompanhamento.status == StatusPedido.EM_PREPARACAO
        assert acompanhamento.tempo_estimado and "🍕" in acompanhamento.tempo_estimado
        assert acompanhamento.tempo_estimado and "❤️" in acompanhamento.tempo_estimado
