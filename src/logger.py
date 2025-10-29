"""Logging module for the Inventory Management System."""
import logging
from typing import Optional
from datetime import datetime
import json

from .storage import Database, DatabaseError

class AdminLogger:
    """Handles logging of admin actions to the database."""
    def __init__(self, db: Database):
        self.db = db
        self.logger = logging.getLogger(__name__)

    def log_action(self, 
                  user: str, 
                  action: str, 
                  details: Optional[dict] = None) -> None:
        """
        Log an admin action to the database.
        
        Args:
            user: Username performing the action
            action: Description of the action
            details: Optional dictionary of additional details
        """
        try:
            details_json = json.dumps(details) if details else None
            
            query = """
            INSERT INTO admin_logs (user, action, details)
            VALUES (?, ?, ?)
            """
            self.db.execute(query, (user, action, details_json))
            self.db.commit()
            
            self.logger.info(f"Admin action logged - User: {user}, Action: {action}")
        except DatabaseError as e:
            self.logger.error(f"Failed to log admin action: {e}")
            # Don't raise - logging should not interrupt main flow

def setup_logging(log_file: str, log_format: str) -> None:
    """
    Set up application-wide logging configuration.
    
    Args:
        log_file: Path to the log file
        log_format: Format string for log messages
    """
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()  # Also log to console
        ]
    )