# Requirements Traceability Matrix

## Functional Requirements

| Requirement ID | Description | Code Module | Test Case | Jira Story |
|---------------|-------------|-------------|-----------|------------|
| INV-F-001 | Add new product with SKU, name, initial stock | src/product_manager.py:add_product | tests/unit/test_product_manager.py:test_INV_F_001_add_product | INV-F-003 |
| INV-F-002 | View all products listing | src/product_manager.py:list_products | tests/unit/test_product_manager.py:test_INV_F_002_list_products | INV-F-002 |
| INV-F-003 | Update stock quantity | src/product_manager.py:update_stock | tests/unit/test_product_manager.py:test_INV_F_003_update_stock | INV-F-003 |
| INV-F-010 | Create sales order | src/order_processor.py:create_sales_order | tests/unit/test_order_processor.py:test_INV_F_010_create_sales_order | INV-F-010 |
| INV-F-011 | Prevent sales with insufficient stock | src/order_processor.py:create_sales_order | tests/unit/test_order_processor.py:test_INV_F_011_insufficient_stock | INV-F-011 |
| INV-F-012 | Create purchase order | src/order_processor.py:create_purchase_order | tests/unit/test_order_processor.py:test_INV_F_012_create_purchase_order | INV-F-017 |
| INV-F-020 | Add supplier with contact details | src/supplier_manager.py:add_supplier | tests/unit/test_supplier_manager.py:test_INV_F_020_add_supplier | INV-F-021 |
| INV-F-021 | Display suppliers list | src/supplier_manager.py:list_suppliers | tests/unit/test_supplier_manager.py:test_INV_F_021_list_suppliers | INV-F-021 |
| INV-F-034 | Low stock alerts | src/product_manager.py:get_low_stock_products | tests/unit/test_product_manager.py:test_get_low_stock_products | INV-34 |

## Non-Functional Requirements

| Requirement ID | Description | Implementation | Test Case | Jira Story |
|---------------|-------------|----------------|-----------|------------|
| INV-NF-001 | Command execution ≤ 2 seconds | src/cli.py | tests/system/test_cli_end_to_end.py:test_INV_NF_001_command_execution_time | INV-CI-01 |
| INV-NF-002 | Data persistence in SQLite | src/storage.py | tests/system/test_cli_end_to_end.py:test_INV_NF_002_data_persistence | INV-CI-01 |
| INV-NF-003 | Admin-only restricted functions | src/auth.py | tests/system/test_cli_end_to_end.py:test_INV_NF_003_admin_authentication | INV-SEC-01 |
| INV-NF-004 | Automated daily backup | src/backup_security.py | tests/system/test_cli_end_to_end.py:test_INV_NF_004_backup_creation | INV-BACKUP-01 |
| INV-NF-005 | Clear CLI menus and prompts | src/cli.py:CLI._*_menu methods | tests/system/test_cli_end_to_end.py | INV-CI-01 |

## Security Requirements

| Requirement ID | Description | Implementation | Test Case | Jira Story |
|---------------|-------------|----------------|-----------|------------|
| PRJ-SEC-001 | Password hashing | src/auth.py:hash_password | tests/system/test_cli_end_to_end.py:test_PRJ_SEC_001_password_hashing | INV-SEC-01 |
| PRJ-SEC-002 | Backup encryption | src/backup_security.py:DatabaseEncryptor | tests/integration/test_db_integration.py:test_db_integration_backup_restore | INV-BACKUP-01 |
| PRJ-SEC-003 | Action logging | src/logger.py:AdminLogger | tests/integration/test_db_integration.py | INV-LOG-01 |
| PRJ-SEC-004 | Data minimization | src/backup_security.py:BackupManager | tests/integration/test_db_integration.py | INV-BACKUP-01 |
| PRJ-SEC-005 | Backup folder permissions | src/backup_security.py:_ensure_backup_dir | tests/integration/test_db_integration.py | INV-BACKUP-01 |