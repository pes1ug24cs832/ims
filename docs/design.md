# Design Documentation

## Architecture Overview

The Inventory Management System (IMS) is designed using a layered architecture pattern with clear separation of concerns:

```
+----------------+
|      CLI      |  User Interface Layer
+----------------+
|   Managers    |  Business Logic Layer
+----------------+
|    Storage    |  Data Access Layer
+----------------+
|   Database    |  Persistence Layer
+----------------+
```

### Components

1. **User Interface Layer** (`cli.py`)
   - Command-line interface handling user input/output
   - Menu-driven navigation
   - Input validation and error display
   - Session management

2. **Business Logic Layer**
   - Product Manager (`product_manager.py`): Product CRUD, stock management
   - Order Processor (`order_processor.py`): Sales/purchase order processing
   - Supplier Manager (`supplier_manager.py`): Supplier CRUD operations
   - Auth Manager (`auth.py`): Authentication and authorization
   - Backup Manager (`backup_security.py`): Backup creation and restoration

3. **Data Access Layer** (`storage.py`)
   - Database connection management
   - SQL query execution
   - Transaction handling
   - Error handling

4. **Persistence Layer**
   - SQLite database
   - File-based backups
   - Admin logs
   - CSV data for seeding

## Design Patterns & Principles

### SOLID Principles

1. **Single Responsibility**
   - Each manager class handles one aspect (products, orders, suppliers)
   - Separate modules for auth, backup, logging

2. **Open/Closed**
   - Manager classes can be extended without modification
   - Database class can support different storage backends

3. **Liskov Substitution**
   - All manager classes follow consistent patterns
   - Error handling is consistent across modules

4. **Interface Segregation**
   - Clear, focused interfaces for each manager
   - Minimal dependencies between components

5. **Dependency Inversion**
   - High-level modules don't depend on low-level modules
   - Database injected into managers

### Design Patterns

1. **Repository Pattern**
   - Database class abstracts data access
   - Consistent CRUD operations across entities

2. **Factory Method**
   - Database connection management
   - Session creation in auth module

3. **Strategy Pattern**
   - Backup encryption strategies
   - Authentication methods

4. **Command Pattern**
   - CLI menu actions
   - Order processing operations

## Security Design

### Authentication & Authorization

1. **Password Security**
   - bcrypt for password hashing
   - Configurable hash rounds
   - No plaintext storage

2. **Session Management**
   - In-memory session tracking
   - Admin privileges enforcement
   - Session timeout (configurable)

3. **Backup Security**
   - AES encryption for backups
   - Key derivation from passphrase
   - Secure file permissions

### Audit & Logging

1. **Admin Action Logging**
   - Timestamped entries
   - User identification
   - Action details
   - Protected log storage

2. **Error Logging**
   - Structured error messages
   - Stack traces in development
   - Log rotation

## Data Model

### Entity Relationships

```
Product <--> Order --> Supplier
   |          |          |
   v          v          v
Stock     Tracking    Contacts
```

### Database Schema

```sql
products (
    sku TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    price DECIMAL(10,2),
    stock_quantity INTEGER,
    created_at TIMESTAMP
)

orders (
    id INTEGER PRIMARY KEY,
    order_type TEXT,
    product_sku TEXT,
    quantity INTEGER,
    price DECIMAL(10,2),
    order_date TIMESTAMP,
    FOREIGN KEY (product_sku) REFERENCES products(sku)
)

suppliers (
    id INTEGER PRIMARY KEY,
    name TEXT,
    contact_person TEXT,
    email TEXT,
    phone TEXT,
    created_at TIMESTAMP
)

admin_logs (
    id INTEGER PRIMARY KEY,
    user TEXT,
    action TEXT,
    details TEXT,
    timestamp TIMESTAMP
)
```

## Error Handling

### Strategy

1. **Domain-Specific Errors**
   - ProductError
   - OrderError
   - SupplierError
   - Custom error messages

2. **Technical Errors**
   - DatabaseError
   - AuthenticationError
   - BackupError
   - Wrapped underlying errors

3. **Error Flow**
   - Errors caught at business logic layer
   - User-friendly messages in CLI
   - Technical details in logs

## Performance Considerations

1. **Database Optimization**
   - Appropriate indexes
   - Transaction management
   - Connection pooling

2. **Memory Management**
   - Cursor result streaming
   - Large dataset pagination
   - Resource cleanup

3. **Response Time**
   - Command execution ≤ 2 seconds
   - Async backup creation
   - Batched operations

## Testing Strategy

1. **Unit Tests**
   - Individual component testing
   - Mock dependencies
   - Edge case coverage

2. **Integration Tests**
   - Component interaction testing
   - Database operations
   - End-to-end flows

3. **System Tests**
   - CLI interaction testing
   - Performance testing
   - Security testing

## Deployment

### Package Structure

```
ims/
├── src/           # Source code
├── tests/         # Test suites
├── docs/          # Documentation
├── sample_data/   # Seed data
└── reports/       # Test & analysis reports
```

### Requirements

- Python 3.10+
- SQLite 3
- Required packages in requirements.txt
- Development tools in requirements-dev.txt