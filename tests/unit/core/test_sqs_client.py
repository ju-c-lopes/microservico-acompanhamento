from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.core.sqs_client import SQSClient


@pytest.mark.asyncio
async def test_send_message_calls_sqs():
    client = SQSClient()
    mock_sqs = AsyncMock()
    mock_cm = MagicMock()
    mock_cm.__aenter__.return_value = mock_sqs
    mock_cm.__aexit__.return_value = None
    with patch.object(client.session, "client", return_value=mock_cm):
        await client.send_message("url", "body")
        mock_sqs.send_message.assert_awaited_once()


@pytest.mark.asyncio
async def test_receive_messages_returns_list():
    client = SQSClient()
    mock_sqs = AsyncMock()
    mock_sqs.receive_message.return_value = {"Messages": [{"Body": "msg"}]}
    mock_cm = MagicMock()
    mock_cm.__aenter__.return_value = mock_sqs
    mock_cm.__aexit__.return_value = None
    with patch.object(client.session, "client", return_value=mock_cm):
        result = await client.receive_messages("url")
        assert isinstance(result, list)
        assert result[0]["Body"] == "msg"
