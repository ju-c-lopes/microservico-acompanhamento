"""
Adaptadores para eventos recebidos do SQS no padrão {"event_type": ..., "data": ...}.
Transformam o JSON da mensagem no formato esperado pelo domínio (modelos Pydantic).
"""

import json
from typing import Any, Dict

# Exemplo: importação dos modelos do domínio
# from app.models.evento_pagamento import EventoPagamentoModel
# from app.models.evento_pedido import EventoPedidoModel


def adaptar_evento_generico(msg_body: str) -> Dict[str, Any]:
    """
    Adapta qualquer evento no padrão {"event_type": ..., "data": ...} para um dicionário.
    Você pode usar o event_type para decidir qual modelo Pydantic instanciar.
    """
    evento = json.loads(msg_body)
    event_type = evento.get("event_type")
    data = evento.get("data", {})
    # Aqui você pode fazer lógica condicional para cada tipo de evento
    # Exemplo:
    # if event_type == "pagamento_confirmado":
    #     return EventoPagamentoModel(**data)
    # elif event_type == "pedido_criado":
    #     return EventoPedidoModel(**data)
    # else:
    #     raise ValueError(f"Tipo de evento não suportado: {event_type}")
    return {"event_type": event_type, "data": data}


# Você pode criar funções específicas para cada tipo de evento, se preferir


def adaptar_evento_pagamento(msg_body: str) -> Dict[str, Any]:
    evento = json.loads(msg_body)
    return evento.get("data", {})


def adaptar_evento_pedido(msg_body: str) -> Dict[str, Any]:
    evento = json.loads(msg_body)
    return evento.get("data", {})
