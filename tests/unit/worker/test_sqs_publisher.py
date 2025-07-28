import pytest
from unittest.mock import AsyncMock, patch

import app.worker.sqs_publisher as sqs_publisher

@pytest.mark.asyncio
async def test_main_publisher(monkeypatch):
    mock_sqs = AsyncMock()
    monkeypatch.setenv("ACOMPANHAMENTO_QUEUE_URL", "fake-url")
    with patch("app.worker.sqs_publisher.get_sqs_client", return_value=mock_sqs):
        await sqs_publisher.main()
        mock_sqs.send_message.assert_awaited_once()