"""Authentication and authorization module for the Inventory Management System."""
import bcrypt
from typing import Optional
import logging
from .config import ADMIN_USERNAME, ADMIN_PASSWORD_HASH, HASH_ROUNDS

logger = logging.getLogger(__name__)

class AuthenticationError(Exception):
    """Raised when authentication fails."""
    pass

def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    salt = bcrypt.gensalt(rounds=HASH_ROUNDS)
    return bcrypt.hashpw(password.encode(), salt).decode()

def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against its hash."""
    try:
        return bcrypt.checkpw(password.encode(), hashed.encode())
    except ValueError:
        return False

class Session:
    """Represents a user session."""
    def __init__(self, username: str, is_admin: bool):
        self.username = username
        self.is_admin = is_admin

class AuthManager:
    """Manages authentication and authorization."""
    def __init__(self):
        self._current_session: Optional[Session] = None

    def authenticate(self, username: str, password: str) -> Session:
        """Authenticate a user and create a session."""
        if username != ADMIN_USERNAME:
            logger.warning(f"Authentication failed for user: {username}")
            raise AuthenticationError("Invalid credentials")

        # Debug logging for password verification
        logger.debug(f"Attempting to verify password. Hash in config: {ADMIN_PASSWORD_HASH}")
        is_valid = verify_password(password, ADMIN_PASSWORD_HASH)
        logger.debug(f"Password verification result: {is_valid}")
        
        if not is_valid:
            logger.warning(f"Authentication failed for user: {username} - password mismatch")
            raise AuthenticationError("Invalid credentials")

        logger.info(f"User authenticated successfully: {username}")
        self._current_session = Session(username, is_admin=True)
        return self._current_session

    def get_current_session(self) -> Optional[Session]:
        """Get the current session if it exists."""
        return self._current_session

    def require_admin(self) -> None:
        """Check if current session has admin privileges."""
        if not self._current_session or not self._current_session.is_admin:
            raise AuthenticationError("Admin privileges required")

    def logout(self) -> None:
        """End the current session."""
        if self._current_session:
            logger.info(f"User logged out: {self._current_session.username}")
            self._current_session = None