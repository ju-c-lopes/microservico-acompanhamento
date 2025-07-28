import pytest

from app.adapters.event_adapter import (
    adaptar_evento_generico,
    adaptar_evento_pagamento,
    adaptar_evento_pedido,
)


def test_adaptar_evento_generico_pagamento():
    msg = '{"event_type": "pagamento_confirmado", "data": {"id_pagamento": 1, "valor": 10.0}}'
    result = adaptar_evento_generico(msg)
    assert result["event_type"] == "pagamento_confirmado"
    assert result["data"]["id_pagamento"] == 1
    assert result["data"]["valor"] == 10.0


def test_adaptar_evento_generico_sem_data():
    msg = '{"event_type": "pagamento_confirmado"}'
    result = adaptar_evento_generico(msg)
    assert result["event_type"] == "pagamento_confirmado"
    assert result["data"] == {}


def test_adaptar_evento_generico_event_type_none():
    msg = '{"data": {"id_pagamento": 1}}'
    result = adaptar_evento_generico(msg)
    assert result["event_type"] is None
    assert result["data"]["id_pagamento"] == 1


def test_adaptar_evento_pagamento():
    msg = '{"event_type": "pagamento_confirmado", "data": {"id_pagamento": 2}}'
    result = adaptar_evento_pagamento(msg)
    assert result["id_pagamento"] == 2


def test_adaptar_evento_pagamento_sem_data():
    msg = '{"event_type": "pagamento_confirmado"}'
    result = adaptar_evento_pagamento(msg)
    assert result == {}


def test_adaptar_evento_pedido():
    msg = '{"event_type": "pedido_criado", "data": {"id_pedido": 3}}'
    result = adaptar_evento_pedido(msg)
    assert result["id_pedido"] == 3


def test_adaptar_evento_pedido_sem_data():
    msg = '{"event_type": "pedido_criado"}'
    result = adaptar_evento_pedido(msg)
    assert result == {}
