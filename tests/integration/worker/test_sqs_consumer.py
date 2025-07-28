import asyncio
from unittest.mock import AsyncMock, patch

import pytest
from app.worker import sqs_consumer


@pytest.mark.asyncio
async def test_consumir_fila_processa_pagamento_e_deleta():
    mock_sqs = AsyncMock()
    mock_sqs.receive_messages.side_effect = [
        [{
            "Body": '''{
                "event_type": "pagamento_confirmado",
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
