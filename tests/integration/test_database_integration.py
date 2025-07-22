"""
Database Integration Tests for AcompanhamentoRepository.
Comprehensive tests to verify database integration works correctly.
"""

import pytest

from app.domain.order_state import StatusPedido
from app.models.acompanhamento import Acompanhamento


class TestDatabaseCRUDOperations:
    """Test CRUD operations with real database."""

    @pytest.mark.anyio
    async def test_criar_acompanhamento_success(
        self, repository, sample_acompanhamento_data
    ):
        """Test successful creation in database."""
        # Arrange
        acompanhamento = Acompanhamento(**sample_acompanhamento_data)

        # Act
        resultado = await repository.criar(acompanhamento)

        # Assert
        assert resultado is not None
        assert resultado.id_pedido == sample_acompanhamento_data["id_pedido"]
        assert resultado.cpf_cliente == sample_acompanhamento_data["cpf_cliente"]
        assert resultado.status == sample_acompanhamento_data["status"]
        assert len(resultado.itens) == len(sample_acompanhamento_data["itens"])

    @pytest.mark.anyio
    async def test_buscar_por_id_pedido_found(
        self, repository, sample_acompanhamento_data
    ):
        """Test finding existing record by pedido ID."""
        # Arrange
        acompanhamento = Acompanhamento(**sample_acompanhamento_data)
        await repository.criar(acompanhamento)

        # Act
        encontrado = await repository.buscar_por_id_pedido(
            sample_acompanhamento_data["id_pedido"]
        )

        # Assert
        assert encontrado is not None
        assert encontrado.id_pedido == sample_acompanhamento_data["id_pedido"]
        assert encontrado.cpf_cliente == sample_acompanhamento_data["cpf_cliente"]
        assert len(encontrado.itens) == len(sample_acompanhamento_data["itens"])

    @pytest.mark.anyio
    async def test_buscar_por_id_pedido_not_found(self, repository):
        """Test searching for non-existent pedido ID."""
        # Act
        encontrado = await repository.buscar_por_id_pedido(99999)

        # Assert
        assert encontrado is None

    @pytest.mark.anyio
    async def test_buscar_por_cpf_cliente(self, repository, sample_acompanhamento_data):
        """Test finding records by client CPF."""
        # Arrange
        acompanhamento = Acompanhamento(**sample_acompanhamento_data)
        await repository.criar(acompanhamento)

        # Act
        encontrados = await repository.buscar_por_cpf_cliente(
            sample_acompanhamento_data["cpf_cliente"]
        )

        # Assert
        assert len(encontrados) == 1
        assert encontrados[0].cpf_cliente == sample_acompanhamento_data["cpf_cliente"]
        assert len(encontrados[0].itens) == len(sample_acompanhamento_data["itens"])

    @pytest.mark.anyio
    async def test_atualizar_acompanhamento(
        self, repository, sample_acompanhamento_data
    ):
        """Test updating existing record."""
        # Arrange
        acompanhamento = Acompanhamento(**sample_acompanhamento_data)
        criado = await repository.criar(acompanhamento)

        # Act
        criado.status = StatusPedido.EM_PREPARACAO
        criado.tempo_estimado = "30 min"
        atualizado = await repository.atualizar(criado)

        # Assert
        assert atualizado.status == StatusPedido.EM_PREPARACAO
        assert atualizado.tempo_estimado == "30 min"
        assert atualizado.id_pedido == sample_acompanhamento_data["id_pedido"]
        assert len(atualizado.itens) == len(sample_acompanhamento_data["itens"])

    @pytest.mark.anyio
    async def test_buscar_por_status(self, repository, sample_acompanhamento_data):
        """Test finding records by status."""
        # Arrange
        acompanhamento = Acompanhamento(**sample_acompanhamento_data)
        await repository.criar(acompanhamento)

        # Act
        encontrados = await repository.buscar_por_status([StatusPedido.RECEBIDO])

        # Assert
        assert len(encontrados) >= 1
        pedido_encontrado = any(
            a.id_pedido == sample_acompanhamento_data["id_pedido"] for a in encontrados
        )
        assert pedido_encontrado

        # Verify itens are loaded
        for acompanhamento_encontrado in encontrados:
            if (
                acompanhamento_encontrado.id_pedido
                == sample_acompanhamento_data["id_pedido"]
            ):
                assert len(acompanhamento_encontrado.itens) == len(
                    sample_acompanhamento_data["itens"]
                )

    @pytest.mark.anyio
    async def test_listar_todos_com_paginacao(
        self, repository, sample_acompanhamento_data, sample_acompanhamento_data_alt
    ):
        """Test listing all records with pagination."""
        # Arrange
        acompanhamento1 = Acompanhamento(**sample_acompanhamento_data)
        acompanhamento2 = Acompanhamento(**sample_acompanhamento_data_alt)
        await repository.criar(acompanhamento1)
        await repository.criar(acompanhamento2)

        # Act
        resultado = await repository.listar_todos(skip=0, limit=10)

        # Assert
        assert len(resultado) == 2
        ids_pedidos = [r.id_pedido for r in resultado]
        assert sample_acompanhamento_data["id_pedido"] in ids_pedidos
        assert sample_acompanhamento_data_alt["id_pedido"] in ids_pedidos

        # Verify itens are loaded for all records
        for acompanhamento_resultado in resultado:
            assert len(acompanhamento_resultado.itens) > 0


class TestDatabaseConstraints:
    """Test database constraints and validations."""

    @pytest.mark.anyio
    async def test_unique_constraint_id_pedido(
        self, repository, sample_acompanhamento_data
    ):
        """Test unique constraint on pedido ID."""
        # Arrange
        acompanhamento1 = Acompanhamento(**sample_acompanhamento_data)
        await repository.criar(acompanhamento1)

        # Act & Assert
        acompanhamento2 = Acompanhamento(**sample_acompanhamento_data)  # Same ID
        with pytest.raises(ValueError, match="Já existe acompanhamento"):
            await repository.criar(acompanhamento2)
