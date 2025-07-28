# app/adapters/event_adapter.py

from typing import Any, Dict, Tuple, Union
import json
from app.domain.models import EventoPagamento, EventoPedido
from app.domain.enums import StatusPagamento, StatusPedido
from datetime import datetime

def adaptar_evento_generico(body: str) -> Tuple[str, Union[EventoPagamento, EventoPedido, Dict[str, Any]]]:
    payload = json.loads(body)
    tipo_evento = payload.get("event_type")
    data = payload.get("data")

    if tipo_evento == "pagamento_confirmado":
        return tipo_evento, EventoPagamento(
            id_pagamento=data["id_pagamento"],
            id_pedido=int(data["id_pedido"]),
            status=StatusPagamento(data["status"]),
            criado_em=datetime.fromisoformat(data["data_criacao"]),
        )

    elif tipo_evento == "pedido_criado":
        return tipo_evento, EventoPedido(
            id_pedido=data["id_pedido"],
            cpf_cliente=data["cliente"],
            itens=[  # Isso depende do formato da lista
                ItemPedidoEvent(
                    id_produto=item["id"],
                    quantidade=item.get("quantidade", 1),  # default 1
                )
                for item in data["produtos"]
            ],
            total_pedido=sum(item["preco"] for item in data["produtos"]),
            tempo_estimado=None,
            status=StatusPedido(data["status"]),
            criado_em=datetime.fromisoformat(data["criado_em"]),
        )

    elif tipo_evento == "pedido_status_atualizado":
        return tipo_evento, {
            "id_pedido": int(data["id_pedido"]),
            "status": StatusPedido(data["status"]),
            "atualizado_em": datetime.fromisoformat(data["atualizado_em"]),
        }

    else:
        raise ValueError(f"Tipo de evento desconhecido: {tipo_evento}")
