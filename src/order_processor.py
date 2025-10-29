"""Order processing module for the Inventory Management System."""
from dataclasses import dataclass
from typing import List, Optional
from decimal import Decimal
from datetime import datetime
import logging

from .storage import Database, DatabaseError
from .product_manager import ProductManager, ProductError

logger = logging.getLogger(__name__)

@dataclass
class Order:
    """Represents an order in the system."""
    id: Optional[int]
    order_type: str  # 'SALE' or 'PURCHASE'
    product_sku: str
    quantity: int
    price: Decimal
    order_date: Optional[str] = None

class OrderError(Exception):
    """Raised when an order operation fails."""
    pass

class OrderProcessor:
    """Processes sales and purchase orders."""
    def __init__(self, db: Database, product_manager: ProductManager):
        self.db = db
        self.product_manager = product_manager

    def create_sales_order(self, product_sku: str, quantity: int) -> Order:
        """
        Create a sales order and update stock.
        
        Args:
            product_sku: Product SKU to sell
            quantity: Quantity to sell
            
        Returns:
            Order: Created sales order
            
        Raises:
            OrderError: If order creation fails or insufficient stock
        """
        if quantity <= 0:
            raise OrderError("Order quantity must be positive")

        try:
            # Get product and check stock
            product = self.product_manager.get_product(product_sku)
            if not product:
                raise OrderError(f"Product with SKU '{product_sku}' not found")

            if product.stock_quantity < quantity:
                raise OrderError(
                    f"Insufficient stock for product '{product_sku}'. "
                    f"Available: {product.stock_quantity}, Requested: {quantity}"
                )

            # Create order
            query = """
            INSERT INTO orders (order_type, product_sku, quantity, price)
            VALUES ('SALE', ?, ?, ?)
            """
            cursor = self.db.execute(
                query,
                (product_sku, quantity, float(product.price * quantity))
            )
            order_id = cursor.lastrowid

            # Update stock
            try:
                self.product_manager.update_stock(product_sku, -quantity)
                self.db.commit()
            except ProductError as e:
                self.db.rollback()
                raise OrderError(f"Failed to update stock: {e}")

            # Return created order
            return self.get_order(order_id)
        except DatabaseError as e:
            logger.error(f"Failed to create sales order: {e}")
            self.db.rollback()
            raise OrderError(f"Failed to create sales order: {e}")

    def create_purchase_order(self, product_sku: str, quantity: int, price: Decimal) -> Order:
        """
        Create a purchase order and update stock.
        
        Args:
            product_sku: Product SKU to purchase
            quantity: Quantity to purchase
            price: Total purchase price
            
        Returns:
            Order: Created purchase order
        """
        if quantity <= 0:
            raise OrderError("Order quantity must be positive")
        if price < 0:
            raise OrderError("Price cannot be negative")

        try:
            # Verify product exists
            if not self.product_manager.get_product(product_sku):
                raise OrderError(f"Product with SKU '{product_sku}' not found")

            # Create order
            query = """
            INSERT INTO orders (order_type, product_sku, quantity, price)
            VALUES ('PURCHASE', ?, ?, ?)
            """
            cursor = self.db.execute(query, (product_sku, quantity, float(price)))
            order_id = cursor.lastrowid

            # Update stock
            try:
                self.product_manager.update_stock(product_sku, quantity)
                self.db.commit()
            except ProductError as e:
                self.db.rollback()
                raise OrderError(f"Failed to update stock: {e}")

            # Return created order
            return self.get_order(order_id)
        except DatabaseError as e:
            logger.error(f"Failed to create purchase order: {e}")
            self.db.rollback()
            raise OrderError(f"Failed to create purchase order: {e}")

    def get_order(self, order_id: int) -> Optional[Order]:
        """Get an order by ID."""
        try:
            query = "SELECT * FROM orders WHERE id = ?"
            row = self.db.fetch_one(query, (order_id,))
            if row:
                return Order(
                    id=row['id'],
                    order_type=row['order_type'],
                    product_sku=row['product_sku'],
                    quantity=row['quantity'],
                    price=Decimal(str(row['price'])),
                    order_date=row['order_date']
                )
            return None
        except DatabaseError as e:
            logger.error(f"Failed to get order {order_id}: {e}")
            raise OrderError(f"Failed to get order: {e}")

    def list_orders(self, order_type: Optional[str] = None) -> List[Order]:
        """
        List all orders, optionally filtered by type.
        
        Args:
            order_type: Optional filter ('SALE' or 'PURCHASE')
            
        Returns:
            List[Order]: List of orders
        """
        try:
            if order_type:
                query = "SELECT * FROM orders WHERE order_type = ? ORDER BY order_date DESC"
                rows = self.db.fetch_all(query, (order_type,))
            else:
                query = "SELECT * FROM orders ORDER BY order_date DESC"
                rows = self.db.fetch_all(query)

            return [
                Order(
                    id=row['id'],
                    order_type=row['order_type'],
                    product_sku=row['product_sku'],
                    quantity=row['quantity'],
                    price=Decimal(str(row['price'])),
                    order_date=row['order_date']
                )
                for row in rows
            ]
        except DatabaseError as e:
            logger.error(f"Failed to list orders: {e}")
            raise OrderError(f"Failed to list orders: {e}")