"""Unit tests for supplier management functionality."""
import pytest
from src.supplier_manager import SupplierManager, SupplierError
from src.storage import Database

@pytest.fixture
def db():
    """Create test database instance."""
    db = Database(":memory:")
    db.connect()
    yield db
    db.disconnect()

@pytest.fixture
def supplier_manager(db):
    """Create SupplierManager instance with test database."""
    return SupplierManager(db)

def test_INV_F_020_add_supplier(supplier_manager):
    """Test adding a new supplier with contact details (INV-F-020)."""
    # Test successful supplier creation
    supplier = supplier_manager.add_supplier(
        name="Test Supplier",
        contact_person="John Doe",
        email="john@example.com",
        phone="123-456-7890"
    )
    assert supplier.name == "Test Supplier"
    assert supplier.contact_person == "John Doe"
    assert supplier.email == "john@example.com"
    assert supplier.phone == "123-456-7890"

    # Test required fields validation
    with pytest.raises(SupplierError, match="required"):
        supplier_manager.add_supplier(name="")

def test_email_validation(supplier_manager):
    """Test email format validation."""
    # Test invalid email format
    with pytest.raises(SupplierError, match="Invalid email"):
        supplier_manager.add_supplier(
            name="Test Supplier",
            email="invalid-email"
        )

    # Test valid email format
    supplier = supplier_manager.add_supplier(
        name="Test Supplier",
        email="valid.email@example.com"
    )
    assert supplier.email == "valid.email@example.com"

def test_INV_F_021_list_suppliers(supplier_manager):
    """Test listing all suppliers (INV-F-021)."""
    # Add test suppliers
    supplier_manager.add_supplier(
        name="Supplier 1",
        contact_person="Contact 1"
    )
    supplier_manager.add_supplier(
        name="Supplier 2",
        contact_person="Contact 2"
    )

    # Test listing suppliers
    suppliers = supplier_manager.list_suppliers()
    assert len(suppliers) == 2
    assert suppliers[0].name == "Supplier 1"
    assert suppliers[1].name == "Supplier 2"

def test_update_supplier(supplier_manager):
    """Test updating supplier details."""
    # Add initial supplier
    supplier = supplier_manager.add_supplier(
        name="Original Name",
        contact_person="Original Contact",
        email="original@example.com",
        phone="123-456-7890"
    )

    # Test partial update
    updated = supplier_manager.update_supplier(
        supplier_id=supplier.id,
        name="Updated Name",
        email="updated@example.com"
    )
    assert updated.name == "Updated Name"
    assert updated.email == "updated@example.com"
    assert updated.contact_person == "Original Contact"  # Unchanged
    assert updated.phone == "123-456-7890"  # Unchanged

    # Test non-existent supplier
    with pytest.raises(SupplierError, match="not found"):
        supplier_manager.update_supplier(supplier_id=9999, name="Test")

def test_get_supplier(supplier_manager):
    """Test retrieving a supplier by ID."""
    # Add test supplier
    original = supplier_manager.add_supplier(
        name="Test Supplier",
        contact_person="Test Contact"
    )

    # Test successful retrieval
    retrieved = supplier_manager.get_supplier(original.id)
    assert retrieved.id == original.id
    assert retrieved.name == original.name
    assert retrieved.contact_person == original.contact_person

    # Test non-existent supplier
    assert supplier_manager.get_supplier(9999) is None