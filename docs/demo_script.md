# IMS Demo Script

## Prerequisites
- Python 3.10+ installed
- Git installed
- Clean environment for demo
- Demo data prepared (sample products and suppliers)

## Demo Flow (15 minutes)

### 1. Project Setup (2 minutes)
```bash
# Clone repository
git clone <repo-url>
cd ims

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt
```

### 2. Core Features Demo (5 minutes)

#### Products Management
```bash
python -m src.cli

# Demo steps:
1. Select "Products" (1)
2. Add new product (1)
   - SKU: DEMO001
   - Name: Demo Laptop
   - Price: 999.99
   - Stock: 10
3. List all products (2)
4. View low stock products (4)
```

#### Orders Processing
```bash
# In the same CLI session:
1. Select "Orders" (2)
2. Create sales order (1)
   - SKU: DEMO001
   - Quantity: 3
3. List orders (3)
4. Return to products and verify stock updated
```

### 3. Security Features (3 minutes)

#### Admin Authentication
```bash
1. Select "Admin" (4)
2. Login with credentials:
   - Username: admin
   - Password: adminpass
3. Create backup (1)
4. View admin logs (4)
```

### 4. CI/CD Pipeline (3 minutes)

Show GitHub Actions workflow:
1. Open GitHub repository
2. Show Actions tab
3. Show recent workflow run with all stages:
   - Build
   - Test
   - Coverage
   - Lint
   - Security
   - Package

Review artifacts:
```bash
# Local testing
pytest --disable-warnings -v
pytest --cov=src --cov-report=html
pylint src/
bandit -r src/
```

### 5. Documentation & Reports (2 minutes)

Show generated reports:
1. Open `reports/coverage/index.html`
   - Highlight >75% coverage
2. Show documentation:
   - `docs/API.md`
   - `docs/design.md`
   - `docs/RTM.md`

## Key Points to Highlight

1. **Quality Gates**
   - All tests passing
   - Coverage >75%
   - Pylint score >7.5
   - No critical security issues

2. **Security Features**
   - Password hashing
   - Encrypted backups
   - Admin action logging

3. **Code Organization**
   - Clean architecture
   - Modular design
   - Comprehensive tests

4. **CI/CD Integration**
   - Automated pipeline
   - Quality checks
   - Artifact generation

## Common Demo Issues & Solutions

1. **Database Connection**
   - Check file permissions
   - Verify SQLite installation

2. **Authentication Fails**
   - Confirm using correct credentials
   - Check database initialization

3. **CI Pipeline Errors**
   - Check Python version
   - Verify dependencies installed
   - Review error logs

4. **Report Generation**
   - Ensure write permissions
   - Check disk space

## Demo Resources

Reports location:
- Coverage: `reports/coverage/index.html`
- Pylint: `reports/pylint-report.txt`
- Bandit: `reports/bandit-report.txt`

Sample data:
- Products: `sample_data/seed_products.csv`
- Suppliers: `sample_data/seed_suppliers.csv`

## Post-Demo Cleanup
```bash
# Deactivate virtual environment
deactivate

# Remove demo files
rm -rf instance/*.db
rm -rf reports/*
```