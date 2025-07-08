# Healthcare Startup Discovery System

A comprehensive Python-based solution for discovering URLs of healthcare startups and SMEs across Germany and Europe. The system uses asynchronous scraping, NLP filtering, and multiple data sources to build a high-quality database of healthcare companies.

## 🎯 Features

- **Asynchronous Scraping**: Uses `asyncio` and `aiohttp` for high-performance, scalable scraping
- **NLP Filtering**: Advanced healthcare keyword detection and relevance scoring
- **Multiple Data Sources**: 
  - Startup directories (Crunchbase, AngelList, F6S, etc.)
  - Search engines (Google, Bing, DuckDuckGo)
  - Healthcare news sources and press releases
- **Geographic Focus**: Prioritizes German and European companies
- **URL Validation**: Comprehensive cleaning, deduplication, and validation
- **Rate Limiting**: Respects robots.txt and implements intelligent delays
- **Error Handling**: Robust retry logic and error recovery
- **Output Formats**: CSV and JSON with detailed metadata

## 🏗️ Architecture

```
├── config.py              # Configuration and constants
├── models.py               # Data models and structures
├── nlp_processor.py        # NLP analysis and healthcare filtering
├── url_validator.py        # URL validation and cleaning
├── scrapers/
│   ├── base_scraper.py     # Base scraper class
│   ├── directory_scraper.py # Startup directory scraper
│   └── search_scraper.py   # Search engine scraper
├── main.py                 # Main orchestrator
└── requirements.txt        # Dependencies
```

## 🚀 Quick Start

### 1. Installation

```bash
# Clone the repository
git clone <repository-url>
cd healthcare-startup-discovery

# Install dependencies
pip install -r requirements.txt

# Download NLTK data (will be done automatically on first run)
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
```

### 2. Configuration

Optional: Set API keys for enhanced functionality:

```bash
export CRUNCHBASE_API_KEY="your_crunchbase_api_key"
export LINKEDIN_API_KEY="your_linkedin_api_key"
```

### 3. Run the Discovery

```bash
python main.py
```

## 📊 Output

The system generates several output files:

1. **CSV File**: `healthcare_startups_YYYYMMDD_HHMMSS.csv`
   - Company name, URL, description, country, confidence score
   - Healthcare keywords matched
   - Source information and discovery timestamp

2. **JSON File**: `healthcare_startups_YYYYMMDD_HHMMSS.json`
   - Complete structured data with all metadata
   - Session information and statistics

3. **Summary Report**: `healthcare_startups_YYYYMMDD_HHMMSS_summary.txt`
   - Discovery statistics and analysis
   - Country and source distribution
   - Top companies by confidence score

## 🎛️ Configuration Options

### Main Parameters

```python
# In main.py, adjust these parameters:
sources = ['directories', 'search']  # Data sources to use
max_companies = 500                  # Maximum companies to discover
output_format = 'both'              # 'csv', 'json', or 'both'
```

### Advanced Configuration

Edit `config.py` to customize:

- **Geographic Focus**: Add/remove target countries
- **Healthcare Keywords**: Extend keyword lists for better filtering
- **Rate Limiting**: Adjust delays and concurrent requests
- **Data Sources**: Add new directories or news sources

## 🔍 Data Sources

### Startup Directories
- Crunchbase
- AngelList (Wellfound)
- F6S
- EU-Startups
- German-Startups
- Healthcare-specific directories

### Search Engines
- DuckDuckGo (primary, less restrictive)
- Google (with careful rate limiting)
- Bing

### News Sources
- Healthcare IT News
- MobiHealthNews
- Fierce Healthcare
- Health Europa

## 🧠 NLP Processing

The system uses sophisticated NLP techniques:

- **Multilingual Keywords**: English and German healthcare terms
- **Stemming**: Porter and Snowball stemmers for better matching
- **Semantic Similarity**: TF-IDF vectorization for relevance scoring
- **Geographic Detection**: Pattern matching for European countries
- **Confidence Scoring**: Multi-factor relevance assessment

## 🛡️ Ethical Scraping

The system follows best practices:

- **robots.txt Compliance**: Checks and respects robots.txt files
- **Rate Limiting**: Configurable delays between requests
- **User Agent Rotation**: Prevents blocking
- **Error Handling**: Graceful failure recovery
- **Respectful Scraping**: Conservative default settings

## 📈 Performance

- **Scalable**: Handles thousands of URLs efficiently
- **Concurrent**: Asynchronous processing for speed
- **Memory Efficient**: Streaming processing where possible
- **Configurable**: Adjustable concurrency and rate limits

## 🔧 Customization

### Adding New Scrapers

Create a new scraper by extending `BaseScraper`:

```python
from scrapers.base_scraper import BaseScraper

class CustomScraper(BaseScraper):
    async def scrape(self, **kwargs) -> ScrapingResult:
        # Implement custom scraping logic
        pass
```

### Extending NLP Processing

Add new healthcare keywords or improve filtering:

```python
# In config.py
HEALTHCARE_KEYWORDS.update({
    'your_custom_keyword',
    'another_healthcare_term'
})
```

### Custom Output Formats

Extend the output generation in `main.py`:

```python
async def _generate_custom_output(self, companies, filename):
    # Implement custom output format
    pass
```

## 🐛 Troubleshooting

### Common Issues

1. **Rate Limiting**: Increase delays in scraper configuration
2. **Memory Usage**: Reduce `max_companies` parameter
3. **Network Errors**: Check internet connection and retry
4. **Empty Results**: Verify target sources are accessible

### Logging

Check `healthcare_discovery.log` for detailed information:

```bash
tail -f healthcare_discovery.log
```

### Debug Mode

Enable verbose logging:

```python
# In config.py
LOG_LEVEL = 'DEBUG'
```

## 📝 Example Output

### CSV Structure
```csv
Company Name,Website URL,Description,Country,Source Type,Confidence Score,Keywords Matched
MedTech Solutions,https://medtech-example.com,Digital health platform,germany,directory,0.857,healthcare;digital health;medtech
```

### JSON Structure
```json
{
  "session_info": {
    "session_id": "uuid-here",
    "total_companies": 245,
    "sources_scraped": 15
  },
  "companies": [
    {
      "name": "HealthTech GmbH",
      "url": "https://example.com",
      "confidence_score": 0.892,
      "keywords_matched": ["healthcare", "digital"],
      "country": "germany"
    }
  ]
}
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Implement your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## ⚠️ Disclaimer

This tool is for research and educational purposes. Always respect website terms of service and applicable laws when scraping data. The authors are not responsible for misuse of this software.

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section
2. Review the logs for error details
3. Open an issue on GitHub
4. Contact the development team

---

**Note**: This system is designed to be respectful of website resources and follows ethical scraping practices. Always ensure compliance with local laws and website terms of service when using this tool.