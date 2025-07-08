#!/usr/bin/env python3
"""
Setup script for Healthcare Startup Discovery System

This script helps users set up the environment and download necessary
dependencies for the healthcare startup discovery system.
"""

import os
import sys
import subprocess
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def check_python_version():
    """Check if Python version is sufficient"""
    if sys.version_info < (3, 7):
        logger.error("Python 3.7 or higher is required")
        sys.exit(1)
    logger.info(f"Python version: {sys.version}")


def install_dependencies():
    """Install required Python packages"""
    logger.info("Installing dependencies...")
    
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ])
        logger.info("Dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to install dependencies: {e}")
        sys.exit(1)


def download_nltk_data():
    """Download necessary NLTK data"""
    logger.info("Downloading NLTK data...")
    
    try:
        import nltk
        
        # Download required NLTK data
        nltk.download('punkt', quiet=True)
        nltk.download('stopwords', quiet=True)
        
        logger.info("NLTK data downloaded successfully")
    except Exception as e:
        logger.error(f"Failed to download NLTK data: {e}")
        sys.exit(1)


def create_directories():
    """Create necessary directories"""
    logger.info("Creating directories...")
    
    directories = [
        'output',
        'logs',
        'cache'
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        logger.info(f"Created directory: {directory}")


def setup_environment():
    """Set up environment variables"""
    logger.info("Setting up environment...")
    
    # Create .env file template if it doesn't exist
    env_file = Path('.env')
    if not env_file.exists():
        env_template = """# Healthcare Startup Discovery System Configuration
# 
# Optional API keys for enhanced functionality:
# CRUNCHBASE_API_KEY=your_crunchbase_api_key_here
# LINKEDIN_API_KEY=your_linkedin_api_key_here
# 
# System configuration:
# LOG_LEVEL=INFO
# MAX_CONCURRENT_REQUESTS=10
# DEFAULT_DELAY=1.0
"""
        with open(env_file, 'w') as f:
            f.write(env_template)
        logger.info("Created .env template file")


def test_imports():
    """Test if all required modules can be imported"""
    logger.info("Testing imports...")
    
    required_modules = [
        'aiohttp',
        'asyncio',
        'beautifulsoup4',
        'pandas',
        'numpy',
        'nltk',
        'scikit-learn',
        'requests',
        'validators',
        'tqdm',
        'langdetect'
    ]
    
    failed_imports = []
    
    for module in required_modules:
        try:
            if module == 'beautifulsoup4':
                import bs4
            else:
                __import__(module)
            logger.info(f"✓ {module}")
        except ImportError:
            failed_imports.append(module)
            logger.error(f"✗ {module}")
    
    if failed_imports:
        logger.error(f"Failed to import: {', '.join(failed_imports)}")
        logger.error("Please run: pip install -r requirements.txt")
        sys.exit(1)
    
    logger.info("All imports successful")


def run_quick_test():
    """Run a quick test to ensure the system works"""
    logger.info("Running quick test...")
    
    try:
        # Test NLP processor
        from nlp_processor import HealthcareNLPProcessor
        nlp = HealthcareNLPProcessor()
        
        test_text = "This is a healthcare startup developing medical devices."
        confidence, keywords, countries = nlp.calculate_overall_confidence(test_text)
        
        if confidence > 0:
            logger.info(f"✓ NLP processor working (confidence: {confidence:.3f})")
        else:
            logger.warning("NLP processor returned zero confidence")
        
        # Test URL validator
        from url_validator import URLValidator
        validator = URLValidator()
        
        test_url = "https://example.com"
        is_valid = validator.is_valid_url(test_url)
        
        if is_valid:
            logger.info("✓ URL validator working")
        else:
            logger.warning("URL validator test failed")
        
        logger.info("Quick test completed successfully")
        
    except Exception as e:
        logger.error(f"Quick test failed: {e}")
        logger.error("Please check the installation and try again")
        sys.exit(1)


def print_usage_instructions():
    """Print usage instructions"""
    print("\n" + "="*60)
    print("HEALTHCARE STARTUP DISCOVERY SYSTEM - SETUP COMPLETE")
    print("="*60)
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. (Optional) Edit .env file to add API keys")
    print("2. Run the discovery system:")
    print("   python main.py")
    print("\n📁 Output will be generated in the current directory")
    print("📊 Check the CSV and JSON files for results")
    print("📈 Review the summary report for statistics")
    print("\n🔧 Configuration:")
    print("- Edit config.py to customize settings")
    print("- Adjust main.py parameters for different discovery targets")
    print("\n📖 For more information, see README.md")
    print("\n" + "="*60)


def main():
    """Main setup function"""
    print("Healthcare Startup Discovery System - Setup")
    print("=" * 50)
    
    try:
        check_python_version()
        install_dependencies()
        download_nltk_data()
        create_directories()
        setup_environment()
        test_imports()
        run_quick_test()
        print_usage_instructions()
        
    except KeyboardInterrupt:
        print("\nSetup interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Setup failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()