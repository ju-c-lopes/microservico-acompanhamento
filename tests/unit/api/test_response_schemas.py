"""
Testes unitários para schemas de RESPONSE da API de acompanhamento.
Foco em serialização, formatação de saída e estruturas de dados complexas.
"""

import json
from datetime import datetime

import pytest
from pydantic import ValidationError

from app.domain.order_state import StatusPagamento, StatusPedido
from app.schemas.acompanhamento_schemas import (
    AcompanhamentoResponse,
    AcompanhamentoResumoResponse,
    ErrorResponse,
    FilaPedidosResponse,
    HealthResponse,
    ItemPedidoResponse,
    SuccessResponse,
)


class TestItemPedidoResponse:
    """
    Testes para schema de response de item individual do pedido.

    Cobre:
    - Validação de campos obrigatórios
    - Tipos de dados corretos
    - Serialização JSON
    - Valores boundary
    """

    def test_criar_item_response_valido(self):
        """Testa criação de item response com dados válidos."""
        item = ItemPedidoResponse(id_produto=1, quantidade=2)

        assert item.id_produto == 1
        assert item.quantidade == 2
        assert isinstance(item.id_produto, int)
        assert isinstance(item.quantidade, int)

    def test_serialization_para_json(self):
        """Testa serialização para formato JSON."""
        item = ItemPedidoResponse(id_produto=123, quantidade=5)
        json_data = item.model_dump()

        expected = {"id_produto": 123, "quantidade": 5}
        assert json_data == expected
        assert isinstance(json_data, dict)

        # Verifica que pode ser convertido para JSON string
        json_string = json.dumps(json_data)
        assert '"id_produto"' in json_string and "123" in json_string

    def test_deserialization_de_json(self):
        """Testa deserialização a partir de dados JSON."""
        json_data = {"id_produto": 456, "quantidade": 3}
        item = ItemPedidoResponse(**json_data)

        assert item.id_produto == 456
        assert item.quantidade == 3

    def test_campos_obrigatorios_id_produto(self):
        """Testa que id_produto é obrigatório."""
        with pytest.raises(ValidationError) as exc_info:
            ItemPedidoResponse(quantidade=2)

        errors = exc_info.value.errors()
        assert any(
            error["loc"] == ("id_produto",) and error["type"] == "missing"
            for error in errors
        )

    def test_campos_obrigatorios_quantidade(self):
        """Testa que quantidade é obrigatório."""
        with pytest.raises(ValidationError) as exc_info:
            ItemPedidoResponse(id_produto=1)

        errors = exc_info.value.errors()
        assert any(
            error["loc"] == ("quantidade",) and error["type"] == "missing"
            for error in errors
        )

    def test_tipos_invalidos_id_produto(self):
        """Testa validação de tipos inválidos para id_produto."""
        tipos_invalidos = ["abc", [], {}, None, 1.5]

        for tipo_invalido in tipos_invalidos:
            with pytest.raises(ValidationError):
                ItemPedidoResponse(id_produto=tipo_invalido, quantidade=2)

    def test_tipos_invalidos_quantidade(self):
        """Testa validação de tipos inválidos para quantidade."""
        tipos_invalidos = ["xyz", [], {}, None, 2.7]

        for tipo_invalido in tipos_invalidos:
            with pytest.raises(ValidationError):
                ItemPedidoResponse(id_produto=1, quantidade=tipo_invalido)

    def test_valores_boundary_validos(self):
        """Testa valores de boundary válidos."""
        # Valores mínimos
        item_min = ItemPedidoResponse(id_produto=1, quantidade=1)
        assert item_min.id_produto == 1
        assert item_min.quantidade == 1

        # Valores grandes
        item_max = ItemPedidoResponse(id_produto=999999, quantidade=100)
        assert item_max.id_produto == 999999
        assert item_max.quantidade == 100

    def test_valores_boundary_invalidos(self):
        """Testa valores de boundary inválidos."""
        # Valores negativos ou zero podem ser inválidos dependendo da regra de negócio
        # Aqui assumimos que Pydantic aceita, mas a validação de negócio seria em outro lugar
        item_zero = ItemPedidoResponse(id_produto=0, quantidade=0)
        assert item_zero.id_produto == 0
        assert item_zero.quantidade == 0


class TestAcompanhamentoResponse:
    """
    Testes para schema de response completo do acompanhamento.

    Cobre:
    - Criação com todos os campos
    - Campos opcionais
    - Validação de relacionamentos
    - Serialização de estruturas complexas
    """

    @pytest.fixture
    def sample_itens(self):
        """Fixture com itens de exemplo para testes."""
        return [
            ItemPedidoResponse(id_produto=1, quantidade=2),
            ItemPedidoResponse(id_produto=2, quantidade=1),
        ]

    @pytest.fixture
    def sample_datetime(self):
        """Fixture com datetime consistente para testes."""
        return datetime(2024, 1, 15, 10, 30, 0)

    def test_criar_response_completo_todos_campos(self, sample_itens, sample_datetime):
        """Testa criação de response com todos os campos preenchidos."""
        response = AcompanhamentoResponse(
            id_pedido=123,
            cpf_cliente="123.456.789-00",
            status=StatusPedido.EM_PREPARACAO,
            status_pagamento=StatusPagamento.PAGO,
            itens=sample_itens,
            valor_pago=25.50,
            tempo_estimado="00:15:00",
            atualizado_em=sample_datetime,
        )

        assert response.id_pedido == 123
        assert response.cpf_cliente == "123.456.789-00"
        assert response.status == StatusPedido.EM_PREPARACAO
        assert response.status_pagamento == StatusPagamento.PAGO
        assert len(response.itens) == 2
        assert response.valor_pago == pytest.approx(25.50)
        assert response.tempo_estimado == "00:15:00"
        assert response.atualizado_em == sample_datetime

    def test_criar_response_campos_opcionais_none(self, sample_itens, sample_datetime):
        """Testa criação com campos opcionais como None."""
        response = AcompanhamentoResponse(
            id_pedido=123,
            cpf_cliente="123.456.789-00",
            status=StatusPedido.RECEBIDO,
            status_pagamento=StatusPagamento.PENDENTE,
            itens=sample_itens,
            valor_pago=None,  # Opcional
            tempo_estimado=None,  # Opcional
            atualizado_em=sample_datetime,
        )

        assert response.valor_pago is None
        assert response.tempo_estimado is None
        assert response.id_pedido == 123  # Campos obrigatórios ainda funcionam

    def test_serialization_json_estrutura_completa(self, sample_itens, sample_datetime):
        """Testa serialização completa para JSON com estrutura verificada."""
        response = AcompanhamentoResponse(
            id_pedido=123,
            cpf_cliente="123.456.789-00",
            status=StatusPedido.PRONTO,
            status_pagamento=StatusPagamento.PAGO,
            itens=sample_itens,
            valor_pago=30.75,
            tempo_estimado="00:05:00",
            atualizado_em=sample_datetime,
        )

        json_data = response.model_dump()

        # Verifica presença de todas as chaves esperadas
        expected_keys = {
            "id_pedido",
            "cpf_cliente",
            "status",
            "status_pagamento",
            "itens",
            "valor_pago",
            "tempo_estimado",
            "atualizado_em",
        }
        assert set(json_data.keys()) == expected_keys

        # Verifica serialização correta dos enums
        assert json_data["status"] == "Pronto"
        assert json_data["status_pagamento"] == "pago"

        # Verifica serialização da lista de itens
        assert isinstance(json_data["itens"], list)
        assert len(json_data["itens"]) == 2
        assert json_data["itens"][0]["id_produto"] == 1
        assert json_data["itens"][0]["quantidade"] == 2

    def test_deserialization_de_json_completo(self, sample_datetime):
        """Testa deserialização completa a partir de JSON."""
        json_data = {
            "id_pedido": 456,
            "cpf_cliente": "987.654.321-00",
            "status": "Finalizado",
            "status_pagamento": "pago",
            "itens": [
                {"id_produto": 3, "quantidade": 1},
                {"id_produto": 4, "quantidade": 2},
            ],
            "valor_pago": 15.00,
            "tempo_estimado": "00:00:00",
            "atualizado_em": sample_datetime.isoformat(),
        }

        response = AcompanhamentoResponse(**json_data)

        assert response.id_pedido == 456
        assert response.cpf_cliente == "987.654.321-00"
        assert response.status == StatusPedido.FINALIZADO
        assert response.status_pagamento == StatusPagamento.PAGO
        assert len(response.itens) == 2
        assert response.itens[0].id_produto == 3
        assert response.itens[1].quantidade == 2
        assert response.valor_pago == pytest.approx(15.00)

    def test_campos_obrigatorios_sistematico(self, sample_itens, sample_datetime):
        """Testa sistematicamente todos os campos obrigatórios."""
        campos_obrigatorios = [
            "id_pedido",
            "cpf_cliente",
            "status",
            "status_pagamento",
            "itens",
            "atualizado_em",
        ]

        base_data = {
            "id_pedido": 123,
            "cpf_cliente": "123.456.789-00",
            "status": StatusPedido.RECEBIDO,
            "status_pagamento": StatusPagamento.PENDENTE,
            "itens": sample_itens,
            "atualizado_em": sample_datetime,
        }

        for campo in campos_obrigatorios:
            data_sem_campo = base_data.copy()
            del data_sem_campo[campo]

            with pytest.raises(ValidationError) as exc_info:
                AcompanhamentoResponse(**data_sem_campo)

            errors = exc_info.value.errors()
            assert any(
                error["loc"] == (campo,) and error["type"] == "missing"
                for error in errors
            ), f"Campo {campo} deveria ser obrigatório"

    def test_lista_itens_vazia_permitida(self, sample_datetime):
        """Testa que lista vazia de itens é permitida."""
        response = AcompanhamentoResponse(
            id_pedido=123,
            cpf_cliente="123.456.789-00",
            status=StatusPedido.RECEBIDO,
            status_pagamento=StatusPagamento.PENDENTE,
            itens=[],  # Lista vazia deve ser permitida
            atualizado_em=sample_datetime,
        )

        assert response.itens == []
        assert isinstance(response.itens, list)

    def test_diferentes_status_pedido(self, sample_itens, sample_datetime):
        """Testa todos os valores possíveis de status do pedido."""
        for status in StatusPedido:
            response = AcompanhamentoResponse(
                id_pedido=123,
                cpf_cliente="123.456.789-00",
                status=status,
                status_pagamento=StatusPagamento.PAGO,
                itens=sample_itens,
                atualizado_em=sample_datetime,
            )
            assert response.status == status

    def test_diferentes_status_pagamento(self, sample_itens, sample_datetime):
        """Testa todos os valores possíveis de status do pagamento."""
        for status_pagamento in StatusPagamento:
            response = AcompanhamentoResponse(
                id_pedido=123,
                cpf_cliente="123.456.789-00",
                status=StatusPedido.RECEBIDO,
                status_pagamento=status_pagamento,
                itens=sample_itens,
                atualizado_em=sample_datetime,
            )
            assert response.status_pagamento == status_pagamento


class TestAcompanhamentoResumoResponse:
    """
    Testes para schema de response resumido (sem itens detalhados).

    Cobre:
    - Campos essenciais apenas
    - Compatibilidade com response completo
    - Uso em listagens
    """

    def test_criar_resumo_todos_campos(self):
        """Testa criação de resumo com todos os campos."""
        atualizado_em = datetime(2024, 1, 15, 10, 30, 0)

        response = AcompanhamentoResumoResponse(
            id_pedido=123,
            cpf_cliente="123.456.789-00",
            status=StatusPedido.PRONTO,
            tempo_estimado="00:02:00",
            atualizado_em=atualizado_em,
        )

        assert response.id_pedido == 123
        assert response.cpf_cliente == "123.456.789-00"
        assert response.status == StatusPedido.PRONTO
        assert response.tempo_estimado == "00:02:00"
        assert response.atualizado_em == atualizado_em

    def test_tempo_estimado_opcional(self):
        """Testa que tempo_estimado é opcional no resumo."""
        response = AcompanhamentoResumoResponse(
            id_pedido=123,
            cpf_cliente="123.456.789-00",
            status=StatusPedido.EM_PREPARACAO,
            tempo_estimado=None,
            atualizado_em=datetime.now(),
        )

        assert response.tempo_estimado is None

    def test_serialization_json_resumo(self):
        """Testa serialização JSON do resumo."""
        response = AcompanhamentoResumoResponse(
            id_pedido=789,
            cpf_cliente="111.222.333-44",
            status=StatusPedido.FINALIZADO,
            tempo_estimado="ready",
            atualizado_em=datetime(2024, 1, 15, 12, 0, 0),
        )

        json_data = response.model_dump()

        assert json_data["id_pedido"] == 789
        assert json_data["status"] == "Finalizado"
        assert json_data["tempo_estimado"] == "ready"

        # Não deve ter campos do response completo
        assert "itens" not in json_data
        assert "valor_pago" not in json_data
        assert "status_pagamento" not in json_data

    def test_campos_obrigatorios_resumo(self):
        """Testa campos obrigatórios do resumo."""
        campos_obrigatorios = ["id_pedido", "cpf_cliente", "status", "atualizado_em"]

        base_data = {
            "id_pedido": 123,
            "cpf_cliente": "123.456.789-00",
            "status": StatusPedido.RECEBIDO,
            "atualizado_em": datetime.now(),
        }

        for campo in campos_obrigatorios:
            data_sem_campo = base_data.copy()
            del data_sem_campo[campo]

            with pytest.raises(ValidationError) as exc_info:
                AcompanhamentoResumoResponse(**data_sem_campo)

            errors = exc_info.value.errors()
            assert any(error["loc"] == (campo,) for error in errors)


class TestFilaPedidosResponse:
    """
    Testes para schema de response da fila de pedidos (lista + metadados).

    Cobre:
    - Lista de resumos
    - Metadados de paginação
    - Casos de borda (lista vazia)
    """

    @pytest.fixture
    def sample_pedidos_resumo(self):
        """Fixture com pedidos resumo para testes."""
        return [
            AcompanhamentoResumoResponse(
                id_pedido=1,
                cpf_cliente="111.111.111-11",
                status=StatusPedido.EM_PREPARACAO,
                tempo_estimado="00:10:00",
                atualizado_em=datetime.now(),
            ),
            AcompanhamentoResumoResponse(
                id_pedido=2,
                cpf_cliente="222.222.222-22",
                status=StatusPedido.PRONTO,
                tempo_estimado="ready",
                atualizado_em=datetime.now(),
            ),
        ]

    def test_criar_fila_com_pedidos(self, sample_pedidos_resumo):
        """Testa criação de fila com pedidos."""
        response = FilaPedidosResponse(
            pedidos=sample_pedidos_resumo,
            total=len(sample_pedidos_resumo),
        )

        assert len(response.pedidos) == 2
        assert response.total == 2
        assert response.pedidos[0].id_pedido == 1
        assert response.pedidos[1].id_pedido == 2

    def test_fila_vazia(self):
        """Testa fila vazia."""
        response = FilaPedidosResponse(
            pedidos=[],
            total=0,
        )

        assert response.pedidos == []
        assert response.total == 0
        assert isinstance(response.pedidos, list)

    def test_serialization_json_fila(self, sample_pedidos_resumo):
        """Testa serialização JSON da fila."""
        response = FilaPedidosResponse(
            pedidos=sample_pedidos_resumo,
            total=2,
        )

        json_data = response.model_dump()

        assert "pedidos" in json_data
        assert "total" in json_data
        assert isinstance(json_data["pedidos"], list)
        assert json_data["total"] == 2
        assert len(json_data["pedidos"]) == 2

        # Verifica estrutura dos pedidos na lista
        primeiro_pedido = json_data["pedidos"][0]
        assert "id_pedido" in primeiro_pedido
        assert "status" in primeiro_pedido

    def test_inconsistencia_total_lista_permitida(self, sample_pedidos_resumo):
        """Testa que inconsistência entre total e tamanho da lista é permitida."""
        # Esta pode ser uma decisão de design - permitir inconsistência
        # para casos como paginação onde total != len(pedidos)
        response = FilaPedidosResponse(
            pedidos=sample_pedidos_resumo,  # 2 itens
            total=10,  # Total maior (ex: total geral, página tem apenas 2)
        )

        assert len(response.pedidos) == 2
        assert response.total == 10

    def test_campos_obrigatorios_fila(self):
        """Testa campos obrigatórios da fila."""
        # Faltando campo pedidos
        with pytest.raises(ValidationError) as exc_info:
            FilaPedidosResponse(total=0)

        errors = exc_info.value.errors()
        assert any(error["loc"] == ("pedidos",) for error in errors)

        # Faltando campo total
        with pytest.raises(ValidationError) as exc_info:
            FilaPedidosResponse(pedidos=[])

        errors = exc_info.value.errors()
        assert any(error["loc"] == ("total",) for error in errors)


class TestSuccessResponse:
    """
    Testes para schema de response de sucesso genérico.

    Cobre:
    - Mensagens de sucesso
    - Dados opcionais
    - Uso em operações CRUD
    """

    def test_criar_success_apenas_mensagem(self):
        """Testa criação com apenas mensagem."""
        response = SuccessResponse(message="Operação realizada com sucesso")

        assert response.message == "Operação realizada com sucesso"
        assert response.data is None

    def test_criar_success_com_dados(self):
        """Testa criação com dados adicionais."""
        data_adicional = {
            "id": 123,
            "status": "updated",
            "timestamp": "2024-01-15T10:30:00",
        }
        response = SuccessResponse(
            message="Status atualizado com sucesso",
            data=data_adicional,
        )

        assert response.message == "Status atualizado com sucesso"
        assert response.data == data_adicional
        assert response.data["id"] == 123

    def test_success_com_dados_complexos(self):
        """Testa success response com estrutura de dados complexa."""
        dados_complexos = {
            "pedido": {"id": 123, "status": "atualizado"},
            "timestamps": ["2024-01-15T10:30:00", "2024-01-15T10:31:00"],
            "metadata": {"user": "system", "version": "1.0"},
        }

        response = SuccessResponse(
            message="Processamento concluído",
            data=dados_complexos,
        )

        assert response.data["pedido"]["id"] == 123
        assert len(response.data["timestamps"]) == 2

    def test_serialization_json_success(self):
        """Testa serialização JSON do success response."""
        response = SuccessResponse(
            message="Teste realizado com sucesso",
            data={"teste": True, "resultado": "ok"},
        )

        json_data = response.model_dump()

        assert json_data["message"] == "Teste realizado com sucesso"
        assert json_data["data"]["teste"] is True
        assert json_data["data"]["resultado"] == "ok"

    def test_campo_message_obrigatorio(self):
        """Testa que message é campo obrigatório."""
        with pytest.raises(ValidationError) as exc_info:
            SuccessResponse()

        errors = exc_info.value.errors()
        assert any(
            error["loc"] == ("message",) and error["type"] == "missing"
            for error in errors
        )

    def test_data_tipos_diversos(self):
        """Testa que data aceita diferentes tipos de dados."""
        tipos_validos = [
            {"dict": "value"},
            {"lista_como_dict": ["lista", "de", "valores"]},  # Lista dentro de dict
            {"string": "string simples"},
            {"numero": 123},
            {"boolean": True},
            None,
        ]

        for tipo_valido in tipos_validos:
            response = SuccessResponse(
                message="Teste com tipo de data",
                data=tipo_valido,
            )
            assert response.data == tipo_valido


class TestErrorResponse:
    """
    Testes para schema de response de erro.

    Cobre:
    - Mensagens de erro
    - Códigos de erro opcionais
    - Compatibilidade com FastAPI HTTPException
    """

    def test_criar_error_apenas_detail(self):
        """Testa criação de erro apenas com detail."""
        response = ErrorResponse(detail="Erro de validação dos dados")

        assert response.detail == "Erro de validação dos dados"
        assert response.error_code is None

    def test_criar_error_com_codigo(self):
        """Testa criação com código de erro específico."""
        response = ErrorResponse(
            detail="CPF informado é inválido",
            error_code="INVALID_CPF",
        )

        assert response.detail == "CPF informado é inválido"
        assert response.error_code == "INVALID_CPF"

    def test_diferentes_tipos_erro(self):
        """Testa diferentes tipos de erro comuns."""
        erros_comuns = [
            ("Pedido não encontrado", "ORDER_NOT_FOUND"),
            ("Dados inválidos", "VALIDATION_ERROR"),
            ("Acesso negado", "ACCESS_DENIED"),
            ("Erro interno do servidor", "INTERNAL_ERROR"),
        ]

        for detail, error_code in erros_comuns:
            response = ErrorResponse(detail=detail, error_code=error_code)
            assert response.detail == detail
            assert response.error_code == error_code

    def test_serialization_json_error(self):
        """Testa serialização JSON do error response."""
        response = ErrorResponse(
            detail="Recurso não encontrado",
            error_code="RESOURCE_NOT_FOUND",
        )

        json_data = response.model_dump()

        assert json_data["detail"] == "Recurso não encontrado"
        assert json_data["error_code"] == "RESOURCE_NOT_FOUND"

    def test_campo_detail_obrigatorio(self):
        """Testa que detail é campo obrigatório."""
        with pytest.raises(ValidationError) as exc_info:
            ErrorResponse()

        errors = exc_info.value.errors()
        assert any(
            error["loc"] == ("detail",) and error["type"] == "missing"
            for error in errors
        )

    def test_error_code_opcional(self):
        """Testa que error_code é opcional."""
        response = ErrorResponse(detail="Erro sem código específico")

        json_data = response.model_dump()
        assert "detail" in json_data
        # error_code pode estar presente como None ou ausente
        assert json_data.get("error_code") is None


class TestHealthResponse:
    """
    Testes para schema de response de health check.

    Cobre:
    - Status de saúde do serviço
    - Informações de versão
    - Timestamp de verificação
    """

    def test_criar_health_completo(self):
        """Testa criação de health response completo."""
        timestamp = datetime(2024, 1, 15, 14, 30, 0)
        response = HealthResponse(
            status="healthy",
            service="acompanhamento",
            timestamp=timestamp,
            version="1.0.0",
        )

        assert response.status == "healthy"
        assert response.service == "acompanhamento"
        assert response.timestamp == timestamp
        assert response.version == "1.0.0"

    def test_diferentes_status_saude(self):
        """Testa diferentes status de saúde válidos."""
        status_validos = ["healthy", "unhealthy", "degraded", "starting", "maintenance"]

        for status in status_validos:
            response = HealthResponse(
                status=status,
                service="test-service",
                timestamp=datetime.now(),
                version="1.0.0",
            )
            assert response.status == status

    def test_diferentes_versoes(self):
        """Testa diferentes formatos de versão."""
        versoes_validas = ["1.0.0", "2.1.3-beta", "1.0.0-SNAPSHOT", "dev-branch"]

        for versao in versoes_validas:
            response = HealthResponse(
                status="healthy",
                service="acompanhamento",
                timestamp=datetime.now(),
                version=versao,
            )
            assert response.version == versao

    def test_serialization_json_health(self):
        """Testa serialização JSON do health response."""
        timestamp = datetime(2024, 1, 15, 14, 30, 0)
        response = HealthResponse(
            status="healthy",
            service="acompanhamento",
            timestamp=timestamp,
            version="2.1.0",
        )

        json_data = response.model_dump()

        assert json_data["status"] == "healthy"
        assert json_data["service"] == "acompanhamento"
        assert json_data["version"] == "2.1.0"
        assert "timestamp" in json_data

    def test_campos_obrigatorios_health(self):
        """Testa que todos os campos do health são obrigatórios."""
        campos_obrigatorios = ["status", "service", "timestamp", "version"]

        base_data = {
            "status": "healthy",
            "service": "test",
            "timestamp": datetime.now(),
            "version": "1.0.0",
        }

        for campo in campos_obrigatorios:
            data_sem_campo = base_data.copy()
            del data_sem_campo[campo]

            with pytest.raises(ValidationError) as exc_info:
                HealthResponse(**data_sem_campo)

            errors = exc_info.value.errors()
            assert any(
                error["loc"] == (campo,) and error["type"] == "missing"
                for error in errors
            )

    def test_timestamp_diferentes_formatos(self):
        """Testa diferentes formatos de timestamp."""
        # Timestamp atual
        response1 = HealthResponse(
            status="healthy",
            service="test",
            timestamp=datetime.now(),
            version="1.0.0",
        )
        assert isinstance(response1.timestamp, datetime)

        # Timestamp específico
        timestamp_especifico = datetime(2024, 12, 25, 0, 0, 0)
        response2 = HealthResponse(
            status="healthy",
            service="test",
            timestamp=timestamp_especifico,
            version="1.0.0",
        )
        assert response2.timestamp == timestamp_especifico


class TestResponseSchemaUtils:
    """
    Testes para funcionalidades utilitárias dos response schemas.
    """

    def test_schema_openapi_generation_responses(self):
        """Testa geração de schemas OpenAPI para responses."""
        schemas_para_testar = [
            AcompanhamentoResponse,
            SuccessResponse,
            ErrorResponse,
            HealthResponse,
        ]

        for schema_class in schemas_para_testar:
            schema = schema_class.model_json_schema()

            assert "type" in schema
            assert "properties" in schema
            assert "required" in schema

            # Verifica que tem documentação adequada
            assert "title" in schema or "description" in schema

    def test_performance_serialization_responses(self):
        """Testa performance de serialização de responses complexos."""
        import time

        # Cria response complexo com muitos itens
        many_items = [
            ItemPedidoResponse(id_produto=i, quantidade=1) for i in range(100)
        ]

        response = AcompanhamentoResponse(
            id_pedido=1,
            cpf_cliente="123.456.789-00",
            status=StatusPedido.EM_PREPARACAO,
            status_pagamento=StatusPagamento.PAGO,
            itens=many_items,
            atualizado_em=datetime.now(),
        )

        start_time = time.time()

        # Serializa múltiplas vezes
        for _ in range(100):
            json_data = response.model_dump()
            assert len(json_data["itens"]) == 100

        end_time = time.time()

        # Deve ser rápido (< 1 segundo para 100 serializações)
        assert end_time - start_time < 1.0
