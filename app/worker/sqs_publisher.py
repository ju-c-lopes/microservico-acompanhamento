"""
Exemplo de uso do envio de eventos para o SQS a partir do microserviço de acompanhamento.
Utilize este script para publicar eventos no padrão acordado.
"""

import asyncio
import json
import os

from app.core.sqs_client import get_sqs_client

# Exemplo de uso: python app/worker/sqs_publisher.py
# Certifique-se de definir a variável de ambiente ACOMPANHAMENTO_QUEUE_URL

ACOMPANHAMENTO_QUEUE_URL = os.getenv("ACOMPANHAMENTO_QUEUE_URL")


async def main():
    sqs = get_sqs_client()
    # Exemplo de evento
    evento = {
        "event_type": "acompanhamento_atualizado",
        "data": {
            "id_acompanhamento": 123,
            "status": "Pronto",
            "data_atualizacao": "2025-07-28T15:00:00",
        },
    }
    mensagem = json.dumps(evento)
    await sqs.send_message(ACOMPANHAMENTO_QUEUE_URL, mensagem)
    print("Evento publicado com sucesso!")


if __name__ == "__main__":
    asyncio.run(main())
