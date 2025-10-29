"""Command-line interface for the Inventory Management System."""
import sys
from typing import Optional
import logging
from decimal import Decimal
import getpass

from .storage import Database
from .product_manager import ProductManager, ProductError
from .supplier_manager import SupplierManager, SupplierError
from .order_processor import OrderProcessor, OrderError
from .auth import AuthManager, AuthenticationError
from .backup_security import BackupManager, BackupError
from .logger import AdminLogger, setup_logging
from .config import DB_PATH, LOG_FILE, LOG_FORMAT

logger = logging.getLogger(__name__)

class CLI:
    """Main CLI interface for the Inventory Management System."""
    def __init__(self):
        setup_logging(LOG_FILE, LOG_FORMAT)
        self.db = Database(DB_PATH)
        self.auth_manager = AuthManager()
        self.product_manager = ProductManager(self.db)
        self.supplier_manager = SupplierManager(self.db)
        self.order_processor = OrderProcessor(self.db, self.product_manager)
        self.backup_manager = BackupManager(self.db)
        self.admin_logger = AdminLogger(self.db)

    def start(self) -> None:
        """Start the CLI interface."""
        try:
            self.db.connect()
            print("Welcome to the Inventory Management System")
            self._main_menu()
        except Exception as e:
            logger.error(f"Application error: {e}")
            print(f"Error: {e}")
        finally:
            self.db.disconnect()

    def _main_menu(self) -> None:
        """Display and handle main menu options."""
        while True:
            print("\nMain Menu:")
            print("1. Products")
            print("2. Orders")
            print("3. Suppliers")
            print("4. Admin")
            print("5. Exit")

            choice = input("\nEnter your choice (1-5): ")

            if choice == "1":
                self._product_menu()
            elif choice == "2":
                self._order_menu()
            elif choice == "3":
                self._supplier_menu()
            elif choice == "4":
                self._admin_menu()
            elif choice == "5":
                print("Thank you for using IMS. Goodbye!")
                break
            else:
                print("Invalid choice. Please try again.")

    def _product_menu(self) -> None:
        """Handle product management menu."""
        while True:
            print("\nProduct Management:")
            print("1. Add new product")
            print("2. List all products")
            print("3. Update stock")
            print("4. View low stock products")
            print("5. Back to main menu")

            choice = input("\nEnter your choice (1-5): ")

            try:
                if choice == "1":
                    self._add_product()
                elif choice == "2":
                    self._list_products()
                elif choice == "3":
                    self._update_stock()
                elif choice == "4":
                    self._show_low_stock()
                elif choice == "5":
                    break
                else:
                    print("Invalid choice. Please try again.")
            except (ProductError, ValueError) as e:
                print(f"Error: {e}")

    def _order_menu(self) -> None:
        """Handle order management menu."""
        while True:
            print("\nOrder Management:")
            print("1. Create sales order")
            print("2. Create purchase order")
            print("3. List orders")
            print("4. Back to main menu")

            choice = input("\nEnter your choice (1-4): ")

            try:
                if choice == "1":
                    self._create_sales_order()
                elif choice == "2":
                    self._create_purchase_order()
                elif choice == "3":
                    self._list_orders()
                elif choice == "4":
                    break
                else:
                    print("Invalid choice. Please try again.")
            except (OrderError, ValueError) as e:
                print(f"Error: {e}")

    def _supplier_menu(self) -> None:
        """Handle supplier management menu."""
        while True:
            print("\nSupplier Management:")
            print("1. Add new supplier")
            print("2. List suppliers")
            print("3. Update supplier")
            print("4. Back to main menu")

            choice = input("\nEnter your choice (1-4): ")

            try:
                if choice == "1":
                    self._add_supplier()
                elif choice == "2":
                    self._list_suppliers()
                elif choice == "3":
                    self._update_supplier()
                elif choice == "4":
                    break
                else:
                    print("Invalid choice. Please try again.")
            except (SupplierError, ValueError) as e:
                print(f"Error: {e}")

    def _admin_menu(self) -> None:
        """Handle admin functions menu."""
        # Require authentication
        if not self._authenticate():
            return

        while True:
            print("\nAdmin Functions:")
            print("1. Create backup")
            print("2. Restore from backup")
            print("3. List backups")
            print("4. View admin logs")
            print("5. Back to main menu")

            choice = input("\nEnter your choice (1-5): ")

            try:
                if choice == "1":
                    self._create_backup()
                elif choice == "2":
                    self._restore_backup()
                elif choice == "3":
                    self._list_backups()
                elif choice == "4":
                    self._view_admin_logs()
                elif choice == "5":
                    break
                else:
                    print("Invalid choice. Please try again.")
            except (BackupError, AuthenticationError) as e:
                print(f"Error: {e}")

    def _authenticate(self) -> bool:
        """Authenticate admin user."""
        print("\nAdmin Authentication Required")
        username = input("Username: ")
        password = getpass.getpass("Password: ")

        try:
            self.auth_manager.authenticate(username, password)
            return True
        except AuthenticationError as e:
            print(f"Authentication failed: {e}")
            return False

    def _add_product(self) -> None:
        """Handle adding a new product."""
        print("\nAdd New Product")
        sku = input("SKU: ")
        name = input("Name: ")
        description = input("Description (optional): ") or None
        price = Decimal(input("Price: "))
        stock = int(input("Initial stock quantity: "))

        product = self.product_manager.add_product(
            sku=sku,
            name=name,
            description=description,
            price=price,
            initial_stock=stock
        )
        print(f"\nProduct added successfully: {product.name} (SKU: {product.sku})")

    def _list_products(self) -> None:
        """Display all products."""
        products = self.product_manager.list_products()
        if not products:
            print("\nNo products found.")
            return

        print("\nProduct List:")
        print("-" * 70)
        print(f"{'SKU':<10} {'Name':<20} {'Price':<10} {'Stock':<8} {'Description':<20}")
        print("-" * 70)
        for product in products:
            desc = (product.description or "")[:20]
            print(f"{product.sku:<10} {product.name[:20]:<20} "
                  f"${float(product.price):<9.2f} {product.stock_quantity:<8} {desc:<20}")

    def _update_stock(self) -> None:
        """Handle stock quantity updates."""
        sku = input("\nEnter product SKU: ")
        product = self.product_manager.get_product(sku)
        if not product:
            print(f"Product with SKU '{sku}' not found.")
            return

        print(f"Current stock for {product.name}: {product.stock_quantity}")
        change = int(input("Enter quantity change (+/-): "))
        
        updated = self.product_manager.update_stock(sku, change)
        print(f"Stock updated. New quantity: {updated.stock_quantity}")

    def _show_low_stock(self) -> None:
        """Display products with low stock."""
        products = self.product_manager.get_low_stock_products()
        if not products:
            print("\nNo products with low stock.")
            return

        print("\nLow Stock Products:")
        print("-" * 70)
        print(f"{'SKU':<10} {'Name':<20} {'Stock':<8} {'Min Required':<12}")
        print("-" * 70)
        for product in products:
            print(f"{product.sku:<10} {product.name[:20]:<20} "
                  f"{product.stock_quantity:<8} {'10':<12}")

    def _create_sales_order(self) -> None:
        """Handle creating a sales order."""
        sku = input("\nEnter product SKU: ")
        product = self.product_manager.get_product(sku)
        if not product:
            print(f"Product with SKU '{sku}' not found.")
            return

        print(f"Available stock for {product.name}: {product.stock_quantity}")
        quantity = int(input("Enter quantity to sell: "))

        order = self.order_processor.create_sales_order(sku, quantity)
        print(f"\nSales order created successfully. Order ID: {order.id}")
        print(f"Total price: ${float(order.price):.2f}")

    def _create_purchase_order(self) -> None:
        """Handle creating a purchase order."""
        sku = input("\nEnter product SKU: ")
        product = self.product_manager.get_product(sku)
        if not product:
            print(f"Product with SKU '{sku}' not found.")
            return

        quantity = int(input("Enter quantity to purchase: "))
        price = Decimal(input("Enter total purchase price: "))

        order = self.order_processor.create_purchase_order(sku, quantity, price)
        print(f"\nPurchase order created successfully. Order ID: {order.id}")

    def _list_orders(self) -> None:
        """Display order list with filtering options."""
        print("\nOrder Type:")
        print("1. All orders")
        print("2. Sales orders only")
        print("3. Purchase orders only")

        choice = input("\nEnter your choice (1-3): ")
        order_type = None
        if choice == "2":
            order_type = "SALE"
        elif choice == "3":
            order_type = "PURCHASE"

        orders = self.order_processor.list_orders(order_type)
        if not orders:
            print("\nNo orders found.")
            return

        print("\nOrder List:")
        print("-" * 80)
        print(f"{'ID':<5} {'Type':<10} {'SKU':<10} {'Quantity':<10} "
              f"{'Price':<10} {'Date':<20}")
        print("-" * 80)
        for order in orders:
            print(f"{order.id:<5} {order.order_type:<10} {order.product_sku:<10} "
                  f"{order.quantity:<10} ${float(order.price):<9.2f} "
                  f"{order.order_date[:19]:<20}")

    def _add_supplier(self) -> None:
        """Handle adding a new supplier."""
        print("\nAdd New Supplier")
        name = input("Company name: ")
        contact = input("Contact person (optional): ") or None
        email = input("Email (optional): ") or None
        phone = input("Phone (optional): ") or None

        supplier = self.supplier_manager.add_supplier(
            name=name,
            contact_person=contact,
            email=email,
            phone=phone
        )
        print(f"\nSupplier added successfully. ID: {supplier.id}")

    def _list_suppliers(self) -> None:
        """Display all suppliers."""
        suppliers = self.supplier_manager.list_suppliers()
        if not suppliers:
            print("\nNo suppliers found.")
            return

        print("\nSupplier List:")
        print("-" * 80)
        print(f"{'ID':<5} {'Name':<20} {'Contact':<20} {'Email':<20} {'Phone':<15}")
        print("-" * 80)
        for supplier in suppliers:
            print(f"{supplier.id:<5} {supplier.name[:20]:<20} "
                  f"{(supplier.contact_person or '')[:20]:<20} "
                  f"{(supplier.email or '')[:20]:<20} "
                  f"{(supplier.phone or '')[:15]:<15}")

    def _update_supplier(self) -> None:
        """Handle updating supplier details."""
        supplier_id = int(input("\nEnter supplier ID: "))
        supplier = self.supplier_manager.get_supplier(supplier_id)
        if not supplier:
            print(f"Supplier with ID {supplier_id} not found.")
            return

        print("\nCurrent details:")
        print(f"Name: {supplier.name}")
        print(f"Contact: {supplier.contact_person or 'N/A'}")
        print(f"Email: {supplier.email or 'N/A'}")
        print(f"Phone: {supplier.phone or 'N/A'}")

        print("\nEnter new details (leave blank to keep current):")
        name = input("Name: ") or None
        contact = input("Contact person: ") or None
        email = input("Email: ") or None
        phone = input("Phone: ") or None

        updated = self.supplier_manager.update_supplier(
            supplier_id=supplier_id,
            name=name,
            contact_person=contact,
            email=email,
            phone=phone
        )
        print(f"\nSupplier {updated.id} updated successfully.")

    def _create_backup(self) -> None:
        """Handle creating an encrypted backup."""
        print("\nCreate Encrypted Backup")
        passphrase = getpass.getpass("Enter encryption passphrase: ")
        confirm = getpass.getpass("Confirm passphrase: ")

        if passphrase != confirm:
            print("Passphrases do not match.")
            return

        backup_path = self.backup_manager.create_backup(passphrase)
        print(f"\nBackup created successfully: {backup_path}")
        
        # Log admin action
        self.admin_logger.log_action(
            self.auth_manager.get_current_session().username,
            "create_backup",
            {"backup_file": str(backup_path)}
        )

    def _restore_backup(self) -> None:
        """Handle restoring from backup."""
        backups = self.backup_manager.list_backups()
        if not backups:
            print("\nNo backups available.")
            return

        print("\nAvailable backups:")
        for i, backup in enumerate(backups, 1):
            print(f"{i}. {backup['filename']} ({backup['created']})")

        try:
            choice = int(input("\nSelect backup to restore (number): ")) - 1
            if choice < 0 or choice >= len(backups):
                print("Invalid selection.")
                return

            backup = backups[choice]
            passphrase = getpass.getpass("Enter backup passphrase: ")

            self.backup_manager.restore_from_backup(
                Path(backup['path']),
                passphrase
            )
            print("\nBackup restored successfully.")
            
            # Log admin action
            self.admin_logger.log_action(
                self.auth_manager.get_current_session().username,
                "restore_backup",
                {"backup_file": backup['filename']}
            )

        except ValueError:
            print("Invalid input.")
        except BackupError as e:
            print(f"Restore failed: {e}")

    def _list_backups(self) -> None:
        """Display available backups."""
        backups = self.backup_manager.list_backups()
        if not backups:
            print("\nNo backups found.")
            return

        print("\nAvailable Backups:")
        print("-" * 80)
        print(f"{'Filename':<30} {'Created':<25} {'Size':<10}")
        print("-" * 80)
        for backup in backups:
            size_mb = backup['size'] / (1024 * 1024)
            print(f"{backup['filename']:<30} {backup['created']:<25} "
                  f"{size_mb:.2f}MB")

    def _view_admin_logs(self) -> None:
        """Display admin action logs."""
        try:
            query = """
            SELECT * FROM admin_logs 
            ORDER BY timestamp DESC 
            LIMIT 50
            """
            logs = self.db.fetch_all(query)

            if not logs:
                print("\nNo admin logs found.")
                return

            print("\nRecent Admin Actions:")
            print("-" * 80)
            print(f"{'Timestamp':<20} {'User':<15} {'Action':<20} {'Details':<25}")
            print("-" * 80)
            for log in logs:
                details = log['details'][:25] if log['details'] else ''
                print(f"{log['timestamp'][:19]:<20} {log['user']:<15} "
                      f"{log['action']:<20} {details:<25}")

        except Exception as e:
            print(f"Error retrieving logs: {e}")

def main() -> None:
    """Main entry point for the CLI."""
    try:
        cli = CLI()
        cli.start()
    except KeyboardInterrupt:
        print("\nProgram terminated by user.")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Unhandled exception: {e}")
        print(f"\nUnexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()