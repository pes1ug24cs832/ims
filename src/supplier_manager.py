"""Supplier management module for the Inventory Management System."""
from dataclasses import dataclass
from typing import List, Optional
import logging
import re

from .storage import Database, DatabaseError

logger = logging.getLogger(__name__)

@dataclass
class Supplier:
    """Represents a supplier in the system."""
    id: Optional[int]
    name: str
    contact_person: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    created_at: Optional[str] = None

class SupplierError(Exception):
    """Raised when a supplier operation fails."""
    pass

class SupplierManager:
    """Manages supplier operations."""
    def __init__(self, db: Database):
        self.db = db
        self._email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

    def _validate_email(self, email: Optional[str]) -> None:
        """Validate email format if provided."""
        if email and not self._email_pattern.match(email):
            raise SupplierError("Invalid email format")

    def add_supplier(self, 
                    name: str, 
                    contact_person: Optional[str] = None,
                    email: Optional[str] = None,
                    phone: Optional[str] = None) -> Supplier:
        """
        Add a new supplier to the system.
        
        Args:
            name: Supplier company name
            contact_person: Optional contact person name
            email: Optional contact email
            phone: Optional contact phone
            
        Returns:
            Supplier: Created supplier
            
        Raises:
            SupplierError: If supplier creation fails
        """
        if not name:
            raise SupplierError("Supplier name is required")

        self._validate_email(email)

        try:
            query = """
            INSERT INTO suppliers (name, contact_person, email, phone)
            VALUES (?, ?, ?, ?)
            """
            cursor = self.db.execute(query, (name, contact_person, email, phone))
            supplier_id = cursor.lastrowid
            self.db.commit()

            return self.get_supplier(supplier_id)
        except DatabaseError as e:
            logger.error(f"Failed to add supplier {name}: {e}")
            raise SupplierError(f"Failed to add supplier: {e}")

    def get_supplier(self, supplier_id: int) -> Optional[Supplier]:
        """
        Get a supplier by ID.
        
        Args:
            supplier_id: Supplier ID to retrieve
            
        Returns:
            Optional[Supplier]: The supplier if found, None otherwise
        """
        try:
            query = "SELECT * FROM suppliers WHERE id = ?"
            row = self.db.fetch_one(query, (supplier_id,))
            if row:
                return Supplier(
                    id=row['id'],
                    name=row['name'],
                    contact_person=row['contact_person'],
                    email=row['email'],
                    phone=row['phone'],
                    created_at=row['created_at']
                )
            return None
        except DatabaseError as e:
            logger.error(f"Failed to get supplier {supplier_id}: {e}")
            raise SupplierError(f"Failed to get supplier: {e}")

    def list_suppliers(self) -> List[Supplier]:
        """
        List all suppliers.
        
        Returns:
            List[Supplier]: List of all suppliers
        """
        try:
            query = "SELECT * FROM suppliers ORDER BY name"
            rows = self.db.fetch_all(query)
            return [
                Supplier(
                    id=row['id'],
                    name=row['name'],
                    contact_person=row['contact_person'],
                    email=row['email'],
                    phone=row['phone'],
                    created_at=row['created_at']
                )
                for row in rows
            ]
        except DatabaseError as e:
            logger.error(f"Failed to list suppliers: {e}")
            raise SupplierError(f"Failed to list suppliers: {e}")

    def update_supplier(self, 
                       supplier_id: int, 
                       name: Optional[str] = None,
                       contact_person: Optional[str] = None,
                       email: Optional[str] = None,
                       phone: Optional[str] = None) -> Supplier:
        """
        Update supplier details.
        
        Args:
            supplier_id: ID of supplier to update
            name: Optional new name
            contact_person: Optional new contact person
            email: Optional new email
            phone: Optional new phone
            
        Returns:
            Supplier: Updated supplier
            
        Raises:
            SupplierError: If update fails
        """
        if email is not None:
            self._validate_email(email)

        try:
            # Get current supplier
            supplier = self.get_supplier(supplier_id)
            if not supplier:
                raise SupplierError(f"Supplier with ID {supplier_id} not found")

            # Build update query dynamically
            updates = []
            params = []
            if name is not None:
                updates.append("name = ?")
                params.append(name)
            if contact_person is not None:
                updates.append("contact_person = ?")
                params.append(contact_person)
            if email is not None:
                updates.append("email = ?")
                params.append(email)
            if phone is not None:
                updates.append("phone = ?")
                params.append(phone)

            if not updates:
                return supplier  # No updates requested

            query = f"""
            UPDATE suppliers 
            SET {', '.join(updates)}
            WHERE id = ?
            """
            params.append(supplier_id)
            
            self.db.execute(query, tuple(params))
            self.db.commit()

            return self.get_supplier(supplier_id)
        except DatabaseError as e:
            logger.error(f"Failed to update supplier {supplier_id}: {e}")
            raise SupplierError(f"Failed to update supplier: {e}")