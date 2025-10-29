"""Unit tests for product management functionality."""
import pytest
from decimal import Decimal
from src.product_manager import ProductManager, ProductError
from src.storage import Database

@pytest.fixture
def db():
    """Create test database instance."""
    db = Database(":memory:")  # Use in-memory SQLite for tests
    db.connect()
    yield db
    db.disconnect()

@pytest.fixture
def product_manager(db):
    """Create ProductManager instance with test database."""
    return ProductManager(db)

def test_INV_F_001_add_product(product_manager):
    """Test adding a new product with validation (INV-F-001)."""
    # Test successful product creation
    product = product_manager.add_product(
        sku="TEST001",
        name="Test Product",
        price=Decimal("10.99"),
        initial_stock=5,
        description="Test description"
    )
    assert product.sku == "TEST001"
    assert product.name == "Test Product"
    assert product.price == Decimal("10.99")
    assert product.stock_quantity == 5
    assert product.description == "Test description"

    # Test duplicate SKU validation
    with pytest.raises(ProductError, match="already exists"):
        product_manager.add_product(
            sku="TEST001",
            name="Another Product",
            price=Decimal("15.99")
        )

    # Test required field validation
    with pytest.raises(ProductError):
        product_manager.add_product(sku="", name="Invalid", price=Decimal("10.00"))

    # Test negative price validation
    with pytest.raises(ProductError):
        product_manager.add_product(
            sku="TEST002",
            name="Invalid Price",
            price=Decimal("-10.00")
        )

    # Test negative initial stock validation
    with pytest.raises(ProductError):
        product_manager.add_product(
            sku="TEST002",
            name="Invalid Stock",
            price=Decimal("10.00"),
            initial_stock=-1
        )

def test_INV_F_002_list_products(product_manager):
    """Test listing all products with stock (INV-F-002)."""
    # Add test products
    product_manager.add_product(
        sku="TEST001",
        name="Test Product 1",
        price=Decimal("10.99"),
        initial_stock=5
    )
    product_manager.add_product(
        sku="TEST002",
        name="Test Product 2",
        price=Decimal("15.99"),
        initial_stock=10
    )

    # Test listing products
    products = product_manager.list_products()
    assert len(products) == 2
    assert products[0].sku == "TEST001"
    assert products[0].stock_quantity == 5
    assert products[1].sku == "TEST002"
    assert products[1].stock_quantity == 10

def test_INV_F_003_update_stock(product_manager):
    """Test updating stock quantity (INV-F-003)."""
    # Add test product
    product_manager.add_product(
        sku="TEST001",
        name="Test Product",
        price=Decimal("10.99"),
        initial_stock=5
    )

    # Test increasing stock
    updated = product_manager.update_stock("TEST001", 3)
    assert updated.stock_quantity == 8

    # Test decreasing stock
    updated = product_manager.update_stock("TEST001", -2)
    assert updated.stock_quantity == 6

    # Test validation for negative resulting stock
    with pytest.raises(ProductError, match="negative quantity"):
        product_manager.update_stock("TEST001", -10)

    # Test validation for non-existent product
    with pytest.raises(ProductError, match="not found"):
        product_manager.update_stock("INVALID", 1)

def test_get_low_stock_products(product_manager):
    """Test retrieving products with low stock."""
    # Add products with various stock levels
    product_manager.add_product(
        sku="LOW001",
        name="Low Stock Product",
        price=Decimal("10.99"),
        initial_stock=5  # Below threshold
    )
    product_manager.add_product(
        sku="GOOD001",
        name="Good Stock Product",
        price=Decimal("15.99"),
        initial_stock=20  # Above threshold
    )

    # Test getting low stock products
    low_stock = product_manager.get_low_stock_products()
    assert len(low_stock) == 1
    assert low_stock[0].sku == "LOW001"
    assert low_stock[0].stock_quantity == 5

def test_get_critical_stock_products(product_manager):
    """Test retrieving products with critically low stock."""
    # Add products with various stock levels
    product_manager.add_product(
        sku="CRIT001",
        name="Critical Stock Product",
        price=Decimal("10.99"),
        initial_stock=2  # Below critical threshold
    )
    product_manager.add_product(
        sku="LOW001",
        name="Low Stock Product",
        price=Decimal("15.99"),
        initial_stock=8  # Above critical but below low threshold
    )

    # Test getting critical stock products
    critical = product_manager.get_critical_stock_products()
    assert len(critical) == 1
    assert critical[0].sku == "CRIT001"
    assert critical[0].stock_quantity == 2