"""Product management module for the Inventory Management System."""
from dataclasses import dataclass
from typing import List, Optional
from decimal import Decimal, InvalidOperation as DecimalInvalidOperation
import logging

from .storage import Database, DatabaseError
from .config import MIN_STOCK_THRESHOLD, CRITICAL_STOCK_THRESHOLD

logger = logging.getLogger(__name__)

@dataclass
class Product:
    """Represents a product in the inventory."""
    sku: str
    name: str
    description: Optional[str]
    price: Decimal
    stock_quantity: int
    created_at: Optional[str] = None

class ProductError(Exception):
    """Raised when a product operation fails."""
    pass

class ProductManager:
    """Manages product operations in the inventory system."""
    def __init__(self, db: Database):
        self.db = db

    def add_product(self, 
                   sku: str, 
                   name: str, 
                   price: Decimal, 
                   initial_stock: int = 0,
                   description: Optional[str] = None) -> Product:
        """
        Add a new product to the inventory.
        
        Args:
            sku: Unique product identifier
            name: Product name
            price: Product price
            initial_stock: Initial stock quantity (default: 0)
            description: Optional product description
        
        Returns:
            Product: The created product
        
        Raises:
            ProductError: If product creation fails
        """
        # Validate SKU uniqueness
        existing = self.get_product(sku)
        if existing:
            raise ProductError(f"Product with SKU '{sku}' already exists")

        # Validate inputs
        if not sku or not name:
            raise ProductError("SKU and name are required")
        if not isinstance(price, Decimal):
            try:
                price = Decimal(str(price))
            except (TypeError, ValueError, DecimalInvalidOperation):
                raise ProductError("Invalid price format")
        if price < Decimal('0'):
            raise ProductError("Price cannot be negative")
        if initial_stock < 0:
            raise ProductError("Initial stock cannot be negative")

        try:
            query = """
            INSERT INTO products (sku, name, description, price, stock_quantity)
            VALUES (?, ?, ?, ?, ?)
            """
            self.db.execute(query, (sku, name, description, float(price), initial_stock))
            self.db.commit()
            
            return self.get_product(sku)  # Return the newly created product
        except DatabaseError as e:
            logger.error(f"Failed to add product {sku}: {e}")
            raise ProductError(f"Failed to add product: {e}")

    def get_product(self, sku: str) -> Optional[Product]:
        """
        Get a product by SKU.
        
        Args:
            sku: Product SKU to retrieve
            
        Returns:
            Optional[Product]: The product if found, None otherwise
        """
        try:
            query = "SELECT * FROM products WHERE sku = ?"
            row = self.db.fetch_one(query, (sku,))
            if row:
                return Product(
                    sku=row['sku'],
                    name=row['name'],
                    description=row['description'],
                    price=Decimal(str(row['price'])),
                    stock_quantity=row['stock_quantity'],
                    created_at=row['created_at']
                )
            return None
        except DatabaseError as e:
            logger.error(f"Failed to get product {sku}: {e}")
            raise ProductError(f"Failed to get product: {e}")

    def list_products(self) -> List[Product]:
        """
        List all products in inventory.
        
        Returns:
            List[Product]: List of all products
        """
        try:
            query = "SELECT * FROM products ORDER BY name"
            rows = self.db.fetch_all(query)
            return [
                Product(
                    sku=row['sku'],
                    name=row['name'],
                    description=row['description'],
                    price=Decimal(str(row['price'])),
                    stock_quantity=row['stock_quantity'],
                    created_at=row['created_at']
                )
                for row in rows
            ]
        except DatabaseError as e:
            logger.error(f"Failed to list products: {e}")
            raise ProductError(f"Failed to list products: {e}")

    def update_stock(self, sku: str, quantity_change: int) -> Product:
        """
        Update stock quantity for a product.
        
        Args:
            sku: Product SKU
            quantity_change: Amount to add (positive) or remove (negative)
            
        Returns:
            Product: Updated product
            
        Raises:
            ProductError: If update fails or would result in negative stock
        """
        try:
            product = self.get_product(sku)
            if not product:
                raise ProductError(f"Product with SKU '{sku}' not found")

            new_quantity = product.stock_quantity + quantity_change
            if new_quantity < 0:
                raise ProductError("Stock update would result in negative quantity")

            query = """
            UPDATE products 
            SET stock_quantity = ?
            WHERE sku = ?
            """
            self.db.execute(query, (new_quantity, sku))
            self.db.commit()

            return self.get_product(sku)  # Return updated product
        except DatabaseError as e:
            logger.error(f"Failed to update stock for product {sku}: {e}")
            raise ProductError(f"Failed to update stock: {e}")

    def get_low_stock_products(self) -> List[Product]:
        """
        Get list of products with stock below minimum threshold.
        
        Returns:
            List[Product]: Products with low stock
        """
        try:
            query = """
            SELECT * FROM products 
            WHERE stock_quantity <= ? 
            ORDER BY stock_quantity
            """
            rows = self.db.fetch_all(query, (MIN_STOCK_THRESHOLD,))
            return [
                Product(
                    sku=row['sku'],
                    name=row['name'],
                    description=row['description'],
                    price=Decimal(str(row['price'])),
                    stock_quantity=row['stock_quantity'],
                    created_at=row['created_at']
                )
                for row in rows
            ]
        except DatabaseError as e:
            logger.error("Failed to get low stock products: {e}")
            raise ProductError(f"Failed to get low stock products: {e}")

    def get_critical_stock_products(self) -> List[Product]:
        """
        Get list of products with critically low stock.
        
        Returns:
            List[Product]: Products with critically low stock
        """
        try:
            query = """
            SELECT * FROM products 
            WHERE stock_quantity <= ? 
            ORDER BY stock_quantity
            """
            rows = self.db.fetch_all(query, (CRITICAL_STOCK_THRESHOLD,))
            return [
                Product(
                    sku=row['sku'],
                    name=row['name'],
                    description=row['description'],
                    price=Decimal(str(row['price'])),
                    stock_quantity=row['stock_quantity'],
                    created_at=row['created_at']
                )
                for row in rows
            ]
        except DatabaseError as e:
            logger.error("Failed to get critical stock products: {e}")
            raise ProductError(f"Failed to get critical stock products: {e}")