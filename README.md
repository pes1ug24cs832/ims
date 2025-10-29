# Inventory Management System (IMS)

A command-line inventory management system with secure authentication, automated backups, and comprehensive test coverage.

## Features

- Product management (add, list, update stock)
- Order processing (sales and purchases)
- Supplier management
- Low stock alerts
- Admin authentication
- Encrypted backups
- Action logging
- SQLite database with CSV data import

## Requirements

- Python 3.10+
- SQLite 3
- Required packages in `requirements.txt`
- Development tools in `requirements-dev.txt`

## Quick Start

1. Clone the repository:
   ```bash
   git clone <repo-url>
   cd ims
   ```

2. Create and activate virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   venv\Scripts\activate     # Windows
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the application:
   ```bash
   python -m src.cli
   ```

Default admin credentials:
- Username: admin
- Password: adminpass

## Development Setup

1. Install development dependencies:
   ```bash
   pip install -r requirements-dev.txt
   ```

2. Run tests:
   ```bash
   pytest -v
   ```

3. Generate coverage report:
   ```bash
   pytest --cov=src --cov-report=html
   ```

4. Run linter:
   ```bash
   pylint src/
   ```

5. Run security scan:
   ```bash
   bandit -r src/
   ```

## Repository Structure

```
ims/
├── src/                # Source code
│   ├── cli.py         # Command-line interface
│   ├── product_manager.py
│   ├── order_processor.py
│   ├── supplier_manager.py
│   ├── storage.py     # Database operations
│   ├── auth.py        # Authentication
│   ├── backup_security.py
│   └── logger.py
├── tests/             # Test suites
│   ├── unit/
│   ├── integration/
│   └── system/
├── docs/              # Documentation
├── sample_data/       # CSV seed data
└── scripts/           # Utility scripts
```

## CI/CD Pipeline

The project uses GitHub Actions for continuous integration and deployment. The pipeline includes:

1. Build: Install dependencies
2. Test: Run pytest suite
3. Coverage: Generate and check coverage report (≥75%)
4. Lint: Run pylint (score ≥7.5)
5. Security: Run bandit security scan
6. Package: Create deployment artifact

To run the pipeline steps locally:

```bash
# Build & install
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Test
pytest -v

# Coverage
pytest --cov=src --cov-report=html
# Report in htmlcov/index.html

# Lint
pylint src/
# Should score ≥7.5

# Security
bandit -r src/
# Should have no critical issues

# Package
./scripts/package_deploy.sh
# Creates deployment-package-<date>.zip
```

## Branch Strategy

- `main`: Production-ready code
- `develop`: Development branch
- Feature branches: `feature/<name>`
- Release branches: `release/v*`
- Hotfix branches: `hotfix/*`

## Contributing

1. Create a feature branch:
   ```bash
   git checkout -b feature/your-feature
   ```

2. Make changes and test:
   ```bash
   pytest -v
   pylint src/
   ```

3. Create a pull request using `PR_TEMPLATE.md`

4. Ensure all checks pass in CI pipeline

## Commit Message Format

Examples of good commit messages:

```
Add product validation (INV-F-001)
Fix stock update bug in order processing (INV-F-011)
Implement encrypted backups (PRJ-SEC-002)
Update API documentation for supplier endpoints
Improve test coverage for auth module
```

## Documentation

- `docs/API.md`: Module interfaces
- `docs/design.md`: Architecture and design
- `docs/RTM.md`: Requirements traceability
- `docs/demo_script.md`: Demo walkthrough

## Security Notes

- Admin credentials are for development only
- Change default admin password in production
- Backups are AES encrypted
- All admin actions are logged
- Passwords are bcrypt hashed

## License

[Add license information]