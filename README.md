# Healthcare URL Validator and Discoverer

A beginner-friendly Python script that validates and cleans healthcare-related URLs, and discovers new ones from various online sources.

## 🎯 What This Script Does

1. **Validates Your Existing URLs**: Checks if your healthcare URLs are live, reachable, and actually healthcare-related
2. **Cleans and Deduplicates**: Removes duplicates, social media links, and login pages
3. **Discovers New URLs**: Finds new healthcare companies from Google searches, Crunchbase, AngelList, and healthcare news sites
4. **Outputs Clean Data**: Saves results in both CSV and JSON formats for easy analysis

## 📋 Features

- ✅ **Fast Concurrent Processing**: Uses asyncio and aiohttp for speed
- ✅ **Healthcare Content Detection**: Automatically identifies healthcare-related content
- ✅ **Smart Filtering**: Removes social media, login pages, and irrelevant URLs
- ✅ **Multiple Data Sources**: Google, Crunchbase, AngelList, healthcare news sites
- ✅ **Comprehensive Reporting**: Detailed statistics and error reporting
- ✅ **Export Options**: CSV and JSON output formats

## 🚀 Quick Start

### Prerequisites

- Python 3.7 or higher
- Internet connection

### Installation

1. **Clone or download this project** to your computer

2. **Open a terminal/command prompt** and navigate to the project folder:
   ```bash
   cd path/to/healthcare-url-validator
   ```

3. **Create a virtual environment** (recommended):
   ```bash
   python3 -m venv healthcare_env
   source healthcare_env/bin/activate  # On Windows: healthcare_env\Scripts\activate
   ```

4. **Install the required packages**:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Script

1. **Activate the virtual environment** (if you created one):
   ```bash
   source healthcare_env/bin/activate  # On Windows: healthcare_env\Scripts\activate
   ```

2. **Test with a few sample URLs first** (recommended):
   ```bash
   python test_sample.py
   ```

3. **Run the full script** (validates all URLs + discovers new ones):
   ```bash
   python main.py
   ```

The full script will:
1. Validate the provided list of 50+ healthcare URLs
2. Discover new URLs from various sources
3. Save results to timestamped CSV and JSON files

## 📁 Project Structure

```
healthcare-url-validator/
├── main.py              # Main script - full validation + discovery
├── test_sample.py       # Quick test with sample URLs
├── url_validator.py     # URL validation and cleaning logic
├── url_discoverer.py    # URL discovery from various sources
├── utils.py             # Common utility functions
├── config.py            # Configuration and settings
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## 📊 Output Files

The script generates several output files with timestamps:

### All Results
- `healthcare_urls_all_YYYYMMDD_HHMMSS.csv` - All processed URLs
- `healthcare_urls_all_YYYYMMDD_HHMMSS.json` - All results with metadata

### Live Healthcare URLs Only
- `healthcare_urls_live_YYYYMMDD_HHMMSS.csv` - Only live healthcare URLs
- `healthcare_urls_live_YYYYMMDD_HHMMSS.json` - Live healthcare URLs with metadata

### CSV Columns
- `url` - The website URL
- `source` - Where the URL was found (e.g., "Validated list", "Google SERP")
- `is_live` - Whether the URL is accessible (True/False)
- `is_healthcare` - Whether the content is healthcare-related (True/False)
- `status_code` - HTTP status code (200, 404, etc.)
- `title` - Page title
- `description` - Page description
- `response_time` - How long it took to load (seconds)
- `error` - Any error that occurred

## ⚙️ Configuration

You can modify the search behavior by editing `config.py`:

### Healthcare Keywords
Add or remove keywords that indicate healthcare content:
```python
HEALTHCARE_KEYWORDS = [
    'health', 'medical', 'therapy', 'patient', 'doctor',
    # Add your own keywords here
]
```

### Search Queries
Modify the Google search queries:
```python
GOOGLE_SEARCH_QUERIES = [
    'digital health startups Germany',
    'healthcare AI companies Europe',
    # Add your own search terms here
]
```

### Request Settings
Adjust performance settings:
```python
REQUEST_TIMEOUT = 10  # Seconds to wait for each URL
MAX_CONCURRENT_REQUESTS = 20  # How many URLs to check at once
```

## 🔍 How It Works

### 1. URL Validation Process
- Cleans URLs (removes tracking parameters, fixes format)
- Removes duplicates
- Filters out social media and login pages
- Makes HTTP requests to check if URLs are live
- Analyzes page content to determine if it's healthcare-related

### 2. URL Discovery Process
- **Google Search**: Searches for healthcare companies using predefined queries
- **Crunchbase**: Searches publicly available company listings
- **AngelList**: Looks for healthcare startups
- **Healthcare News Sites**: Extracts URLs from industry websites

### 3. Content Analysis
The script determines if a URL is healthcare-related by:
- Analyzing page titles and descriptions
- Checking for healthcare keywords in the URL and content
- Using a scoring system (requires multiple healthcare indicators)

## 🛠️ Troubleshooting

### Common Issues

**"Module not found" errors**
```bash
pip install -r requirements.txt
```

**"Permission denied" errors**
- Make sure you have write permissions in the folder
- Try running with administrator/sudo privileges

**No URLs discovered from Google**
- Google may block automated searches occasionally
- The script includes delays to be respectful
- Consider using Google Custom Search API for production use

**Slow performance**
- Reduce `MAX_CONCURRENT_REQUESTS` in `config.py`
- Some websites may be slow to respond

### Performance Tips

1. **For faster validation** (fewer discovered URLs):
   - Comment out discovery sources in `url_discoverer.py`
   - Reduce Google search queries in `config.py`

2. **For more thorough discovery**:
   - Add more search queries to `config.py`
   - Increase `MAX_URLS_PER_SOURCE` in `config.py`

## 📈 Example Output

```
Healthcare URL Validator and Discoverer
==================================================
Starting at: 2024-01-15 14:30:25

Step 1: Validating 50 provided URLs...
Starting validation of 49 URLs...
After cleaning and deduplication: 49 URLs
Step 2: Validating URLs (checking if live and healthcare-related)...
  - Live URLs: 42
  - Healthcare-related URLs: 38

Step 2: Discovering new URLs from various sources...
Starting 12 discovery tasks...
Found 15 URLs from Google SERP
Found 8 URLs from Crunchbase public page
Found 12 URLs from Healthcare news sites
...

============================================================
FINAL STATISTICS
============================================================
Total URLs processed: 95
Live URLs: 78 (82.1%)
Healthcare-related URLs: 65 (68.4%)
```

## 🤝 Contributing

This script is designed to be beginner-friendly and extensible. Feel free to:
- Add new URL discovery sources
- Improve healthcare content detection
- Add new output formats
- Optimize performance

## 📄 License

This project is open source and available under the MIT License.

## 🆘 Need Help?

If you encounter any issues:
1. Check that all dependencies are installed correctly
2. Ensure you have internet connectivity
3. Try running with a smaller dataset first
4. Check the error messages in the output

---

**Happy URL hunting! 🔍💊**