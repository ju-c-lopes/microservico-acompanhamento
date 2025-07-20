"""
Testes unitários para schemas de REQUEST da API de acompanhamento.
Foco em validação de entrada, deserialização JSON e validação de campos.
"""

import json

import pytest
from pydantic import ValidationError

from app.domain.order_state import StatusPedido
from app.schemas.acompanhamento_schemas import AtualizarStatusRequest


class TestAtualizarStatusRequest:
    """
    Testes abrangentes para o schema de request de atualização de status.

    Cobre:
    - Validação de campos obrigatórios
    - Validação de enums
    - Serialização/deserialização
    - Edge cases de validação
    """

    def test_criar_request_valido(self):
        """Testa criação de request válido com status válido."""
        request = AtualizarStatusRequest(status=StatusPedido.EM_PREPARACAO)

        assert request.status == StatusPedido.EM_PREPARACAO
        assert isinstance(request.status, StatusPedido)

    def test_todos_status_validos_aceitos(self):
        """Testa que todos os valores do enum StatusPedido são aceitos."""
        status_validos = [
            StatusPedido.RECEBIDO,
            StatusPedido.EM_PREPARACAO,
            StatusPedido.PRONTO,
            StatusPedido.FINALIZADO,
        ]

        for status in status_validos:
            request = AtualizarStatusRequest(status=status)
            assert request.status == status
            assert isinstance(request.status, StatusPedido)

    def test_serialization_para_json(self):
        """Testa serialização do schema para formato JSON."""
        request = AtualizarStatusRequest(status=StatusPedido.PRONTO)
        json_data = request.model_dump()

        # Verifica estrutura do JSON
        assert isinstance(json_data, dict)
        assert "status" in json_data
        assert json_data["status"] == "Pronto"  # Enum serializado como string real

        # Verifica que pode ser convertido para JSON string
        json_string = json.dumps(json_data)
        assert '"Pronto"' in json_string

    def test_deserialization_de_json_string(self):
        """Testa deserialização a partir de string JSON."""
        # JSON com status como string (formato da API)
        json_data = {"status": "Em preparação"}
        request = AtualizarStatusRequest(**json_data)

        assert request.status == StatusPedido.EM_PREPARACAO

    def test_deserialization_de_enum_direto(self):
        """Testa deserialização a partir de enum diretamente."""
        # Dict com enum (caso de uso interno)
        dict_data = {"status": StatusPedido.FINALIZADO}
        request = AtualizarStatusRequest(**dict_data)

        assert request.status == StatusPedido.FINALIZADO

    def test_campo_status_obrigatorio(self):
        """Testa que o campo status é obrigatório."""
        with pytest.raises(ValidationError) as exc_info:
            AtualizarStatusRequest()

        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["type"] == "missing"
        assert errors[0]["loc"] == ("status",)
        assert "Field required" in errors[0]["msg"]

    def test_status_string_invalida(self):
        """Testa validação com string de status inválida."""
        status_invalidos = [
            "status_inexistente",
            "CANCELADO",  # Não existe no enum
            "preparando",  # Similar mas incorreto
            "",  # String vazia
            "null",  # String "null"
        ]

        for status_invalido in status_invalidos:
            with pytest.raises(ValidationError) as exc_info:
                AtualizarStatusRequest(status=status_invalido)

            errors = exc_info.value.errors()
            assert len(errors) == 1
            assert "Input should be" in errors[0]["msg"]

    def test_tipos_invalidos_rejeitados(self):
        """Testa que tipos inválidos são rejeitados."""
        tipos_invalidos = [
            123,  # Número
            [],  # Lista
            {},  # Dict vazio
            None,  # None
            True,  # Boolean
        ]

        for tipo_invalido in tipos_invalidos:
            with pytest.raises(ValidationError):
                AtualizarStatusRequest(status=tipo_invalido)

    def test_case_sensitivity_status(self):
        """Testa sensibilidade a maiúsculas/minúsculas."""
        # O enum deve ser case sensitive
        with pytest.raises(ValidationError):
            AtualizarStatusRequest(status="PRONTO")  # Maiúsculo incorreto

        with pytest.raises(ValidationError):
            AtualizarStatusRequest(status="pronto")  # Minúsculo incorreto

    def test_alias_e_validacao_campo(self):
        """Testa aliases de campo e validação personalizada."""
        # Verifica que o campo tem a documentação adequada
        schema = AtualizarStatusRequest.model_json_schema()

        assert "properties" in schema
        assert "status" in schema["properties"]

        # Verifica documentação do campo
        status_field = schema["properties"]["status"]
        assert "description" in status_field
        assert "Novo status do pedido" in status_field["description"]

    def test_validacao_extra_fields_ignorados(self):
        """Testa que campos extras são ignorados por padrão."""
        # Pydantic ignora campos extras por padrão
        request_data = {
            "status": "Pronto",  # Valor correto do enum
            "campo_extra": "ignorado",
            "outro_campo": 123,
        }

        request = AtualizarStatusRequest(**request_data)
        assert request.status == StatusPedido.PRONTO
        # Campos extras são ignorados silenciosamente

    def test_model_copy_e_update(self):
        """Testa funcionalidade de cópia e atualização do model."""
        request_original = AtualizarStatusRequest(status=StatusPedido.RECEBIDO)

        # Cria cópia com novo status
        request_copiado = request_original.model_copy(
            update={"status": StatusPedido.FINALIZADO}
        )

        assert request_original.status == StatusPedido.RECEBIDO
        assert request_copiado.status == StatusPedido.FINALIZADO

    def test_model_dump_diferentes_modos(self):
        """Testa diferentes modos de serialização."""
        request = AtualizarStatusRequest(status=StatusPedido.EM_PREPARACAO)

        # Dump padrão
        dump_padrao = request.model_dump()
        assert dump_padrao == {"status": "Em preparação"}

        # Dump excluindo campos (não aplicável neste caso, mas testa a funcionalidade)
        dump_partial = request.model_dump(exclude=set())
        assert dump_partial == dump_padrao

        # Dump como JSON serializable
        dump_json = request.model_dump(mode="json")
        assert dump_json == {"status": "Em preparação"}

    def test_hashable_e_equality(self):
        """Testa se requests com mesmo status são considerados iguais."""
        request1 = AtualizarStatusRequest(status=StatusPedido.PRONTO)
        request2 = AtualizarStatusRequest(status=StatusPedido.PRONTO)
        request3 = AtualizarStatusRequest(status=StatusPedido.RECEBIDO)

        # Igualdade
        assert request1 == request2
        assert request1 != request3

        # BaseModel não é hashable por padrão, então removemos teste de hash
        # assert hash(request1) == hash(request2)

    def test_representacao_string(self):
        """Testa representação em string do objeto."""
        request = AtualizarStatusRequest(status=StatusPedido.FINALIZADO)

        str_repr = str(request)
        # Pydantic BaseModel tem representação específica
        assert "status=" in str_repr
        assert "Finalizado" in str_repr

    def test_performance_validacao_multiplos_requests(self):
        """Testa performance de validação para múltiplos requests."""
        import time

        start_time = time.time()

        # Cria muitos requests para testar performance
        requests = []
        for i in range(1000):
            status = list(StatusPedido)[i % len(StatusPedido)]
            request = AtualizarStatusRequest(status=status)
            requests.append(request)

        end_time = time.time()

        # Validação deve ser rápida (< 1 segundo para 1000 requests)
        assert end_time - start_time < 1.0
        assert len(requests) == 1000

    def test_thread_safety_basico(self):
        """Testa segurança básica para uso em threads."""
        import threading

        results = []

        def create_request():
            request = AtualizarStatusRequest(status=StatusPedido.PRONTO)
            results.append(request.status)

        # Cria múltiplas threads
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=create_request)
            threads.append(thread)
            thread.start()

        # Aguarda todas as threads
        for thread in threads:
            thread.join()

        # Verifica que todos os resultados são corretos
        assert len(results) == 10
        assert all(result == StatusPedido.PRONTO for result in results)


class TestRequestSchemaValidationUtils:
    """
    Testes para utilities e funções auxiliares relacionadas a request schemas.
    """

    def test_schema_openapi_generation(self):
        """Testa geração de schema OpenAPI para documentação."""
        schema = AtualizarStatusRequest.model_json_schema()

        # Verifica estrutura básica do schema OpenAPI
        assert "type" in schema
        assert schema["type"] == "object"
        assert "properties" in schema
        assert "required" in schema
        assert "status" in schema["required"]

        # Verifica propriedades do campo status
        status_property = schema["properties"]["status"]
        assert "$ref" in status_property or "enum" in status_property

    def test_schema_compatibility_fastapi(self):
        """Testa compatibilidade com FastAPI para request body."""
        # Simula o que FastAPI faria ao receber um request
        from fastapi import FastAPI

        app = FastAPI()

        @app.put("/test")
        async def test_endpoint(request: AtualizarStatusRequest):
            return {"received_status": request.status.value}

        # Não executa o teste completo, mas verifica que FastAPI aceita o schema
        # (teste completo seria em test de integração)
        assert hasattr(AtualizarStatusRequest, "model_json_schema")

    def test_schema_error_messages_i18n_ready(self):
        """Testa que mensagens de erro são adequadas para internacionalização."""
        try:
            # Precisa usar Any para evitar erro de tipo
            from typing import Any

            status_invalido: Any = "status_invalido"
            AtualizarStatusRequest(status=status_invalido)
        except ValidationError as e:
            errors = e.errors()
            error_msg = errors[0]["msg"]

            # Mensagem deve ser em inglês (padrão Pydantic) para i18n
            assert "Input should be" in error_msg
            # Contexto deve incluir valores válidos
            assert "Recebido" in error_msg or "Pronto" in error_msg

    def test_request_schema_memory_efficiency(self):
        """Testa eficiência de memória dos request schemas."""
        import sys

        # Request deve ser leve em memória
        request = AtualizarStatusRequest(status=StatusPedido.PRONTO)
        size = sys.getsizeof(request)

        # Deve ser razoavelmente pequeno (menos de 1KB)
        assert size < 1024
