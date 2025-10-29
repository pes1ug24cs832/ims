#!/bin/bash

# Packaging script for IMS deployment
# Creates a zip file containing all required files for deployment

# Exit on any error
set -e

# Get current date for versioning
VERSION=$(date +%Y%m%d_%H%M%S)
PACKAGE_NAME="deployment-package-$VERSION"

# Create package directory
mkdir -p "$PACKAGE_NAME"

# Copy source files
cp -r src/ "$PACKAGE_NAME/"

# Copy documentation
cp -r docs/ "$PACKAGE_NAME/"

# Copy sample data
cp -r sample_data/ "$PACKAGE_NAME/"

# Generate reports directory
mkdir -p "$PACKAGE_NAME/reports"

# Run tests and generate coverage report
echo "Running tests and generating coverage report..."
python -m pytest --cov=src --cov-report=html
cp -r htmlcov/* "$PACKAGE_NAME/reports/coverage/"

# Run pylint
echo "Running pylint..."
pylint src/ --output-format=parseable --reports=y > "$PACKAGE_NAME/reports/pylint-report.txt" || true

# Run bandit
echo "Running security scan..."
bandit -r src/ -f txt -o "$PACKAGE_NAME/reports/bandit-report.txt" || true

# Copy requirements and README
cp requirements.txt "$PACKAGE_NAME/"
cp README.md "$PACKAGE_NAME/"

# Create zip archive
zip -r "$PACKAGE_NAME.zip" "$PACKAGE_NAME/"

# Clean up
rm -rf "$PACKAGE_NAME"

echo "Package created: $PACKAGE_NAME.zip"