import pytest
from datetime import datetime
from app.adapters.event_adapter import adaptar_evento_generico
from app.models.acompanhamento import EventoPagamento, EventoPedido, ItemPedidoEvent
from app.domain.order_state import StatusPagamento, StatusPedido


def test_adaptar_evento_generico_pagamento():
    msg = '{"event_type": "pagamento_confirmado", "data": {"id_pagamento": 1, "id_pedido": 10, "status": "confirmado", "data_criacao": "2025-07-28T12:00:00"}}'
    tipo_evento, evento = adaptar_evento_generico(msg)

    assert tipo_evento == "pagamento_confirmado"
    assert isinstance(evento, EventoPagamento)
    assert evento.id_pagamento == 1
    assert evento.id_pedido == 10
    assert evento.status == StatusPagamento.CONFIRMADO
    assert evento.criado_em == datetime(2025, 7, 28, 12, 0, 0)


def test_adaptar_evento_generico_pedido():
    msg = '''
    {
        "event_type": "pedido_criado",
        "data": {
            "id_pedido": 123,
            "cliente": "12345678900",
            "produtos": [
                {"id": 1, "quantidade": 2, "preco": 10.0},
                {"id": 2, "preco": 5.0}
            ],
            "status": "recebido",
            "criado_em": "2025-07-28T10:30:00"
        }
    }
    '''
    tipo_evento, evento = adaptar_evento_generico(msg)

    assert tipo_evento == "pedido_criado"
    assert isinstance(evento, EventoPedido)
    assert evento.id_pedido == 123
    assert evento.cpf_cliente == "12345678900"
    assert len(evento.itens) == 2
    assert evento.itens[0] == ItemPedidoEvent(id_produto=1, quantidade=2)
    assert evento.itens[1] == ItemPedidoEvent(id_produto=2, quantidade=1)
    assert evento.total_pedido == 15.0
    assert evento.status == StatusPedido.RECEBIDO
    assert evento.criado_em == datetime(2025, 7, 28, 10, 30, 0)


def test_adaptar_evento_generico_pedido_status_atualizado():
    msg = '{"event_type": "pedido_status_atualizado", "data": {"id_pedido": 456, "status": "pronto", "atualizado_em": "2025-07-28T18:45:00"}}'
    tipo_evento, evento = adaptar_evento_generico(msg)

    assert tipo_evento == "pedido_status_atualizado"
    assert isinstance(evento, dict)
    assert evento["id_pedido"] == 456
    assert evento["status"] == StatusPedido.PRONTO
    assert evento["atualizado_em"] == datetime(2025, 7, 28, 18, 45, 0)


def test_adaptar_evento_generico_tipo_desconhecido():
    msg = '{"event_type": "evento_invalido", "data": {}}'
    with pytest.raises(ValueError, match="Tipo de evento desconhecido: evento_invalido"):
        adaptar_evento_generico(msg)
