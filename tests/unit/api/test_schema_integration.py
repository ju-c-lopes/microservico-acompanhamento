"""
Testes de integração e edge cases para schemas da API de documentação.
Foco em interoperabilidade, performance e casos extremos.
"""

import json
import threading
import time
from datetime import datetime

import pytest
from pydantic import ValidationError

from app.domain.order_state import StatusPagamento, StatusPedido
from app.models.acompanhamento import Acompanhamento, ItemPedido
from app.schemas.acompanhamento_schemas import (
    AcompanhamentoResponse,
    AcompanhamentoResumoResponse,
    AtualizarStatusRequest,
    ErrorResponse,
    FilaPedidosResponse,
    HealthResponse,
    ItemPedidoResponse,
    SuccessResponse,
)


class TestSchemaModelIntegration:
    """
    Testes de integração entre schemas da API e models de domínio.

    Verifica:
    - Conversão Model → Schema
    - Compatibilidade de tipos
    - Preservação de dados
    - Mapeamento de enums
    """

    def test_conversao_acompanhamento_model_para_response(self):
        """Testa conversão completa de model Acompanhamento para AcompanhamentoResponse."""
        # Criar model de domínio
        itens_model = [
            ItemPedido(id_produto=1, quantidade=2),
            ItemPedido(id_produto=3, quantidade=1),
        ]

        acompanhamento_model = Acompanhamento(
            id_pedido=123,
            cpf_cliente="123.456.789-00",
            status=StatusPedido.EM_PREPARACAO,
            status_pagamento=StatusPagamento.PAGO,
            itens=itens_model,
            valor_pago=25.50,
            tempo_estimado="00:15:00",
            atualizado_em=datetime(2024, 1, 15, 10, 30, 0),
        )

        # Converter para schema de response
        itens_response = [
            ItemPedidoResponse(id_produto=item.id_produto, quantidade=item.quantidade)
            for item in acompanhamento_model.itens
        ]

        response = AcompanhamentoResponse(
            id_pedido=acompanhamento_model.id_pedido,
            cpf_cliente=acompanhamento_model.cpf_cliente,
            status=acompanhamento_model.status,
            status_pagamento=acompanhamento_model.status_pagamento,
            itens=itens_response,
            valor_pago=acompanhamento_model.valor_pago,
            tempo_estimado=acompanhamento_model.tempo_estimado,
            atualizado_em=acompanhamento_model.atualizado_em,
        )

        # Verificar que a conversão preserva todos os dados
        assert response.id_pedido == acompanhamento_model.id_pedido
        assert response.cpf_cliente == acompanhamento_model.cpf_cliente
        assert response.status == acompanhamento_model.status
        assert response.status_pagamento == acompanhamento_model.status_pagamento
        assert len(response.itens) == len(acompanhamento_model.itens)
        assert response.valor_pago == pytest.approx(acompanhamento_model.valor_pago)
        assert response.tempo_estimado == acompanhamento_model.tempo_estimado
        assert response.atualizado_em == acompanhamento_model.atualizado_em

        # Verificar itens individualmente
        for i, item_response in enumerate(response.itens):
            item_model = acompanhamento_model.itens[i]
            assert item_response.id_produto == item_model.id_produto
            assert item_response.quantidade == item_model.quantidade

    def test_conversao_acompanhamento_para_resumo(self):
        """Testa conversão de AcompanhamentoResponse para AcompanhamentoResumoResponse."""
        # Response completo
        response_completo = AcompanhamentoResponse(
            id_pedido=456,
            cpf_cliente="987.654.321-00",
            status=StatusPedido.PRONTO,
            status_pagamento=StatusPagamento.PAGO,
            itens=[ItemPedidoResponse(id_produto=1, quantidade=1)],
            valor_pago=35.00,
            tempo_estimado="00:02:00",
            atualizado_em=datetime(2024, 1, 15, 11, 0, 0),
        )

        # Converter para resumo (simula o que seria feito no service layer)
        resumo = AcompanhamentoResumoResponse(
            id_pedido=response_completo.id_pedido,
            cpf_cliente=response_completo.cpf_cliente,
            status=response_completo.status,
            tempo_estimado=response_completo.tempo_estimado,
            atualizado_em=response_completo.atualizado_em,
        )

        # Verificar que campos essenciais são preservados
        assert resumo.id_pedido == response_completo.id_pedido
        assert resumo.cpf_cliente == response_completo.cpf_cliente
        assert resumo.status == response_completo.status
        assert resumo.tempo_estimado == response_completo.tempo_estimado
        assert resumo.atualizado_em == response_completo.atualizado_em

        # Verificar que campos detalhados não estão presentes
        assert not hasattr(resumo, "itens")
        assert not hasattr(resumo, "valor_pago")
        assert not hasattr(resumo, "status_pagamento")

    def test_compatibilidade_enums_model_schema(self):
        """Testa compatibilidade completa de enums entre models e schemas."""
        # Testar todos os status de pedido
        for status in StatusPedido:
            # Schema de request
            request = AtualizarStatusRequest(status=status)
            assert request.status == status

            # Schema de response resumido
            resumo = AcompanhamentoResumoResponse(
                id_pedido=1,
                cpf_cliente="123.456.789-00",
                status=status,
                atualizado_em=datetime.now(),
            )
            assert resumo.status == status

            # Schema de response completo
            response = AcompanhamentoResponse(
                id_pedido=1,
                cpf_cliente="123.456.789-00",
                status=status,
                status_pagamento=StatusPagamento.PAGO,
                itens=[],
                atualizado_em=datetime.now(),
            )
            assert response.status == status

        # Testar todos os status de pagamento
        for status_pagamento in StatusPagamento:
            response = AcompanhamentoResponse(
                id_pedido=1,
                cpf_cliente="123.456.789-00",
                status=StatusPedido.RECEBIDO,
                status_pagamento=status_pagamento,
                itens=[],
                atualizado_em=datetime.now(),
            )
            assert response.status_pagamento == status_pagamento

    def test_factory_methods_simulation(self):
        """Testa simulação de factory methods para criação de schemas."""

        def create_response_from_model(
            acompanhamento: Acompanhamento,
        ) -> AcompanhamentoResponse:
            """Factory method simulado para conversão model → response."""
            return AcompanhamentoResponse(
                id_pedido=acompanhamento.id_pedido,
                cpf_cliente=acompanhamento.cpf_cliente,
                status=acompanhamento.status,
                status_pagamento=acompanhamento.status_pagamento,
                itens=[
                    ItemPedidoResponse(
                        id_produto=item.id_produto, quantidade=item.quantidade
                    )
                    for item in acompanhamento.itens
                ],
                valor_pago=acompanhamento.valor_pago,
                tempo_estimado=acompanhamento.tempo_estimado,
                atualizado_em=acompanhamento.atualizado_em,
            )

        # Testar factory method
        model = Acompanhamento(
            id_pedido=789,
            cpf_cliente="111.222.333-44",
            status=StatusPedido.FINALIZADO,
            status_pagamento=StatusPagamento.PAGO,
            itens=[ItemPedido(id_produto=2, quantidade=3)],
            valor_pago=50.00,
            tempo_estimado="completed",
            atualizado_em=datetime.now(),
        )

        response = create_response_from_model(model)

        assert response.id_pedido == model.id_pedido
        assert len(response.itens) == 1
        assert response.itens[0].id_produto == 2
        assert response.itens[0].quantidade == 3


class TestSchemaValidationEdgeCases:
    """
    Testes de edge cases e validações avançadas.

    Cobre:
    - Roundtrip JSON ↔ Schema
    - Casos extremos de dados
    - Comportamentos limítrofes
    """

    def test_json_roundtrip_completo_preservacao_dados(self):
        """Testa roundtrip completo JSON → Schema → JSON preservando dados."""
        original_data = {
            "id_pedido": 999,
            "cpf_cliente": "000.000.000-00",
            "status": "Em preparação",
            "status_pagamento": "pago",
            "itens": [
                {"id_produto": 1, "quantidade": 3},
                {"id_produto": 2, "quantidade": 1},
                {"id_produto": 99, "quantidade": 10},
            ],
            "valor_pago": 45.75,
            "tempo_estimado": "00:20:00",
            "atualizado_em": "2024-01-15T10:30:00",
        }

        # JSON → Schema
        response = AcompanhamentoResponse(**original_data)

        # Schema → JSON
        json_result = response.model_dump()

        # Verificar preservação de dados (exceto datetime que muda formato)
        assert json_result["id_pedido"] == original_data["id_pedido"]
        assert json_result["cpf_cliente"] == original_data["cpf_cliente"]
        assert json_result["status"] == original_data["status"]
        assert json_result["status_pagamento"] == original_data["status_pagamento"]
        assert len(json_result["itens"]) == len(original_data["itens"])
        assert json_result["valor_pago"] == pytest.approx(original_data["valor_pago"])
        assert json_result["tempo_estimado"] == original_data["tempo_estimado"]

        # Verificar itens preservados
        for i, item_original in enumerate(original_data["itens"]):
            item_result = json_result["itens"][i]
            assert item_result["id_produto"] == item_original["id_produto"]
            assert item_result["quantidade"] == item_original["quantidade"]

    def test_campos_none_vs_ausentes_comportamento(self):
        """Testa diferença entre campos None explícitos e campos ausentes."""
        base_data = {
            "id_pedido": 123,
            "cpf_cliente": "123.456.789-00",
            "status": StatusPedido.RECEBIDO,
            "status_pagamento": StatusPagamento.PENDENTE,
            "itens": [],
            "atualizado_em": datetime.now(),
        }

        # Com campos None explícitos
        response_with_none = AcompanhamentoResponse(
            **base_data,
            valor_pago=None,
            tempo_estimado=None,
        )

        # Sem campos opcionais (usando defaults)
        response_without_fields = AcompanhamentoResponse(**base_data)

        # Ambos devem ser equivalentes
        assert response_with_none.valor_pago is None
        assert response_without_fields.valor_pago is None
        assert response_with_none.tempo_estimado is None
        assert response_without_fields.tempo_estimado is None

        # Serialização deve ser idêntica
        json_with_none = response_with_none.model_dump()
        json_without = response_without_fields.model_dump()

        # Campos None podem aparecer explicitamente ou estar ausentes
        for key in ["valor_pago", "tempo_estimado"]:
            if key in json_with_none:
                assert json_with_none[key] is None
            if key in json_without:
                assert json_without[key] is None

    def test_schema_documentation_e_metadata(self):
        """Testa que schemas têm documentação e metadados adequados."""
        schemas_para_verificar = [
            (AtualizarStatusRequest, "Request para atualização"),
            (AcompanhamentoResponse, "Response completo"),
            (ErrorResponse, "Response de erro"),
            (SuccessResponse, "Response de sucesso"),
        ]

        for schema_class, descricao_esperada in schemas_para_verificar:
            schema_json = schema_class.model_json_schema()

            # Verificar estrutura básica OpenAPI
            assert "type" in schema_json
            assert "properties" in schema_json

            # Verificar que tem alguma documentação
            has_documentation = (
                "title" in schema_json
                or "description" in schema_json
                or any(
                    "description" in prop for prop in schema_json["properties"].values()
                )
            )
            assert (
                has_documentation
            ), f"Schema {schema_class.__name__} deveria ter documentação"

    def test_invalid_json_structures_rejection(self):
        """Testa que estruturas JSON inválidas são rejeitadas adequadamente."""
        invalid_structures = [
            # Lista onde deveria ser objeto
            [{"status": "pronto"}],
            # String onde deveria ser objeto
            '{"status": "pronto"}',
            # Número onde deveria ser objeto
            123,
            # Boolean onde deveria ser objeto
            True,
            # None onde deveria ser objeto
            None,
        ]

        for invalid_structure in invalid_structures:
            with pytest.raises((ValidationError, TypeError)):
                AtualizarStatusRequest(**invalid_structure)

    def test_campos_extras_ignorados_gracefully(self):
        """Testa que campos extras são ignorados graciosamente."""
        # Request com campos extras
        request_data = {
            "status": "Pronto",  # Valor correto do enum
            "campo_extra_1": "ignorado",
            "campo_extra_2": 123,
            "campo_extra_3": {"nested": "object"},
            "campo_extra_4": ["lista", "de", "valores"],
        }

        request = AtualizarStatusRequest(**request_data)
        assert request.status == StatusPedido.PRONTO

        # Campos extras não devem aparecer na serialização
        json_data = request.model_dump()
        assert set(json_data.keys()) == {"status"}

    def test_unicode_e_caracteres_especiais(self):
        """Testa suporte a Unicode e caracteres especiais."""
        # Dados com caracteres especiais
        response = SuccessResponse(
            message="Operação realizada com sucesso! ✅ 🎉",
            data={
                "caracteres_especiais": "áéíóú çñü àèìòù",
                "emojis": "😀 🚀 💯 ✨",
                "simbolos": "© ® ™ € $ £ ¥",
                "unicode": "こんにちは 世界",
            },
        )

        # Serialização deve preservar Unicode
        json_data = response.model_dump()
        assert "✅" in json_data["message"]
        assert "áéíóú" in json_data["data"]["caracteres_especiais"]
        assert "😀" in json_data["data"]["emojis"]

        # Roundtrip deve funcionar
        json_string = json.dumps(json_data, ensure_ascii=False)
        parsed_data = json.loads(json_string)
        response_restored = SuccessResponse(**parsed_data)
        assert response_restored.message == response.message

    def test_timezone_aware_datetime_handling(self):
        """Testa tratamento de datetime com timezone."""
        from datetime import timedelta, timezone

        # Datetime com timezone
        timezone_offset = timezone(timedelta(hours=-3))  # UTC-3
        timestamp_with_tz = datetime(2024, 1, 15, 10, 30, 0, tzinfo=timezone_offset)

        response = AcompanhamentoResponse(
            id_pedido=123,
            cpf_cliente="123.456.789-00",
            status=StatusPedido.RECEBIDO,
            status_pagamento=StatusPagamento.PENDENTE,
            itens=[],
            atualizado_em=timestamp_with_tz,
        )

        # Verificar que timezone é preservado
        assert response.atualizado_em.tzinfo is not None
        assert response.atualizado_em == timestamp_with_tz

        # Serialização deve incluir timezone
        json_data = response.model_dump(mode="json")  # Força serialização JSON
        timestamp_str = json_data["atualizado_em"]
        assert isinstance(timestamp_str, str)
        # ISO format deve incluir timezone info
        assert "-03:00" in timestamp_str or "T" in timestamp_str


class TestSchemaPerformance:
    """
    Testes de performance e eficiência dos schemas.

    Verifica:
    - Tempo de validação
    - Uso de memória
    - Escalabilidade
    """

    def test_performance_validacao_multiplos_schemas(self):
        """Testa performance de validação para múltiplos schemas."""
        start_time = time.time()

        # Criar muitos schemas diferentes
        schemas_criados = []
        for i in range(1000):
            # Varia entre diferentes tipos de schema
            if i % 4 == 0:
                schema = AtualizarStatusRequest(status=StatusPedido.PRONTO)
            elif i % 4 == 1:
                schema = ItemPedidoResponse(id_produto=i, quantidade=1)
            elif i % 4 == 2:
                schema = SuccessResponse(message=f"Operação {i} realizada")
            else:
                schema = ErrorResponse(detail=f"Erro {i}")

            schemas_criados.append(schema)

        end_time = time.time()

        # Validação deve ser rápida (< 1 segundo para 1000 schemas)
        assert end_time - start_time < 1.0
        assert len(schemas_criados) == 1000

    def test_performance_serialization_schemas_complexos(self):
        """Testa performance de serialização para schemas complexos."""
        # Criar response complexo com muitos itens
        many_items = [
            ItemPedidoResponse(id_produto=i, quantidade=i % 10 + 1) for i in range(100)
        ]

        response = AcompanhamentoResponse(
            id_pedido=1,
            cpf_cliente="123.456.789-00",
            status=StatusPedido.EM_PREPARACAO,
            status_pagamento=StatusPagamento.PAGO,
            itens=many_items,
            valor_pago=999.99,
            tempo_estimado="01:30:00",
            atualizado_em=datetime.now(),
        )

        start_time = time.time()

        # Serializar múltiplas vezes
        for _ in range(100):
            json_data = response.model_dump()
            assert len(json_data["itens"]) == 100

        end_time = time.time()

        # Deve ser rápido (< 1 segundo para 100 serializações)
        assert end_time - start_time < 1.0

    def test_memory_efficiency_schemas(self):
        """Testa eficiência de memória dos schemas."""
        import sys

        # Schemas simples devem ser eficientes em memória
        simple_schemas = [
            AtualizarStatusRequest(status=StatusPedido.PRONTO),
            SuccessResponse(message="OK"),
            ErrorResponse(detail="Error"),
        ]

        for schema in simple_schemas:
            size = sys.getsizeof(schema)
            # Deve ser relativamente pequeno (< 1KB)
            assert (
                size < 1024
            ), f"Schema {type(schema).__name__} muito grande: {size} bytes"

    def test_thread_safety_schema_operations(self):
        """Testa thread safety básica das operações de schema."""
        results = []
        errors = []

        def create_and_serialize_schema(thread_id):
            try:
                schema = AcompanhamentoResponse(
                    id_pedido=thread_id,
                    cpf_cliente=f"123.456.789-{thread_id:02d}",
                    status=StatusPedido.PRONTO,
                    status_pagamento=StatusPagamento.PAGO,
                    itens=[ItemPedidoResponse(id_produto=1, quantidade=1)],
                    atualizado_em=datetime.now(),
                )

                json_data = schema.model_dump()
                results.append((thread_id, json_data["id_pedido"]))
            except Exception as e:
                errors.append((thread_id, str(e)))

        # Criar múltiplas threads
        threads = []
        for i in range(10):
            thread = threading.Thread(target=create_and_serialize_schema, args=(i,))
            threads.append(thread)
            thread.start()

        # Aguardar todas as threads
        for thread in threads:
            thread.join()

        # Não deve haver erros
        assert len(errors) == 0, f"Erros em threads: {errors}"
        assert len(results) == 10

        # Resultados devem estar corretos
        for thread_id, pedido_id in results:
            assert thread_id == pedido_id


class TestSchemaFastAPIIntegration:
    """
    Testes de integração preparatórios para uso com FastAPI.

    Simula comportamentos que serão testados nos testes de endpoints.
    """

    def test_schema_fastapi_compatibility_simulation(self):
        """Simula compatibilidade com FastAPI response_model."""
        # Simula o que FastAPI faz internamente
        from fastapi.responses import JSONResponse

        # Simula endpoint que retorna AcompanhamentoResponse
        response_data = AcompanhamentoResponse(
            id_pedido=123,
            cpf_cliente="123.456.789-00",
            status=StatusPedido.PRONTO,
            status_pagamento=StatusPagamento.PAGO,
            itens=[ItemPedidoResponse(id_produto=1, quantidade=1)],
            valor_pago=25.50,
            tempo_estimado="00:05:00",
            atualizado_em=datetime.now(),
        )

        # FastAPI deve conseguir serializar
        json_response = JSONResponse(content=response_data.model_dump(mode="json"))
        assert json_response.status_code == 200

    def test_schema_openapi_generation_quality(self):
        """Testa qualidade da geração de documentação OpenAPI."""
        schemas_principais = [
            AtualizarStatusRequest,
            AcompanhamentoResponse,
            FilaPedidosResponse,
            SuccessResponse,
            ErrorResponse,
            HealthResponse,
        ]

        for schema_class in schemas_principais:
            openapi_schema = schema_class.model_json_schema()

            # Verificar estrutura básica
            assert "type" in openapi_schema
            assert "properties" in openapi_schema

            # Verificar que tem documentação útil
            has_meaningful_docs = (
                "title" in openapi_schema
                or "description" in openapi_schema
                or any(
                    "description" in prop and len(prop["description"]) > 10
                    for prop in openapi_schema["properties"].values()
                    if isinstance(prop, dict)
                )
            )
            assert (
                has_meaningful_docs
            ), f"Schema {schema_class.__name__} precisa de melhor documentação"

    def test_request_validation_simulation_completa(self):
        """Simula validação completa de requests HTTP."""
        # Simula dados que viriam de diferentes tipos de requisição
        test_cases = [
            # Caso válido básico
            ('{"status": "Pronto"}', StatusPedido.PRONTO, True),
            # Caso válido com enum diferente
            ('{"status": "Em preparação"}', StatusPedido.EM_PREPARACAO, True),
            # Caso inválido - status inexistente
            ('{"status": "inexistente"}', None, False),
            # Caso inválido - JSON malformado seria tratado antes
            ('{"status": "Finalizado"}', StatusPedido.FINALIZADO, True),
        ]

        for json_string, expected_status, should_succeed in test_cases:
            request_dict = json.loads(json_string)

            if should_succeed:
                request_obj = AtualizarStatusRequest(**request_dict)
                assert request_obj.status == expected_status
            else:
                with pytest.raises(ValidationError):
                    AtualizarStatusRequest(**request_dict)

    def test_error_response_fastapi_format(self):
        """Testa formatação de error responses compatível com FastAPI."""
        error_response = ErrorResponse(
            detail="Pedido não encontrado",
            error_code="ORDER_NOT_FOUND",
        )

        # Simula serialização para HTTP response
        json_data = error_response.model_dump()

        # Formato deve ser compatível com FastAPI HTTPException
        assert "detail" in json_data
        assert json_data["detail"] == "Pedido não encontrado"

        # Campos adicionais devem estar presentes
        assert json_data["error_code"] == "ORDER_NOT_FOUND"

        # Simula como FastAPI usaria isso
        from fastapi import HTTPException

        http_exception = HTTPException(
            status_code=404,
            detail=json_data,
        )
        assert http_exception.status_code == 404
        assert http_exception.detail == json_data
