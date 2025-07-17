from datetime import datetime

import pytest

from app.models.acompanhamento import (Acompanhamento, EventoPagamento,
                                       EventoPedido, ItemPedido)
from app.models.events import EventoAcompanhamento


class TestModelConsistency:
    """Integration tests for model consistency and relationships"""

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

    def test_evento_pedido_vs_acompanhamento_consistency(
        self, sample_datetime, sample_itens
    ):
        """Test consistency between EventoPedido and Acompanhamento"""
        # Create EventoPedido
        evento_pedido = EventoPedido(
            id_pedido=12345,
            cpf_cliente="123.456.789-00",
            itens=sample_itens,
            total_pedido=59.90,
            tempo_estimado="30 min",
            status="criado",
            criado_em=sample_datetime,
        )

        # Create corresponding Acompanhamento
        acompanhamento = Acompanhamento(
            id_pedido=evento_pedido.id_pedido,
            cpf_cliente=evento_pedido.cpf_cliente,
            status="preparando",  # Status evolved from "criado"
            status_pagamento="pago",
            itens=evento_pedido.itens,
            tempo_estimado=evento_pedido.tempo_estimado,
            atualizado_em=sample_datetime,
        )

        # Verify consistency
        assert acompanhamento.id_pedido == evento_pedido.id_pedido
        assert acompanhamento.cpf_cliente == evento_pedido.cpf_cliente
        assert acompanhamento.itens == evento_pedido.itens
        assert acompanhamento.tempo_estimado == evento_pedido.tempo_estimado

    def test_evento_pagamento_vs_acompanhamento_consistency(
        self, sample_datetime, sample_itens
    ):
        """Test consistency between EventoPagamento and Acompanhamento"""
        # Create EventoPagamento
        evento_pagamento = EventoPagamento(
            id_pagamento=999, id_pedido=12345, status="pago", criado_em=sample_datetime
        )

        # Create corresponding Acompanhamento
        acompanhamento = Acompanhamento(
            id_pedido=evento_pagamento.id_pedido,
            cpf_cliente="123.456.789-00",
            status="preparando",
            status_pagamento=evento_pagamento.status,
            itens=sample_itens,
            tempo_estimado="25 min",
            atualizado_em=sample_datetime,
        )

        # Verify consistency
        assert acompanhamento.id_pedido == evento_pagamento.id_pedido
        assert acompanhamento.status_pagamento == evento_pagamento.status

    def test_model_state_transitions(self, sample_datetime, sample_itens):
        """Test model state transitions"""
        # Start with EventoPedido
        evento_pedido = EventoPedido(
            id_pedido=12345,
            cpf_cliente="123.456.789-00",
            itens=sample_itens,
            total_pedido=59.90,
            tempo_estimado="30 min",
            status="criado",
            criado_em=sample_datetime,
        )

        # Payment event
        evento_pagamento = EventoPagamento(
            id_pagamento=999,
            id_pedido=evento_pedido.id_pedido,
            status="pago",
            criado_em=sample_datetime,
        )

        # Final state in Acompanhamento
        acompanhamento = Acompanhamento(
            id_pedido=evento_pedido.id_pedido,
            cpf_cliente=evento_pedido.cpf_cliente,
            status="preparando",
            status_pagamento=evento_pagamento.status,
            itens=evento_pedido.itens,
            tempo_estimado="25 min",  # Updated time
            atualizado_em=sample_datetime,
        )

        # Verify the complete flow
        assert acompanhamento.id_pedido == evento_pedido.id_pedido
        assert acompanhamento.status_pagamento == evento_pagamento.status
        assert acompanhamento.status == "preparando"  # Status evolved

    def test_business_rule_violations(self, sample_datetime, sample_itens):
        """Test business rule violations across models"""
        # Business rule: Can't have "entregue" status with "pendente" payment
        acompanhamento = Acompanhamento(
            id_pedido=12345,
            cpf_cliente="123.456.789-00",
            status="entregue",
            status_pagamento="pendente",  # This violates business logic
            itens=sample_itens,
            tempo_estimado="0 min",
            atualizado_em=sample_datetime,
        )

        # This should be caught by business logic (not by Pydantic validation)
        assert acompanhamento.status == "entregue"
        assert acompanhamento.status_pagamento == "pendente"
        # In real application, this would be validated by business logic layer


class TestEventFlow:
    """Integration tests for event flow between models"""

    def test_complete_order_flow(self):
        """Test complete order flow from creation to delivery"""
        timestamp = datetime.now()

        # Step 1: Order created
        itens = [ItemPedido(id_produto=1, quantidade=2)]
        evento_pedido = EventoPedido(
            id_pedido=12345,
            cpf_cliente="123.456.789-00",
            itens=itens,
            total_pedido=29.90,
            tempo_estimado="30 min",
            status="criado",
            criado_em=timestamp,
        )

        # Step 2: Payment processed
        evento_pagamento = EventoPagamento(
            id_pagamento=999, id_pedido=12345, status="pago", criado_em=timestamp
        )

        # Step 3: Order status updates
        status_updates = ["preparando", "pronto", "entregue"]

        for status in status_updates:
            evento_acompanhamento = EventoAcompanhamento(
                id_pedido=12345,
                status=status,
                status_pagamento="pago",
                tempo_estimado="15 min" if status != "entregue" else None,
                atualizado_em=timestamp,
            )

            # Verify each status update
            assert evento_acompanhamento.id_pedido == evento_pedido.id_pedido
            assert evento_acompanhamento.status_pagamento == evento_pagamento.status
            assert evento_acompanhamento.status == status

    def test_order_with_multiple_items(self):
        """Test order with multiple items"""
        itens = [
            ItemPedido(id_produto=1, quantidade=2),
            ItemPedido(id_produto=2, quantidade=1),
            ItemPedido(id_produto=3, quantidade=3),
        ]

        evento_pedido = EventoPedido(
            id_pedido=12345,
            cpf_cliente="123.456.789-00",
            itens=itens,
            total_pedido=89.90,
            tempo_estimado="45 min",
            status="criado",
            criado_em=datetime.now(),
        )

        # Verify item count and details
        assert len(evento_pedido.itens) == 3
        assert evento_pedido.itens[0].id_produto == 1
        assert evento_pedido.itens[0].quantidade == 2
        assert evento_pedido.itens[2].quantidade == 3
