import asyncio
from unittest.mock import AsyncMock, patch

import pytest

from app.worker import sqs_consumer


@pytest.mark.asyncio
async def test_consumir_fila_processa_e_deleta():
    mock_sqs = AsyncMock()
    # Simula uma mensagem na primeira chamada, depois lista vazia para sair do loop
    mock_sqs.receive_messages.side_effect = [
        [{"Body": '{"event_type": "teste", "data": {}}', "ReceiptHandle": "abc"}],
        [],
    ]
    mock_sqs.delete_message.return_value = None

    with patch("app.worker.sqs_consumer.get_sqs_client", return_value=mock_sqs):
        with patch("app.worker.sqs_consumer.AcompanhamentoService") as mock_service_cls:
            mock_service = AsyncMock()
            mock_service_cls.return_value = mock_service
            # Executa só um ciclo do loop
            task = asyncio.create_task(sqs_consumer.consumir_fila("url", "tipo"))
            await asyncio.sleep(0.1)  # Dá tempo para rodar o ciclo
            task.cancel()  # Cancela para não travar o teste
            try:
                await task
            except asyncio.CancelledError:
                pass
            mock_service.processar_evento.assert_called_once()
            mock_sqs.delete_message.assert_called_once()
