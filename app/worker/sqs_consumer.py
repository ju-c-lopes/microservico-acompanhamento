"""
Worker assíncrono para consumir eventos das filas SQS e processar no domínio.
Escuta múltiplas filas, usa adaptadores e chama o service.
"""

import asyncio
import os

from app.adapters.event_adapter import adaptar_evento_generico
from app.core.sqs_client import get_sqs_client
from app.domain.acompanhamento_service import AcompanhamentoService

# URLs das filas SQS (defina via variáveis de ambiente ou diretamente aqui)
PEDIDO_QUEUE_URL = os.getenv("PEDIDO_QUEUE_URL")
PAGAMENTO_QUEUE_URL = os.getenv("PAGAMENTO_QUEUE_URL")
PRODUTO_QUEUE_URL = os.getenv("PRODUTO_QUEUE_URL")

# Mapeamento fila -> tipo de evento (pode ser expandido)
FILAS = [
    (PEDIDO_QUEUE_URL, "pedido"),
    (PAGAMENTO_QUEUE_URL, "pagamento"),
    (PRODUTO_QUEUE_URL, "produto"),
]


async def consumir_fila(queue_url: str, tipo: str):
    sqs = get_sqs_client()
    service = AcompanhamentoService()
    while True:
        messages = await sqs.receive_messages(queue_url)
        for msg in messages:
            evento = adaptar_evento_generico(msg["Body"])
            # Aqui você pode rotear pelo event_type se quiser
            await service.processar_evento(evento)
            await sqs.delete_message(queue_url, msg["ReceiptHandle"])
        await asyncio.sleep(1)


async def main():
    tasks = [consumir_fila(queue_url, tipo) for queue_url, tipo in FILAS if queue_url]
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())
