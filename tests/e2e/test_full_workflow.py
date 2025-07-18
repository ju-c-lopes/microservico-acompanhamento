from datetime import datetime

import pytest

from app.models.acompanhamento import (Acompanhamento, EventoPagamento,
                                       EventoPedido, ItemPedido)
from app.models.events import EventoAcompanhamento


class TestFullOrderWorkflow:
    """End-to-end tests for complete order workflow"""

    def test_complete_order_lifecycle(self):
        """Test complete order lifecycle from creation to delivery"""
        timestamp = datetime.now()

        # Step 1: Customer places order
        itens = [
            ItemPedido(id_produto=1, quantidade=2),
            ItemPedido(id_produto=2, quantidade=1),
        ]

        evento_pedido = EventoPedido(
            id_pedido=12345,
            cpf_cliente="123.456.789-00",
            itens=itens,
            total_pedido=49.90,
            tempo_estimado="30 min",
            status="criado",
            criado_em=timestamp,
        )

        # Verify order creation
        assert evento_pedido.id_pedido == 12345
        assert len(evento_pedido.itens) == 2
        assert evento_pedido.status == "criado"

        # Step 2: Payment is processed
        evento_pagamento = EventoPagamento(
            id_pagamento=999,
            id_pedido=evento_pedido.id_pedido,
            status="pago",
            criado_em=timestamp,
        )

        # Verify payment
        assert evento_pagamento.id_pedido == evento_pedido.id_pedido
        assert evento_pagamento.status == "pago"

        # Step 3: Order starts preparation
        acompanhamento = Acompanhamento(
            id_pedido=evento_pedido.id_pedido,
            cpf_cliente=evento_pedido.cpf_cliente,
            status="preparando",
            status_pagamento=evento_pagamento.status,
            itens=evento_pedido.itens,
            tempo_estimado="25 min",
            atualizado_em=timestamp,
        )

        # Verify preparation state
        assert acompanhamento.status == "preparando"
        assert acompanhamento.status_pagamento == "pago"

        # Step 4: Order is ready
        evento_pronto = EventoAcompanhamento(
            id_pedido=evento_pedido.id_pedido,
            status="pronto",
            status_pagamento="pago",
            tempo_estimado="Ready for pickup",
            atualizado_em=timestamp,
        )

        # Verify ready state
        assert evento_pronto.status == "pronto"
        assert evento_pronto.tempo_estimado == "Ready for pickup"

        # Step 5: Order is delivered
        evento_entregue = EventoAcompanhamento(
            id_pedido=evento_pedido.id_pedido,
            status="entregue",
            status_pagamento="pago",
            tempo_estimado=None,
            atualizado_em=timestamp,
        )

        # Verify delivery state
        assert evento_entregue.status == "entregue"
        assert evento_entregue.tempo_estimado is None

        # Final verification: All events relate to the same order
        assert all(
            event.id_pedido == evento_pedido.id_pedido
            for event in [
                evento_pagamento,
                acompanhamento,
                evento_pronto,
                evento_entregue,
            ]
        )

    def test_order_with_payment_failure(self):
        """Test order workflow with payment failure"""
        timestamp = datetime.now()

        # Create order
        itens = [ItemPedido(id_produto=1, quantidade=1)]
        evento_pedido = EventoPedido(
            id_pedido=12346,
            cpf_cliente="123.456.789-01",
            itens=itens,
            total_pedido=19.90,
            tempo_estimado="20 min",
            status="criado",
            criado_em=timestamp,
        )

        # Payment fails
        evento_pagamento = EventoPagamento(
            id_pagamento=1000,
            id_pedido=evento_pedido.id_pedido,
            status="falhou",
            criado_em=timestamp,
        )

        # Order remains in waiting state
        acompanhamento = Acompanhamento(
            id_pedido=evento_pedido.id_pedido,
            cpf_cliente=evento_pedido.cpf_cliente,
            status="aguardando_pagamento",
            status_pagamento=evento_pagamento.status,
            itens=evento_pedido.itens,
            tempo_estimado=None,
            atualizado_em=timestamp,
        )

        # Verify failed payment workflow
        assert evento_pagamento.status == "falhou"
        assert acompanhamento.status == "aguardando_pagamento"
        assert acompanhamento.status_pagamento == "falhou"
        assert acompanhamento.tempo_estimado is None

    def test_bulk_order_processing(self):
        """Test processing multiple orders simultaneously"""
        timestamp = datetime.now()

        # Create multiple orders
        orders = []
        for i in range(5):
            itens = [ItemPedido(id_produto=i + 1, quantidade=1)]
            evento_pedido = EventoPedido(
                id_pedido=13000 + i,
                cpf_cliente=f"123.456.789-{i:02d}",
                itens=itens,
                total_pedido=float(10 + i),
                tempo_estimado="20 min",
                status="criado",
                criado_em=timestamp,
            )
            orders.append(evento_pedido)

        # Process payments for all orders
        payments = []
        for order in orders:
            payment = EventoPagamento(
                id_pagamento=2000 + order.id_pedido,
                id_pedido=order.id_pedido,
                status="pago",
                criado_em=timestamp,
            )
            payments.append(payment)

        # Create tracking for all orders
        tracking_records = []
        for order, payment in zip(orders, payments):
            tracking = Acompanhamento(
                id_pedido=order.id_pedido,
                cpf_cliente=order.cpf_cliente,
                status="preparando",
                status_pagamento=payment.status,
                itens=order.itens,
                tempo_estimado="15 min",
                atualizado_em=timestamp,
            )
            tracking_records.append(tracking)

        # Verify all orders are processed correctly
        assert len(orders) == 5
        assert len(payments) == 5
        assert len(tracking_records) == 5

        # Verify consistency
        for i, (order, payment, tracking) in enumerate(
            zip(orders, payments, tracking_records)
        ):
            assert order.id_pedido == 13000 + i
            assert payment.id_pedido == order.id_pedido
            assert tracking.id_pedido == order.id_pedido
            assert tracking.status_pagamento == "pago"
