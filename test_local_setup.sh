#!/bin/bash

# Test script for local clone and setup workflow
# This script simulates the process a user would follow to set up the job hunt ecosystem

echo "===== Testing Local Clone and Setup Workflow ====="

# Create a temporary directory for testing
TEST_DIR="/tmp/job_hunt_ecosystem_test"
echo "Creating test directory: $TEST_DIR"
mkdir -p $TEST_DIR

# Simulate git clone by copying the project
echo "Simulating git clone..."
cp -r /home/ubuntu/job_hunt_ecosystem/* $TEST_DIR/

# Navigate to the test directory
cd $TEST_DIR

# Check if README.md exists
echo "Checking for README.md..."
if [ -f "README.md" ]; then
    echo "✅ README.md found"
else
    echo "❌ README.md not found"
    exit 1
fi

# Check if requirements.txt exists
echo "Checking for requirements.txt..."
if [ -f "job_hunt_app/requirements.txt" ]; then
    echo "✅ requirements.txt found"
else
    echo "❌ requirements.txt not found"
    exit 1
fi

# Check if package.json exists
echo "Checking for package.json..."
if [ -f "job_hunt_ui/package.json" ]; then
    echo "✅ package.json found"
else
    echo "❌ package.json not found"
    exit 1
fi

# Test backend setup
echo "Testing backend setup..."
echo "Creating virtual environment..."
python3 -m venv test_venv
source test_venv/bin/activate

echo "Installing Python dependencies..."
pip install -r job_hunt_app/requirements.txt

echo "Testing database initialization..."
if [ -f "job_hunt_app/src/data_structure_design.py" ]; then
    echo "✅ Database initialization script found"
else
    echo "❌ Database initialization script not found"
    exit 1
fi

# Check if main.py exists
echo "Checking for main.py..."
if [ -f "job_hunt_app/src/main.py" ]; then
    echo "✅ main.py found"
else
    echo "❌ main.py not found"
    exit 1
fi

# Deactivate virtual environment
deactivate

# Test frontend setup
echo "Testing frontend setup..."
if [ -d "job_hunt_ui/src" ]; then
    echo "✅ Frontend source directory found"
else
    echo "❌ Frontend source directory not found"
    exit 1
fi

# Check for essential frontend files
echo "Checking for essential frontend files..."
ESSENTIAL_FILES=("job_hunt_ui/src/App.tsx" "job_hunt_ui/src/lib/api.ts" "job_hunt_ui/src/hooks/useAuth.tsx")
for file in "${ESSENTIAL_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file found"
    else
        echo "❌ $file not found"
    fi
done

echo "===== Local Clone and Setup Workflow Test Complete ====="

# Clean up
echo "Cleaning up test directory..."
rm -rf $TEST_DIR
rm -rf test_venv

echo "Test completed successfully!"
