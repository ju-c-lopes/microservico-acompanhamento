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
            try:
                event_type, data = adaptar_evento_generico(msg["Body"])

                if event_type == "pagamento_atualizado":
                    await service.processar_evento_pagamento(data)

                elif event_type == "pedido_criado":
                    await service.processar_evento_pedido(data)

                elif event_type == "pedido_status_atualizado":
                    await service.atualizar_status_pedido(
                        id_pedido=data["id_pedido"],
                        novo_status=data["status"],
                    )
                else:
                    print(f"⚠️ Evento ignorado: {event_type}")

                await sqs.delete_message(queue_url, msg["ReceiptHandle"])

            except Exception as e:
                print(f"❌ Erro ao processar mensagem da fila {tipo}: {e}")

        await asyncio.sleep(1)


async def main():
    tasks = [consumir_fila(queue_url, tipo) for queue_url, tipo in FILAS if queue_url]
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())
