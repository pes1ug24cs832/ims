"""Integration tests for database operations and business logic."""
import pytest
import tempfile
import os
import shutil
from decimal import Decimal
from pathlib import Path

from src.storage import Database
from src.product_manager import ProductManager
from src.supplier_manager import SupplierManager
from src.order_processor import OrderProcessor
from src.auth import AuthManager, AuthenticationError, hash_password
from src.backup_security import BackupManager

@pytest.fixture
def temp_db_path():
    """Create a temporary database file."""
    fd, path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    yield path
    if os.path.exists(path):
        os.unlink(path)

@pytest.fixture
def db(temp_db_path):
    """Create a test database instance."""
    # Create an empty file first
    Path(temp_db_path).touch()
    
    # Initialize database
    db = Database(temp_db_path)
    db.connect()
    db._create_schema()  # Ensure schema is created
    
    yield db
    
    # Cleanup
    db.disconnect()
    try:
        Path(temp_db_path).unlink()
    except FileNotFoundError:
        pass

@pytest.fixture
def product_manager(db):
    """Create a ProductManager instance."""
    return ProductManager(db)

@pytest.fixture
def supplier_manager(db):
    """Create a SupplierManager instance."""
    return SupplierManager(db)

@pytest.fixture
def order_processor(db, product_manager):
    """Create an OrderProcessor instance."""
    return OrderProcessor(db, product_manager)

@pytest.fixture
def auth_manager(monkeypatch):
    """Create an AuthManager instance with test credentials."""
    # Generate a fresh hash for the test password
    test_password = "adminpass"
    password_hash = hash_password(test_password)
    
    # Patch the password hash in the config
    monkeypatch.setattr('src.config.ADMIN_PASSWORD_HASH', password_hash)
    
    return AuthManager()

def test_db_integration_product_order_flow(product_manager, order_processor):
    """Test full product and order workflow integration."""
    # Add product
    product = product_manager.add_product(
        sku="TEST001",
        name="Test Product",
        price=Decimal("10.99"),
        initial_stock=10
    )
    assert product.stock_quantity == 10

    # Create sales order
    sale = order_processor.create_sales_order(product.sku, 3)
    assert sale.quantity == 3
    assert sale.price == Decimal("32.97")  # 3 * 10.99

    # Verify stock updated
    updated_product = product_manager.get_product(product.sku)
    assert updated_product.stock_quantity == 7

    # Create purchase order
    purchase = order_processor.create_purchase_order(
        product.sku,
        5,
        Decimal("45.00")
    )
    assert purchase.quantity == 5

    # Verify final stock
    final_product = product_manager.get_product(product.sku)
    assert final_product.stock_quantity == 12

def test_db_integration_supplier_product_relationship(
    supplier_manager, product_manager):
    """Test supplier and product integration."""
    # Add supplier
    supplier = supplier_manager.add_supplier(
        name="Test Supplier",
        contact_person="John Doe",
        email="john@example.com"
    )
    assert supplier.id is not None

    # Add products
    product1 = product_manager.add_product(
        sku="SUPP001",
        name="Supplier Product 1",
        price=Decimal("10.99"),
        initial_stock=5
    )
    product2 = product_manager.add_product(
        sku="SUPP002",
        name="Supplier Product 2",
        price=Decimal("15.99"),
        initial_stock=8
    )

    # Verify products in database
    products = product_manager.list_products()
    assert len(products) == 2
    assert any(p.sku == "SUPP001" for p in products)
    assert any(p.sku == "SUPP002" for p in products)

def test_db_integration_backup_restore(temp_db_path, db, product_manager):
    """Test database backup and restore functionality."""
    # Ensure database is initialized
    db.connect()
    
    # Create backup manager with temporary backup directory
    backup_dir = tempfile.mkdtemp()
    backup_manager = BackupManager(db, backup_dir)    # Add test data
    product = product_manager.add_product(
        sku="BACKUP001",
        name="Backup Test Product",
        price=Decimal("10.99"),
        initial_stock=5
    )

    # Create backup
    passphrase = "test-passphrase"
    backup_path = backup_manager.create_backup(passphrase)
    assert backup_path.exists()

    # Clear database by closing and recreating
    db.disconnect()
    os.unlink(temp_db_path)
    db.connect()  # This will create a new empty database

    # Verify data is gone
    assert not product_manager.get_product("BACKUP001")

    # Restore from backup
    backup_manager.restore_from_backup(backup_path, passphrase)
    
    # Reconnect to the restored database to ensure fresh connection
    db.disconnect()
    db.connect()
    
    # Initialize schema after restore
    db._create_schema()

    # Verify data is restored
    restored = product_manager.get_product("BACKUP001")
    assert restored is not None
    assert restored.name == "Backup Test Product"
    assert restored.stock_quantity == 5

    # Cleanup
    shutil.rmtree(backup_dir)

def test_db_integration_authentication(auth_manager):
    """Test authentication integration."""
    # Test successful login
    session = auth_manager.authenticate("admin", "adminpass")
    assert session.username == "admin"
    assert session.is_admin is True

    # Test invalid credentials
    with pytest.raises(AuthenticationError):
        auth_manager.authenticate("admin", "wrongpass")

    with pytest.raises(AuthenticationError):
        auth_manager.authenticate("wronguser", "adminpass")

def test_db_integration_stock_alerts(product_manager):
    """Test stock alerting integration."""
    # Add products with various stock levels
    product_manager.add_product(
        sku="CRIT001",
        name="Critical Stock",
        price=Decimal("10.99"),
        initial_stock=2
    )
    product_manager.add_product(
        sku="LOW001",
        name="Low Stock",
        price=Decimal("11.99"),
        initial_stock=8
    )
    product_manager.add_product(
        sku="GOOD001",
        name="Good Stock",
        price=Decimal("12.99"),
        initial_stock=20
    )

    # Check low stock alerts
    low_stock = product_manager.get_low_stock_products()
    assert len(low_stock) == 2  # Both CRIT001 and LOW001 should be included
    assert any(p.sku == "CRIT001" for p in low_stock)
    assert any(p.sku == "LOW001" for p in low_stock)

    # Check critical stock alerts
    critical = product_manager.get_critical_stock_products()
    assert len(critical) == 1  # Only CRIT001
    assert critical[0].sku == "CRIT001"