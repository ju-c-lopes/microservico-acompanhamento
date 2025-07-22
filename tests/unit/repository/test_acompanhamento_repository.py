"""
Testes unitários para AcompanhamentoRepository

Estes testes definem o COMPORTAMENTO ESPERADO do repository.
Vamos usar mocks para não depender de banco de dados real.

Por que começar com testes?
1. Define claramente o que o repository deve fazer
2. Garante que a implementação está correta
3. Documenta o comportamento esperado
4. Permite refatoração segura
"""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest

from app.db.base import Acompanhamento as AcompanhamentoModel
from app.domain.order_state import StatusPedido
from app.repository.acompanhamento_repository import (
    AcompanhamentoRepository, AcompanhamentoRepositoryInterface)


class TestAcompanhamentoRepositoryInterface:
    """
    Testa se nossa implementação segue corretamente a interface.

    Por que testar interface?
    - Garante que implementação concreta respeita o contrato
    - Facilita substituição de implementações (ex: PostgreSQL → MongoDB)
    - Documenta o que qualquer implementação deve fazer
    """

    def test_repository_implements_interface(self):
        """
        Verifica se AcompanhamentoRepository implementa corretamente a interface
        """
        # Arrange & Act
        mock_session = AsyncMock()
        repository = AcompanhamentoRepository(mock_session)

        # Assert
        assert isinstance(repository, AcompanhamentoRepositoryInterface)

        # Verifica se todos os métodos da interface estão implementados
        interface_methods = [
            "criar",
            "buscar_por_id",
            "buscar_por_id_pedido",
            "buscar_por_cpf_cliente",
            "buscar_por_status",
            "atualizar",
            "listar_todos",
        ]

        for method_name in interface_methods:
            assert hasattr(repository, method_name)
            assert callable(getattr(repository, method_name))


class TestAcompanhamentoRepositoryCreateOperations:
    """
    Testa operações de criação no repository.

    Por que separar por operação?
    - Organização: Fica mais fácil encontrar teste específico
    - Foco: Cada classe testa um aspecto específico
    - Manutenção: Mudanças em uma operação afetam apenas uma classe
    """

    @pytest.mark.anyio
    async def test_criar_acompanhamento_success(self, sample_acompanhamento):
        """
        Testa criação bem-sucedida de acompanhamento.

        Este teste define que:
        1. Repository deve aceitar um objeto Acompanhamento
        2. Deve retornar o objeto criado (possivelmente com ID gerado)
        3. Deve chamar os métodos corretos do SQLAlchemy
        """
        # Arrange
        mock_session = AsyncMock()
        repository = AcompanhamentoRepository(mock_session)

        # Mock para a consulta com eager loading
        mock_result = AsyncMock()
        mock_result.scalar_one.return_value = sample_acompanhamento
        mock_session.execute.return_value = mock_result

        # Criamos uma cópia do acompanhamento para simular o resultado com ID
        expected_result = sample_acompanhamento

        # Act
        with patch.object(repository, "_to_db_model") as mock_to_db:
            with patch.object(repository, "_from_db_model") as mock_from_db:
                mock_to_db.return_value = sample_acompanhamento
                mock_from_db.return_value = expected_result

                result = await repository.criar(sample_acompanhamento)

        # Assert
        assert result == expected_result
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()
        mock_session.execute.assert_called_once()  # Para consulta com eager loading

    @pytest.mark.anyio
    async def test_criar_acompanhamento_duplicate_id_pedido(
        self, sample_acompanhamento
    ):
        """
        Testa tentativa de criar acompanhamento com ID de pedido duplicado.

        Regra de negócio: Não pode existir dois acompanhamentos para mesmo pedido.
        """
        # Arrange
        mock_session = AsyncMock()
        repository = AcompanhamentoRepository(mock_session)

        # Simula erro de constraint do banco
        from sqlalchemy.exc import IntegrityError

        mock_session.commit.side_effect = IntegrityError(
            "Duplicate entry", {}, Exception("orig")
        )

        # Act & Assert
        with pytest.raises(ValueError, match="Já existe acompanhamento"):
            await repository.criar(sample_acompanhamento)


class TestAcompanhamentoRepositoryReadOperations:
    """
    Testa operações de leitura/busca no repository.
    """

    @pytest.mark.anyio
    async def test_buscar_por_id_found(self):
        """
        Testa busca por ID quando registro existe.
        """
        # Arrange
        mock_session = AsyncMock()
        repository = AcompanhamentoRepository(mock_session)

        # Mock do objeto de banco de dados com atributos simples
        class MockDbAcompanhamento:
            id_pedido = 12345
            cpf_cliente = "12345678901"
            status = "Recebido"
            status_pagamento = "pendente"
            tempo_estimado = "25 min"
            atualizado_em = datetime.now()
            valor_pago = None

            def __init__(self):
                # Mock de itens do banco
                class MockDbItem:
                    id_produto = 101
                    quantidade = 2

                self.itens = [MockDbItem()]

        mock_db_acompanhamento = MockDbAcompanhamento()

        # Mock para o execute() do SQLAlchemy
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = mock_db_acompanhamento
        mock_session.execute.return_value = mock_result

        result = await repository.buscar_por_id(1)

        # Assert
        assert result is not None
        assert result.id_pedido == 12345
        mock_session.execute.assert_called_once()

    @pytest.mark.anyio
    async def test_buscar_por_id_not_found(self):
        """
        Testa busca por ID quando registro não existe.
        """
        # Arrange
        mock_session = AsyncMock()
        repository = AcompanhamentoRepository(mock_session)

        # Mock para o execute() do SQLAlchemy retornando None
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        # Act
        result = await repository.buscar_por_id(999)

        # Assert
        assert result is None
        mock_session.execute.assert_called_once()

    @pytest.mark.anyio
    async def test_buscar_por_id_pedido_found(self, sample_acompanhamento):
        """
        Testa busca por ID do pedido - método muito usado no service.
        """
        # Arrange
        mock_session = AsyncMock()
        repository = AcompanhamentoRepository(mock_session)

        # Simula resultado da query
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = sample_acompanhamento
        mock_session.execute.return_value = mock_result

        # Act
        with patch.object(repository, "_from_db_model") as mock_from_db:
            mock_from_db.return_value = sample_acompanhamento
            result = await repository.buscar_por_id_pedido(12345)

        # Assert
        assert result == sample_acompanhamento
        mock_session.execute.assert_called_once()

    @pytest.mark.anyio
    async def test_buscar_por_cpf_cliente(self, sample_acompanhamento):
        """
        Testa busca por CPF - para histórico do cliente.
        """
        # Arrange
        mock_session = AsyncMock()
        repository = AcompanhamentoRepository(mock_session)

        # Simula lista de resultados - usar Mock simples para .all()
        mock_scalars = AsyncMock()
        mock_scalars.all = lambda: [
            sample_acompanhamento
        ]  # função simples não coroutine

        mock_result = AsyncMock()
        mock_result.scalars = lambda: mock_scalars  # função simples não coroutine
        mock_session.execute.return_value = mock_result

        # Act
        with patch.object(repository, "_from_db_model") as mock_from_db:
            mock_from_db.return_value = sample_acompanhamento
            results = await repository.buscar_por_cpf_cliente("123.456.789-00")

        # Assert
        assert len(results) == 1
        assert results[0] == sample_acompanhamento
        mock_session.execute.assert_called_once()

    @pytest.mark.anyio
    async def test_buscar_por_status_multiple_statuses(
        self, sample_acompanhamento, sample_acompanhamento_em_preparacao
    ):
        """
        Testa busca por múltiplos status - para fila de produção.
        """
        # Arrange
        mock_session = AsyncMock()
        repository = AcompanhamentoRepository(mock_session)

        # Simula múltiplos resultados
        mock_scalars = AsyncMock()
        mock_scalars.all = lambda: [
            sample_acompanhamento,
            sample_acompanhamento_em_preparacao,
        ]

        mock_result = AsyncMock()
        mock_result.scalars = lambda: mock_scalars
        mock_session.execute.return_value = mock_result

        # Act
        with patch.object(repository, "_from_db_model") as mock_from_db:
            mock_from_db.side_effect = [
                sample_acompanhamento,
                sample_acompanhamento_em_preparacao,
            ]
            results = await repository.buscar_por_status(
                [StatusPedido.RECEBIDO, StatusPedido.EM_PREPARACAO]
            )

        # Assert
        assert len(results) == 2
        assert results[0] == sample_acompanhamento
        assert results[1] == sample_acompanhamento_em_preparacao


class TestAcompanhamentoRepositoryUpdateOperations:
    """
    Testa operações de atualização no repository.
    """

    @pytest.mark.anyio
    async def test_atualizar_acompanhamento_success(self, sample_acompanhamento):
        """
        Testa atualização bem-sucedida de acompanhamento.
        """
        # Arrange
        mock_session = AsyncMock()
        repository = AcompanhamentoRepository(mock_session)

        # Modifica dados para simular atualização
        sample_acompanhamento.status = StatusPedido.EM_PREPARACAO
        sample_acompanhamento.atualizado_em = datetime.now()

        # Simula que registro existe no banco
        mock_db_acompanhamento = MagicMock()
        mock_db_acompanhamento.id_acompanhamento = 1
        mock_db_acompanhamento.id_pedido = sample_acompanhamento.id_pedido

        mock_result = AsyncMock()
        mock_result.scalar_one_or_none = lambda: mock_db_acompanhamento
        mock_session.execute.return_value = mock_result

        # Act
        with patch.object(repository, "_from_db_model") as mock_from_db:
            mock_from_db.return_value = sample_acompanhamento
            result = await repository.atualizar(sample_acompanhamento)

        # Assert
        assert result == sample_acompanhamento
        mock_session.commit.assert_called_once()

    @pytest.mark.anyio
    async def test_atualizar_acompanhamento_not_found(self, sample_acompanhamento):
        """
        Testa tentativa de atualizar acompanhamento inexistente.
        """
        # Arrange
        mock_session = AsyncMock()
        repository = AcompanhamentoRepository(mock_session)

        # Simula que registro não existe no banco
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none = lambda: None  # função simples
        mock_session.execute.return_value = mock_result

        # Act & Assert
        with pytest.raises(ValueError, match="Acompanhamento não encontrado"):
            await repository.atualizar(sample_acompanhamento)


class TestAcompanhamentoRepositoryPaginationOperations:
    """
    Testa operações de listagem com paginação.
    """

    @pytest.mark.anyio
    async def test_listar_todos_with_pagination(self, sample_acompanhamento):
        """
        Testa listagem com paginação - importante para performance.
        """
        # Arrange
        mock_session = AsyncMock()
        repository = AcompanhamentoRepository(mock_session)

        # Simula resultado paginado
        mock_scalars = AsyncMock()
        mock_scalars.all = lambda: [sample_acompanhamento]

        mock_result = AsyncMock()
        mock_result.scalars = lambda: mock_scalars
        mock_session.execute.return_value = mock_result

        # Act
        with patch.object(repository, "_from_db_model") as mock_from_db:
            mock_from_db.return_value = sample_acompanhamento
            results = await repository.listar_todos(skip=10, limit=5)

        # Assert
        assert len(results) == 1
        assert results[0] == sample_acompanhamento
        mock_session.execute.assert_called_once()

        # Verifica se query incluiu offset e limit
        # (implementação específica depende de como construirmos a query)
