"""Unit tests for order processing functionality."""
import pytest
from decimal import Decimal
from src.product_manager import ProductManager
from src.order_processor import OrderProcessor, OrderError
from src.storage import Database

@pytest.fixture
def db():
    """Create test database instance."""
    db = Database(":memory:")
    db.connect()
    yield db
    db.disconnect()

@pytest.fixture
def product_manager(db):
    """Create ProductManager instance with test database."""
    return ProductManager(db)

@pytest.fixture
def order_processor(db, product_manager):
    """Create OrderProcessor instance with test database."""
    return OrderProcessor(db, product_manager)

@pytest.fixture
def sample_product(product_manager):
    """Create a sample product for testing."""
    return product_manager.add_product(
        sku="TEST001",
        name="Test Product",
        price=Decimal("10.99"),
        initial_stock=10
    )

def test_INV_F_010_create_sales_order(order_processor, sample_product):
    """Test creating a sales order (INV-F-010)."""
    # Test successful sale
    order = order_processor.create_sales_order("TEST001", 3)
    assert order.order_type == "SALE"
    assert order.product_sku == "TEST001"
    assert order.quantity == 3
    assert order.price == Decimal("32.97")  # 3 * 10.99

    # Verify stock was updated
    product = order_processor.product_manager.get_product("TEST001")
    assert product.stock_quantity == 7

def test_INV_F_011_insufficient_stock(order_processor, sample_product):
    """Test prevention of sales with insufficient stock (INV-F-011)."""
    # Attempt to sell more than available
    with pytest.raises(OrderError, match="Insufficient stock"):
        order_processor.create_sales_order("TEST001", 15)

    # Verify stock wasn't changed
    product = order_processor.product_manager.get_product("TEST001")
    assert product.stock_quantity == 10

def test_INV_F_012_create_purchase_order(order_processor, sample_product):
    """Test creating a purchase order (INV-F-012)."""
    # Test successful purchase
    order = order_processor.create_purchase_order(
        "TEST001",
        5,
        Decimal("45.00")
    )
    assert order.order_type == "PURCHASE"
    assert order.product_sku == "TEST001"
    assert order.quantity == 5
    assert order.price == Decimal("45.00")

    # Verify stock was updated
    product = order_processor.product_manager.get_product("TEST001")
    assert product.stock_quantity == 15

def test_order_validation(order_processor, sample_product):
    """Test order input validation."""
    # Test negative quantity for sale
    with pytest.raises(OrderError, match="must be positive"):
        order_processor.create_sales_order("TEST001", -1)

    # Test zero quantity for purchase
    with pytest.raises(OrderError, match="must be positive"):
        order_processor.create_purchase_order("TEST001", 0, Decimal("10.00"))

    # Test negative price for purchase
    with pytest.raises(OrderError, match="cannot be negative"):
        order_processor.create_purchase_order(
            "TEST001",
            1,
            Decimal("-10.00")
        )

def test_list_orders(order_processor, sample_product):
    """Test listing orders with filters."""
    # Create some test orders
    order_processor.create_sales_order("TEST001", 2)
    order_processor.create_purchase_order("TEST001", 3, Decimal("25.00"))

    # Test listing all orders
    all_orders = order_processor.list_orders()
    assert len(all_orders) == 2

    # Test filtering sales orders
    sales = order_processor.list_orders("SALE")
    assert len(sales) == 1
    assert sales[0].order_type == "SALE"

    # Test filtering purchase orders
    purchases = order_processor.list_orders("PURCHASE")
    assert len(purchases) == 1
    assert purchases[0].order_type == "PURCHASE"