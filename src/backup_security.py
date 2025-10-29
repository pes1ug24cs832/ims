"""Backup and security module for the Inventory Management System."""
import os
from pathlib import Path
from datetime import datetime, timedelta
import logging
import shutil
import json
from typing import Dict, Any, Optional
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

from .config import (
    DB_PATH, 
    BACKUP_DIR, 
    BACKUP_RETENTION_DAYS,
    ENCRYPTION_KEY_LENGTH,
    SALT_LENGTH
)
from .storage import Database

logger = logging.getLogger(__name__)

class BackupError(Exception):
    """Raised when backup operations fail."""
    pass

class BackupManager:
    """Manages database backup and restore operations."""
    def __init__(self, 
                 db: Database,
                 backup_dir: str = BACKUP_DIR,
                 retention_days: int = BACKUP_RETENTION_DAYS):
        self.db = db
        self.backup_dir = Path(backup_dir)
        self.retention_days = retention_days
        self._ensure_backup_dir()

    def _ensure_backup_dir(self) -> None:
        """Create backup directory if it doesn't exist."""
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        # Set appropriate permissions
        os.chmod(self.backup_dir, 0o700)  # Owner read/write/execute only

    def _get_backup_filename(self) -> str:
        """Generate backup filename with timestamp."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        return f"backup_{timestamp}.db"

    def create_backup(self, passphrase: str) -> Path:
        """
        Create an encrypted backup of the database.
        
        Args:
            passphrase: Password to encrypt the backup
            
        Returns:
            Path: Path to created backup file
            
        Raises:
            BackupError: If backup creation fails
        """
        try:
            # Generate backup path
            backup_path = self.backup_dir / self._get_backup_filename()
            
            # Get database path from the Database instance
            db_path = Path(self.db.db_path)
            logger.info(f"Database path: {db_path}")
            logger.info(f"Database exists: {db_path.exists()}")
            if not db_path.exists():
                raise BackupError(f"Database file not found at {db_path}")
                
            # Copy database file
            shutil.copy2(db_path, backup_path)
            
            # Encrypt the backup
            encryptor = DatabaseEncryptor()
            encryptor.encrypt_file(backup_path, passphrase)
            
            logger.info(f"Created encrypted backup: {backup_path}")
            
            # Clean old backups
            self._cleanup_old_backups()
            
            return backup_path
            
        except Exception as e:
            logger.error(f"Backup creation failed: {e}")
            if backup_path.exists():
                backup_path.unlink()
            raise BackupError(f"Failed to create backup: {e}")

    def restore_from_backup(self, backup_path: Path, passphrase: str) -> None:
        """
        Restore database from an encrypted backup.
        
        Args:
            backup_path: Path to backup file
            passphrase: Password to decrypt the backup
            
        Raises:
            BackupError: If restore fails
        """
        if not backup_path.exists():
            raise BackupError(f"Backup file not found: {backup_path}")

        try:
            # Create temporary decrypted copy
            temp_path = backup_path.with_suffix('.temp')
            
            # Decrypt backup
            encryptor = DatabaseEncryptor()
            encryptor.decrypt_file(backup_path, temp_path, passphrase)
            
            # Replace current database
            shutil.copy2(temp_path, DB_PATH)
            
            logger.info(f"Successfully restored from backup: {backup_path}")
            
        except Exception as e:
            logger.error(f"Restore failed: {e}")
            raise BackupError(f"Failed to restore from backup: {e}")
        finally:
            if temp_path.exists():
                temp_path.unlink()

    def list_backups(self) -> list[Dict[str, Any]]:
        """
        List available backups with metadata.
        
        Returns:
            list[dict]: List of backup information
        """
        backups = []
        for path in self.backup_dir.glob("backup_*.db"):
            try:
                stats = path.stat()
                backups.append({
                    "filename": path.name,
                    "size": stats.st_size,
                    "created": datetime.fromtimestamp(stats.st_ctime).isoformat(),
                    "path": str(path)
                })
            except OSError:
                continue
        
        return sorted(backups, key=lambda x: x["created"], reverse=True)

    def _cleanup_old_backups(self) -> None:
        """Remove backups older than retention period."""
        cutoff = datetime.now() - timedelta(days=self.retention_days)
        
        for backup in self.list_backups():
            try:
                created = datetime.fromisoformat(backup["created"])
                if created < cutoff:
                    Path(backup["path"]).unlink()
                    logger.info(f"Removed old backup: {backup['filename']}")
            except (OSError, ValueError) as e:
                logger.error(f"Failed to remove old backup {backup['filename']}: {e}")

class DatabaseEncryptor:
    """Handles database file encryption/decryption."""
    def __init__(self):
        self.iterations = 100_000  # PBKDF2 iterations

    def _derive_key(self, passphrase: str, salt: Optional[bytes] = None) -> tuple[bytes, bytes]:
        """
        Derive encryption key from passphrase using PBKDF2.
        
        Args:
            passphrase: Password to derive key from
            salt: Optional salt (generated if not provided)
            
        Returns:
            tuple: (key, salt)
        """
        if salt is None:
            salt = os.urandom(SALT_LENGTH)
            
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=ENCRYPTION_KEY_LENGTH,
            salt=salt,
            iterations=self.iterations,
        )
        
        key = base64.urlsafe_b64encode(kdf.derive(passphrase.encode()))
        return key, salt

    def encrypt_file(self, file_path: Path, passphrase: str) -> None:
        """
        Encrypt a file in-place using Fernet (AES).
        
        Args:
            file_path: Path to file to encrypt
            passphrase: Encryption password
        """
        try:
            # Read file
            with open(file_path, 'rb') as f:
                data = f.read()
            
            # Generate key and salt
            key, salt = self._derive_key(passphrase)
            
            # Encrypt
            fernet = Fernet(key)
            encrypted_data = fernet.encrypt(data)
            
            # Write encrypted data with salt prefix
            with open(file_path, 'wb') as f:
                f.write(salt)  # Write salt as prefix
                f.write(encrypted_data)
                
        except Exception as e:
            raise BackupError(f"Encryption failed: {e}")

    def decrypt_file(self, 
                    encrypted_path: Path, 
                    output_path: Path, 
                    passphrase: str) -> None:
        """
        Decrypt a file encrypted by encrypt_file.
        
        Args:
            encrypted_path: Path to encrypted file
            output_path: Path to write decrypted file
            passphrase: Decryption password
        """
        try:
            # Read encrypted file
            with open(encrypted_path, 'rb') as f:
                salt = f.read(SALT_LENGTH)
                encrypted_data = f.read()
            
            # Derive key with salt from file
            key, _ = self._derive_key(passphrase, salt)
            
            # Decrypt
            fernet = Fernet(key)
            decrypted_data = fernet.decrypt(encrypted_data)
            
            # Write decrypted file
            with open(output_path, 'wb') as f:
                f.write(decrypted_data)
                
        except Exception as e:
            raise BackupError(f"Decryption failed: {e}")