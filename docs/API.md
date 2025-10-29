# Module API Documentation

## Core Modules

### Product Manager (`src/product_manager.py`)

```python
class ProductManager:
    def add_product(sku: str, name: str, price: Decimal, initial_stock: int = 0,
                   description: Optional[str] = None) -> Product
    def get_product(sku: str) -> Optional[Product]
    def list_products() -> List[Product]
    def update_stock(sku: str, quantity_change: int) -> Product
    def get_low_stock_products() -> List[Product]
    def get_critical_stock_products() -> List[Product]
```

### Order Processor (`src/order_processor.py`)

```python
class OrderProcessor:
    def create_sales_order(product_sku: str, quantity: int) -> Order
    def create_purchase_order(product_sku: str, quantity: int, price: Decimal) -> Order
    def get_order(order_id: int) -> Optional[Order]
    def list_orders(order_type: Optional[str] = None) -> List[Order]
```

### Supplier Manager (`src/supplier_manager.py`)

```python
class SupplierManager:
    def add_supplier(name: str, contact_person: Optional[str] = None,
                    email: Optional[str] = None, phone: Optional[str] = None) -> Supplier
    def get_supplier(supplier_id: int) -> Optional[Supplier]
    def list_suppliers() -> List[Supplier]
    def update_supplier(supplier_id: int, **kwargs) -> Supplier
```

## Storage & Security

### Database (`src/storage.py`)

```python
class Database:
    def connect() -> None
    def disconnect() -> None
    def execute(query: str, params: tuple = ()) -> sqlite3.Cursor
    def execute_many(query: str, params: List[tuple]) -> sqlite3.Cursor
    def commit() -> None
    def rollback() -> None
    def fetch_one(query: str, params: tuple = ()) -> Optional[Dict[str, Any]]
    def fetch_all(query: str, params: tuple = ()) -> List[Dict[str, Any]]
```

### Authentication (`src/auth.py`)

```python
class AuthManager:
    def authenticate(username: str, password: str) -> Session
    def get_current_session() -> Optional[Session]
    def require_admin() -> None
    def logout() -> None
```

### Backup & Security (`src/backup_security.py`)

```python
class BackupManager:
    def create_backup(passphrase: str) -> Path
    def restore_from_backup(backup_path: Path, passphrase: str) -> None
    def list_backups() -> List[Dict[str, Any]]

class DatabaseEncryptor:
    def encrypt_file(file_path: Path, passphrase: str) -> None
    def decrypt_file(encrypted_path: Path, output_path: Path, passphrase: str) -> None
```

## CLI Interface

### Command Line Interface (`src/cli.py`)

```python
class CLI:
    def start() -> None  # Main entry point
    def _main_menu() -> None  # Main menu handler
    def _product_menu() -> None  # Product management menu
    def _order_menu() -> None  # Order management menu
    def _supplier_menu() -> None  # Supplier management menu
    def _admin_menu() -> None  # Admin functions menu
```

## Data Models

### Product Model

```python
@dataclass
class Product:
    sku: str
    name: str
    description: Optional[str]
    price: Decimal
    stock_quantity: int
    created_at: Optional[str] = None
```

### Order Model

```python
@dataclass
class Order:
    id: Optional[int]
    order_type: str  # 'SALE' or 'PURCHASE'
    product_sku: str
    quantity: int
    price: Decimal
    order_date: Optional[str] = None
```

### Supplier Model

```python
@dataclass
class Supplier:
    id: Optional[int]
    name: str
    contact_person: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    created_at: Optional[str] = None
```

## Configuration

### Configuration Settings (`src/config.py`)

- Database path & backup settings
- Stock threshold values
- Security settings (hash rounds, encryption parameters)
- Logging configuration
- Sample data paths

## Error Types

- `ProductError`: Product-related operation failures
- `OrderError`: Order processing failures
- `SupplierError`: Supplier-related operation failures
- `DatabaseError`: Database operation failures
- `AuthenticationError`: Authentication/authorization failures
- `BackupError`: Backup/restore operation failures

## Usage Examples

### Adding a Product

```python
product_manager = ProductManager(db)
product = product_manager.add_product(
    sku="LAPTOP001",
    name="Business Laptop",
    price=Decimal("899.99"),
    initial_stock=10,
    description="15.6\" Business Laptop"
)
```

### Creating a Sales Order

```python
order_processor = OrderProcessor(db, product_manager)
order = order_processor.create_sales_order(
    product_sku="LAPTOP001",
    quantity=2
)
```

### Adding a Supplier

```python
supplier_manager = SupplierManager(db)
supplier = supplier_manager.add_supplier(
    name="TechCorp Inc",
    contact_person="John Smith",
    email="john.smith@techcorp.com",
    phone="555-0101"
)
```