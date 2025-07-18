import pytest
from pydantic import ValidationError

from app.models.acompanhamento import ItemPedido


class TestItemPedido:
    """Unit tests for ItemPedido model"""

    def test_create_valid_item_pedido(self):
        """Test creating a valid ItemPedido"""
        item = ItemPedido(id_produto=123, quantidade=2)
        assert item.id_produto == 123
        assert item.quantidade == 2

    def test_item_pedido_serialization(self):
        """Test ItemPedido serialization to dict"""
        item = ItemPedido(id_produto=456, quantidade=1)
        expected = {"id_produto": 456, "quantidade": 1}
        assert item.model_dump() == expected

    def test_item_pedido_from_dict(self):
        """Test creating ItemPedido from dictionary"""
        data = {"id_produto": 789, "quantidade": 5}
        item = ItemPedido.model_validate(data)
        assert item.id_produto == 789
        assert item.quantidade == 5

    def test_item_pedido_invalid_types(self):
        """Test ItemPedido with invalid data types"""
        with pytest.raises(ValidationError):
            ItemPedido(id_produto="invalid", quantidade=1)

        with pytest.raises(ValidationError):
            ItemPedido(id_produto=123, quantidade="invalid")

    def test_item_pedido_missing_required_fields(self):
        """Test ItemPedido with missing required fields"""
        with pytest.raises(ValidationError):
            ItemPedido(id_produto=123)

        with pytest.raises(ValidationError):
            ItemPedido(quantidade=1)

    def test_item_pedido_negative_values(self):
        """Test ItemPedido validation with negative values (should fail)"""
        # id_produto and quantidade should not accept negative values according to business logic
        with pytest.raises(ValidationError) as exc_info:
            ItemPedido(id_produto=-1, quantidade=5)
        assert "Product ID must be positive" in str(exc_info.value)

        with pytest.raises(ValidationError) as exc_info:
            ItemPedido(id_produto=1, quantidade=-5)
        assert "Quantity must be positive" in str(exc_info.value)

        with pytest.raises(ValidationError) as exc_info:
            ItemPedido(id_produto=-1, quantidade=-5)
        assert "Product ID must be positive" in str(exc_info.value)

    def test_item_pedido_zero_quantity(self):
        """Test ItemPedido validation with zero quantity (should fail)"""
        # quantity should not be zero according to business logic
        with pytest.raises(ValidationError) as exc_info:
            ItemPedido(id_produto=123, quantidade=0)
        assert "Quantity must be positive" in str(exc_info.value)

        # Test zero id_produto as well
        with pytest.raises(ValidationError) as exc_info:
            ItemPedido(id_produto=0, quantidade=1)
        assert "Product ID must be positive" in str(exc_info.value)

    def test_item_pedido_equality(self):
        """Test ItemPedido equality comparison"""
        item1 = ItemPedido(id_produto=1, quantidade=2)
        item2 = ItemPedido(id_produto=1, quantidade=2)
        item3 = ItemPedido(id_produto=2, quantidade=2)

        assert item1 == item2
        assert item1 != item3

    def test_item_pedido_large_quantities(self):
        """Test with large item quantities"""
        large_item = ItemPedido(id_produto=1, quantidade=1000000)
        assert large_item.quantidade == 1000000
