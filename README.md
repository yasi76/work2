# Digital Health Startup Discovery System

A comprehensive Python-based system for discovering, evaluating, and analyzing digital health startups in Germany and Europe. This tool automates the process of finding real startup websites, validating their health relevance, and extracting key information.

## 🚀 Features

- **Multi-source Discovery**: Combines multiple discovery methods to find digital health startups
- **Automated Validation**: Checks if discovered URLs are live and health-related
- **Company Name Extraction**: Intelligently extracts company names from websites
- **Comprehensive Analytics**: Generates detailed reports and summaries
- **Language Support**: Works with both English and German websites
- **Concurrent Processing**: Uses multi-threading for efficient processing
- **Free Tools Only**: Uses only free and public resources

### 🆕 Enhanced Name Extraction Features

- **NLP-based Extraction**: Uses spaCy for intelligent organization name detection
- **Domain Mapping**: Configurable mappings for tricky domains
- **Advanced Metadata Parsing**: Supports nested JSON-LD and @graph structures
- **JavaScript Support**: Optional headless browser for JS-heavy sites
- **Extraction Metrics**: Detailed statistics on extraction methods and success rates
- **Input Validation**: Robust handling of various input formats

## 📋 Components

### 1. **ultimate_startup_discovery.py**
Main orchestrator that combines all discovery methods:
- Integrates multiple discovery sources
- Manages hardcoded verified URLs
- Deduplicates and consolidates results
- Outputs comprehensive JSON and CSV files

### 2. **enhanced_startup_discovery.py**
Real-time discovery engine that finds startups from:
- Startup directories and databases
- Tech news and blog sites
- Investment and accelerator platforms
- Public APIs and web scraping

### 3. **google_search_scraper.py**
Specialized Google search scraper:
- Finds health startups through targeted search queries
- Implements respectful rate limiting
- Extracts URLs from search results

### 4. **evaluate_health_startups.py**
Validates discovered URLs:
- Checks if websites are live (HTTP status)
- Determines health relevance using keyword analysis
- Extracts metadata (title, description, keywords)
- Identifies language and location
- Rates health relevance score

### 5. **extract_company_names.py**
Intelligent company name extraction:
- Parses website content to find company names
- Uses multiple extraction strategies
- Handles various naming conventions
- Updates existing data with company names
- **NEW**: NLP-based organization detection with spaCy
- **NEW**: Configurable domain-to-name mappings
- **NEW**: JavaScript rendering support with Playwright
- **NEW**: Detailed extraction statistics and metrics

### 6. **generate_startup_summary.py**
Analytics and reporting tool:
- Generates comprehensive statistics
- Creates visualizations (optional)
- Produces text reports
- Exports to various formats

### 7. **process_startup_data.py**
Data processing utilities:
- Handles data transformation
- Manages file I/O operations
- Provides helper functions

## 🛠️ Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd digital-health-startup-discovery
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

3. (Optional) Install visualization dependencies:
```bash
pip install matplotlib seaborn pandas openpyxl
```

4. (Optional) Install enhanced name extraction dependencies:
```bash
# For NLP-based extraction
pip install spacy
python -m spacy download en_core_web_sm

# For JavaScript rendering
pip install playwright
playwright install
```

## 📖 Usage

### Basic Discovery Pipeline

1. **Run the main discovery system:**
```bash
python ultimate_startup_discovery.py
```
This will:
- Search for digital health startups
- Validate discovered URLs
- Extract company names
- Generate output files

### Individual Components

**Evaluate existing URLs:**
```bash
python evaluate_health_startups.py input_urls.json
```

**Extract company names:**
```bash
# Basic extraction from existing data
python extract_company_names.py validated_urls.json

# Refetch URLs for better accuracy
python extract_company_names.py validated_urls.json --refetch

# Use JavaScript rendering for dynamic sites
python extract_company_names.py validated_urls.json --refetch --js

# Update domain mappings
python extract_company_names.py validated_urls.json --update-domain-map new_mappings.json
```

**Generate summary reports:**
```bash
python generate_startup_summary.py validated_urls.json
```

### Output Files

The system generates several output files:

- `discovered_startups_[timestamp].json` - Complete data in JSON format
- `discovered_startups_[timestamp].csv` - Simplified CSV export
- `startup_summary_report_[timestamp].txt` - Text summary report
- `startup_evaluation.log` - Detailed processing logs
- **NEW**: `[prefix]_extraction_stats.json` - Name extraction statistics
- **NEW**: `domain_name_map.json` - Domain to company name mappings

## 📊 Data Structure

Each startup entry contains:
```json
{
    "url": "https://example.health",
    "company_name": "Example Health GmbH",
    "status": "active",
    "health_related": true,
    "health_score": 0.85,
    "title": "Example Health - Digital Healthcare Solutions",
    "description": "Innovative digital health platform...",
    "keywords": ["digital health", "telemedicine", "healthcare"],
    "language": "en",
    "location": "Germany",
    "discovery_method": "enhanced_search",
    "validation_timestamp": "2024-01-15T10:30:00"
}
```

## ⚙️ Configuration

### Rate Limiting
- Default delay: 2 seconds between requests
- Configurable in each module

### Concurrent Processing
- Default: 10 concurrent workers
- Adjustable via ThreadPoolExecutor settings

### Health Keywords
Customizable health-related keywords in multiple languages:
- English: health, medical, care, therapy, etc.
- German: gesundheit, medizin, pflege, therapie, etc.

### Domain Name Mappings
Edit `domain_name_map.json` to add custom domain-to-name mappings:
```json
{
  "getnutrio.com": "Nutrio",
  "telemed24online.de": "TeleMed24 Online"
}
```

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📝 License

This project is licensed under the MIT License.

## ⚠️ Disclaimer

This tool is designed for legitimate research and discovery purposes. Please:
- Respect website terms of service
- Use appropriate rate limiting
- Follow robots.txt guidelines
- Obtain necessary permissions for data collection

## 🐛 Troubleshooting

**Common Issues:**

1. **Import Errors**: Ensure all Python files are in the same directory
2. **Request Timeouts**: Check internet connection and increase timeout values
3. **Rate Limiting**: Reduce concurrent workers or increase delays
4. **SSL Errors**: Some websites may have certificate issues - these are logged but skipped

**Logging:**
- Check `startup_evaluation.log` for detailed error messages
- Enable debug logging by modifying the logging level in scripts

## 📧 Support

For issues, questions, or contributions, please open an issue on the repository.