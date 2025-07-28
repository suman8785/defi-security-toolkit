#!/bin/bash

echo "🚀 DeFi Security Toolkit Quick Start"
echo "===================================="

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
required_version="3.9"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then 
    echo "❌ Python 3.9+ is required. Found: $python_version"
    exit 1
fi

echo "✅ Python version: $python_version"

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv env

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source env/bin/activate || . env/Scripts/activate

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "📦 Installing requirements..."
pip install -r requirements.txt

# Install additional tools
echo "🔧 Installing security tools..."
pip install slither-analyzer mythril

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p slither-reports mythril-reports logs

# Run tests
echo "🧪 Running tests..."
python test_all_features.py

# Check if tests passed
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Setup complete! The toolkit is ready to use."
    echo ""
    echo "To start the application:"
    echo "  streamlit run streamlit_app.py"
    echo ""
    echo "The application will open at http://localhost:8501"
else
    echo ""
    echo "⚠ Some tests failed. Please check the errors above."
    echo "You can still try running the application:"
    echo "  streamlit run streamlit_app.py"
fi