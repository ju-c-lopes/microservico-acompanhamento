import asyncio
from unittest.mock import AsyncMock, patch

import pytest
from app.worker import sqs_consumer
from app.domain.order_state import StatusPedido


@pytest.mark.asyncio
async def test_consumir_fila_processa_pagamento_e_deleta():
    mock_sqs = AsyncMock()
    mock_sqs.receive_messages.side_effect = [
        [{
            "Body": '''{
                "event_type": "pagamento_atualizado",
                "data": {
                    "id_pagamento": 1,
                    "id_pedido": 10,
                    "status": "pago",
                    "data_criacao": "2025-07-28T12:00:00"
                }
            }''',
            "ReceiptHandle": "abc"
        }],
        []  # segunda chamada retorna vazio pra encerrar o loop
    ]
    mock_sqs.delete_message.return_value = None

    with patch("app.worker.sqs_consumer.get_sqs_client", return_value=mock_sqs):
        with patch("app.worker.sqs_consumer.AcompanhamentoService") as mock_service_cls:
            mock_service = AsyncMock()
            mock_service_cls.return_value = mock_service

            task = asyncio.create_task(sqs_consumer.consumir_fila("url", "pagamento"))
            await asyncio.sleep(0.1)
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

            mock_service.processar_evento_pagamento.assert_called_once()
            mock_sqs.delete_message.assert_called_once()

@pytest.mark.asyncio
async def test_consumir_fila_processa_pedido_criado():
    mock_sqs = AsyncMock()
    mock_sqs.receive_messages.side_effect = [
        [{
            "Body": '''{
                "event_type": "pedido_criado",
                "data": {
                    "id_pedido": 123,
                    "cliente": "12345678900",
                    "produtos": [
                        {"id": 1, "quantidade": 1, "preco": 10.0}
                    ],
                    "status": "Recebido",
                    "criado_em": "2025-07-28T10:00:00"
                }
            }''',
            "ReceiptHandle": "xyz"
        }],
        []
    ]
    mock_sqs.delete_message.return_value = None

    with patch("app.worker.sqs_consumer.get_sqs_client", return_value=mock_sqs):
        with patch("app.worker.sqs_consumer.AcompanhamentoService") as mock_service_cls:
            mock_service = AsyncMock()
            mock_service_cls.return_value = mock_service

            task = asyncio.create_task(sqs_consumer.consumir_fila("url", "pedido"))
            await asyncio.sleep(0.1)
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

            mock_service.processar_evento_pedido.assert_called_once()
            mock_sqs.delete_message.assert_called_once()


@pytest.mark.asyncio
async def test_consumir_fila_atualiza_status_pedido():
    mock_sqs = AsyncMock()
    mock_sqs.receive_messages.side_effect = [
        [{
            "Body": '''{
                "event_type": "pedido_status_atualizado",
                "data": {
                    "id_pedido": 456,
                    "status": "Pronto",
                    "atualizado_em": "2025-07-28T18:45:00"
                }
            }''',
            "ReceiptHandle": "aaa"
        }],
        []
    ]
    mock_sqs.delete_message.return_value = None

    with patch("app.worker.sqs_consumer.get_sqs_client", return_value=mock_sqs):
        with patch("app.worker.sqs_consumer.AcompanhamentoService") as mock_service_cls:
            mock_service = AsyncMock()
            mock_service_cls.return_value = mock_service

            task = asyncio.create_task(sqs_consumer.consumir_fila("url", "pedido"))
            await asyncio.sleep(0.1)
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

            mock_service.atualizar_status_pedido.assert_called_once_with(
                id_pedido=456,
                novo_status=StatusPedido.PRONTO
            )
            mock_sqs.delete_message.assert_called_once()