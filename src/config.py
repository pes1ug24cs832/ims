"""Configuration settings for the Inventory Management System."""
import os
from pathlib import Path

# Database configuration
DB_PATH = os.getenv('IMS_DB_PATH', 'inventory.db')
BACKUP_DIR = os.getenv('IMS_BACKUP_DIR', Path.home() / '.ims/backups')
BACKUP_RETENTION_DAYS = 7

# Product settings
MIN_STOCK_THRESHOLD = 10
CRITICAL_STOCK_THRESHOLD = 5

# Security settings
HASH_ROUNDS = 12  # For bcrypt
ADMIN_USERNAME = 'admin'  # For development only
ADMIN_PASSWORD_HASH = os.getenv(
    'IMS_ADMIN_PASSWORD_HASH',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LehpYyF/nH.cqyqgS'  # Default hash for 'adminpass'
)

# Encryption settings
ENCRYPTION_KEY_LENGTH = 32  # AES-256
SALT_LENGTH = 16

# Logging configuration
LOG_FILE = 'admin_actions.log'
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# Sample data paths
SAMPLE_DATA_DIR = Path(__file__).parent.parent / 'sample_data'
SAMPLE_PRODUCTS_CSV = SAMPLE_DATA_DIR / 'seed_products.csv'
SAMPLE_SUPPLIERS_CSV = SAMPLE_DATA_DIR / 'seed_suppliers.csv'