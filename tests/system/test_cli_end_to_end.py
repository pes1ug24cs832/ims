"""System tests for CLI functionality."""
import pytest
import subprocess
import os
import tempfile
import time
from pathlib import Path
import sqlite3

# Helper functions for system tests
def run_cli_command(command: str, input_data: str = "") -> tuple[int, str, str]:
    """
    Run a CLI command and return exit code, stdout, and stderr.
    
    Args:
        command: Command to run
        input_data: Input to send to process
        
    Returns:
        tuple: (return_code, stdout, stderr)
    """
    process = subprocess.Popen(
        command,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    stdout, stderr = process.communicate(input_data)
    return process.returncode, stdout, stderr

class TestCLISystem:
    """System tests for CLI functionality."""
    
    @pytest.fixture
    def temp_db_path(self):
        """Create a temporary database file."""
        fd, path = tempfile.mkstemp(suffix='.db')
        os.close(fd)
        yield path
        if os.path.exists(path):
            os.unlink(path)

    @pytest.fixture
    def env_vars(self, temp_db_path):
        """Set up environment variables for testing."""
        # Generate a test password hash
        from src.auth import hash_password
        test_password_hash = hash_password("adminpass")
        
        old_vars = {}
        new_vars = {
            'IMS_DB_PATH': temp_db_path,
            'IMS_BACKUP_DIR': tempfile.mkdtemp(),
            'IMS_ADMIN_PASSWORD_HASH': test_password_hash  # Set password hash in environment
        }
        
        # Save old vars and set new ones
        for key, value in new_vars.items():
            old_vars[key] = os.environ.get(key)
            os.environ[key] = value
            
        yield new_vars
        
        # Restore old vars
        for key, value in old_vars.items():
            if value is None:
                del os.environ[key]
            else:
                os.environ[key] = value

    def test_INV_NF_001_command_execution_time(self, env_vars):
        """Test that typical commands execute within time limit (INV-NF-001)."""
        # Add a product
        start_time = time.time()
        input_data = "1\n1\nTEST001\nTest Product\nTest Description\n10.99\n5\n5\n"
        returncode, stdout, stderr = run_cli_command(
            ["python", "-m", "src.cli"],
            input_data
        )
        execution_time = time.time() - start_time
        
        assert returncode == 0
        assert execution_time <= 2.0  # Should complete within 2 seconds
        assert "Product added successfully" in stdout

    def test_INV_NF_002_data_persistence(self, env_vars):
        """Test that data persists across restarts (INV-NF-002)."""
        # Add a product
        input_data = "1\n1\nTEST001\nTest Product\nTest Description\n10.99\n5\n5\n"
        run_cli_command(["python", "-m", "src.cli"], input_data)
        
        # Start new process and verify product exists
        input_data = "1\n2\n5\n"  # View products and exit
        returncode, stdout, stderr = run_cli_command(
            ["python", "-m", "src.cli"],
            input_data
        )
        
        assert returncode == 0
        assert "TEST001" in stdout
        assert "Test Product" in stdout

    def test_INV_NF_003_admin_authentication(self, env_vars):
        """Test admin-only functionality requires login (INV-NF-003)."""
        # Try admin function with incorrect password
        input_data = "4\nadmin\nwrongpass\n5\n"
        returncode, stdout, stderr = run_cli_command(
            ["python", "-m", "src.cli"],
            input_data
        )
        
        assert returncode == 0
        assert "Authentication failed" in stdout
        
        # Try with correct password
        input_data = "4\nadmin\nadminpass\n5\n"
        returncode, stdout, stderr = run_cli_command(
            ["python", "-m", "src.cli"],
            input_data
        )
        
        assert returncode == 0
        assert "Authentication failed" not in stdout

    def test_INV_NF_004_backup_creation(self, env_vars):
        """Test backup creation and restore (INV-NF-004)."""
        # Add test data
        input_data = "1\n1\nTEST001\nTest Product\n\n10.99\n5\n5\n"
        run_cli_command(["python", "-m", "src.cli"], input_data)
        
        # Create backup
        input_data = "4\nadmin\nadminpass\n1\nbackup123\nbackup123\n5\n5\n"
        returncode, stdout, stderr = run_cli_command(
            ["python", "-m", "src.cli"],
            input_data
        )
        
        assert returncode == 0
        assert "Backup created successfully" in stdout
        
        # Verify backup file exists
        backup_files = list(Path(env_vars['IMS_BACKUP_DIR']).glob('backup_*.db'))
        assert len(backup_files) == 1

    def test_PRJ_SEC_001_password_hashing(self, env_vars):
        """Test that passwords are properly hashed (PRJ-SEC-001)."""
        # Connect directly to database
        conn = sqlite3.connect(env_vars['IMS_DB_PATH'])
        cursor = conn.cursor()
        
        # Try to authenticate with admin account
        input_data = "4\nadmin\nadminpass\n5\n"
        returncode, stdout, stderr = run_cli_command(
            ["python", "-m", "src.cli"],
            input_data
        )
        
        assert returncode == 0
        assert "Authentication failed" not in stdout
        
        # Verify password is not stored in plaintext
        cursor.execute("SELECT * FROM admin_logs WHERE user = 'admin'")
        log_entry = cursor.fetchone()
        assert log_entry is not None
        # Ensure log entry exists but doesn't contain password
        assert 'adminpass' not in str(log_entry)

    def test_end_to_end_order_flow(self, env_vars):
        """Test complete order processing flow."""
        # Add product
        input_data = "1\n1\nTEST001\nTest Product\n\n10.99\n10\n"
        run_cli_command(["python", "-m", "src.cli"], input_data)
        
        # Create sales order
        input_data = "2\n1\nTEST001\n3\n"
        returncode, stdout, stderr = run_cli_command(
            ["python", "-m", "src.cli"],
            input_data
        )
        
        assert returncode == 0
        assert "Sales order created successfully" in stdout
        
        # Check updated stock
        input_data = "1\n2\n5\n"
        returncode, stdout, stderr = run_cli_command(
            ["python", "-m", "src.cli"],
            input_data
        )
        
        assert returncode == 0
        assert "TEST001" in stdout
        assert "7" in stdout  # Initial 10 - 3 sold

    def test_low_stock_alerts(self, env_vars):
        """Test low stock alerting functionality."""
        # Add product with low stock
        input_data = "1\n1\nLOW001\nLow Stock Product\n\n10.99\n5\n"
        run_cli_command(["python", "-m", "src.cli"], input_data)
        
        # Check low stock alerts
        input_data = "1\n4\n5\n"
        returncode, stdout, stderr = run_cli_command(
            ["python", "-m", "src.cli"],
            input_data
        )
        
        assert returncode == 0
        assert "LOW001" in stdout
        assert "Low Stock Product" in stdout

    def test_input_validation(self, env_vars):
        """Test input validation and error handling."""
        # Try to add product with invalid price
        input_data = "1\n1\nTEST001\nTest Product\n\n-10.99\n5\n"
        returncode, stdout, stderr = run_cli_command(
            ["python", "-m", "src.cli"],
            input_data
        )
        
        assert returncode == 0
        assert "Error" in stdout or "Invalid" in stdout

        # Create a valid product first
        input_data = "1\n1\nTEST001\nTest Product\n\n10.99\n5\n5\n"  # Added newline for description and menu exit
        returncode, stdout, stderr = run_cli_command(
            ["python", "-m", "src.cli"],
            input_data
        )
        
        # Verify product was created
        input_data = "1\n2\n5\n"  # List products and exit
        returncode, stdout, stderr = run_cli_command(
            ["python", "-m", "src.cli"],
            input_data
        )
        assert "TEST001" in stdout, "Product creation failed"

        # Try to create sale with insufficient stock
        input_data = "2\n1\nTEST001\n999\n"
        returncode, stdout, stderr = run_cli_command(
            ["python", "-m", "src.cli"],
            input_data
        )
        
        assert returncode == 0
        assert "Error" in stdout
        assert "Insufficient stock" in stdout