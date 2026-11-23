"""Integration tests: OrderService + ProductRepository + calculation functions together.

Every test follows Arrange / Act / Assert. `order_service` comes from conftest.py.
"""


class TestIntegrationOrderService:
    def test_successful_order(self, order_service):
        # Act
        result = order_service.place_order("SHIRT", 2)
        # Assert: 2 x 25 = 50, + 20 % tax = 60
        assert result == {"success": True, "item": "T-Shirt", "quantity": 2, "total": 60.0}

    def test_stock_is_reduced(self, order_service):
        order_service.place_order("MUG", 3)
        assert order_service.repo.get_product("MUG")["stock"] == 97

    def test_unknown_product(self, order_service):
        assert order_service.place_order("PANTS", 1) == {"success": False, "error": "Product not found"}

    def test_not_enough_stock_and_stock_unchanged(self, order_service):
        result = order_service.place_order("HAT", 999)
        assert result == {"success": False, "error": "Not enough stock"}
        assert order_service.repo.get_product("HAT")["stock"] == 30

    def test_multiple_orders_deplete_stock(self, order_service):
        order_service.place_order("HAT", 10)
        order_service.place_order("HAT", 15)
        assert order_service.repo.get_product("HAT")["stock"] == 5

    def test_exact_stock_then_empty(self, order_service):
        assert order_service.place_order("HAT", 30)["success"] is True
        assert order_service.place_order("HAT", 1)["error"] == "Not enough stock"

    def test_zero_quantity_rejected(self, order_service):
        # bug found while testing: an order of 0 items used to succeed
        assert order_service.place_order("MUG", 0) == {"success": False, "error": "Quantity must be positive"}
