# Digital Health Startup Discovery System

A streamlined Python-based system for discovering, evaluating, and analyzing digital health startups in Germany and Europe. This tool automates the process of finding real startup websites, validating their health relevance, and extracting key information.

## 🚀 Features

- **Unified Discovery**: Single script that combines multiple discovery methods
- **Automated Validation**: Checks if discovered URLs are live and health-related
- **Intelligent Name Extraction**: Advanced company name extraction with NLP support
- **Comprehensive Analytics**: Generates detailed reports and summaries
- **Accuracy Evaluation**: Compare extracted names against ground truth data
- **Language Support**: Works with both English and German websites
- **Concurrent Processing**: Multi-threaded for efficient processing

### 🆕 Enhanced Name Extraction Features

- **NLP-based Extraction**: Uses spaCy for intelligent organization name detection
- **Domain Mapping**: Configurable mappings for tricky domains
- **Advanced Metadata Parsing**: Supports nested JSON-LD and @graph structures
- **JavaScript Support**: Optional headless browser for JS-heavy sites
- **Extraction Metrics**: Detailed statistics on extraction methods and success rates

## 📋 Core Components

### 1. **ultimate_startup_discovery.py**
Main discovery engine that:
- Searches multiple sources for digital health startups
- Combines hardcoded verified URLs with dynamic discovery
- Deduplicates and consolidates results
- Outputs comprehensive JSON and CSV files

### 2. **evaluate_health_startups.py**
Validates discovered URLs by:
- Checking if websites are live (HTTP status)
- Determining health relevance using keyword analysis
- Extracting metadata (title, description, keywords)
- Identifying language and location
- Rating health relevance score

### 3. **extract_company_names.py**
Advanced name extraction with:
- Multiple extraction strategies (9+ methods)
- NLP-based organization detection (optional)
- Configurable domain-to-name mappings
- JavaScript rendering support (optional)
- Detailed extraction statistics

### 4. **generate_startup_summary.py**
Analytics and reporting:
- Generates comprehensive statistics
- Creates visualizations (optional)
- Produces detailed text reports
- Exports to multiple formats

### 5. **evaluate_name_extraction.py**
Accuracy evaluation tool:
- Compares extracted names against ground truth
- Calculates accuracy metrics and similarity scores
- Generates evaluation reports in multiple formats
- Color-coded console output for easy review

## 🛠️ Installation

### Basic Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd digital-health-startup-discovery
```

2. Install required Python packages:
```bash
pip install requests beautifulsoup4 lxml
```

### Optional Dependencies

For enhanced features:
```bash
# For NLP-based name extraction
pip install spacy
python -m spacy download en_core_web_sm

# For JavaScript rendering
pip install playwright
playwright install

# For visualization and Excel export
pip install matplotlib seaborn pandas openpyxl
```

## 📖 Usage

### Complete Discovery Pipeline

```bash
# 1. Discover startups
python ultimate_startup_discovery.py

# 2. Evaluate the discovered URLs (if not already done)
python evaluate_health_startups.py discovered_startups_*.json

# 3. Extract company names
python extract_company_names.py *_validated.json --refetch

# 4. Generate summary report
python generate_startup_summary.py *_with_names.json

# 5. Evaluate extraction accuracy (optional)
python evaluate_name_extraction.py *_with_names.json
```

### Individual Operations

**Evaluate URLs:**
```bash
python evaluate_health_startups.py input_urls.json
```

**Extract company names:**
```bash
# Basic extraction from existing data
python extract_company_names.py validated_urls.json

# Refetch URLs for better accuracy
python extract_company_names.py validated_urls.json --refetch

# Use JavaScript rendering
python extract_company_names.py validated_urls.json --refetch --js
```

**Generate summary:**
```bash
python generate_startup_summary.py validated_urls.json
```

**Evaluate accuracy:**
```bash
python evaluate_name_extraction.py startups_with_names.json
```

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
    "discovery_method": "hardcoded",
    "name_extraction_method": "og:site_name",
    "validation_timestamp": "2024-01-15T10:30:00"
}
```

## 📁 Configuration Files

### domain_name_map.json
Maps tricky domains to correct company names:
```json
{
  "getnutrio.com": "Nutrio",
  "telemed24online.de": "TeleMed24 Online"
}
```

Update with:
```bash
python extract_company_names.py data.json --update-domain-map new_mappings.json
```

## 📈 Evaluation Metrics

The evaluation tool provides:
- **Exact Match Accuracy**: Case-insensitive comparison
- **Similarity Scores**: Character-level similarity (0-1)
- **Method Performance**: Accuracy breakdown by extraction method
- **Coverage Analysis**: Percentage of ground truth URLs found

## 🔧 Tips & Best Practices

1. **Discovery**: Run `ultimate_startup_discovery.py` first to get a comprehensive list
2. **Validation**: Always validate URLs before extracting names
3. **Name Extraction**: Use `--refetch` for best accuracy
4. **Evaluation**: Maintain a ground truth file for tracking improvements

## ⚠️ Important Notes

- Respects rate limiting (2-second delays by default)
- Handles SSL errors gracefully
- Logs all operations for debugging
- Saves incremental progress

## 🐛 Troubleshooting

**Common Issues:**

1. **Import Errors**: Install missing dependencies
2. **Request Timeouts**: Check internet connection
3. **Rate Limiting**: Increase delays between requests
4. **Memory Issues**: Process files in smaller batches

## 📝 License

This project is licensed under the MIT License.

## 🤝 Contributing

Contributions welcome! Please submit pull requests with:
- Clear descriptions
- Test cases
- Documentation updates