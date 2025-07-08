#!/bin/bash

# Healthcare Startup Discovery System - Installation Script
# This script sets up the system in a virtual environment

set -e

echo "==================================================="
echo "Healthcare Startup Discovery System - Installation"
echo "==================================================="

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required but not found"
    exit 1
fi

echo "✓ Python 3 found: $(python3 --version)"

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "Installing dependencies..."
pip install -r requirements.txt

# Download NLTK data
echo "Downloading NLTK data..."
python -c "
import nltk
import ssl
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)
print('NLTK data downloaded successfully')
"

# Create directories
echo "Creating directories..."
mkdir -p output logs cache

# Create .env file
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cat > .env << 'EOF'
# Healthcare Startup Discovery System Configuration
# 
# Optional API keys for enhanced functionality:
# CRUNCHBASE_API_KEY=your_crunchbase_api_key_here
# LINKEDIN_API_KEY=your_linkedin_api_key_here
# 
# System configuration:
# LOG_LEVEL=INFO
# MAX_CONCURRENT_REQUESTS=10
# DEFAULT_DELAY=1.0
EOF
fi

# Test the installation
echo "Testing installation..."
python -c "
from nlp_processor import HealthcareNLPProcessor
from url_validator import URLValidator

# Test NLP processor
nlp = HealthcareNLPProcessor()
test_text = 'This is a healthcare startup developing medical devices.'
confidence, keywords, countries = nlp.calculate_overall_confidence(test_text)
print(f'✓ NLP processor working (confidence: {confidence:.3f})')

# Test URL validator
validator = URLValidator()
test_url = 'https://example.com'
is_valid = validator.is_valid_url(test_url)
print(f'✓ URL validator working: {is_valid}')

print('✓ All tests passed!')
"

echo ""
echo "=========================================="
echo "INSTALLATION COMPLETED SUCCESSFULLY!"
echo "=========================================="
echo ""
echo "To run the healthcare startup discovery:"
echo "1. Activate the virtual environment:"
echo "   source venv/bin/activate"
echo ""
echo "2. Run the discovery system:"
echo "   python main.py"
echo ""
echo "3. Check the generated output files for results"
echo ""
echo "For more information, see README.md"
echo ""

deactivate