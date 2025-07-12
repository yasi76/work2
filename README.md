# Enhanced Healthcare Company Directory Scraper

A comprehensive web scraper for extracting German healthcare companies from multiple high-quality directory sources.

## 🚀 Features

- **Multiple Data Sources**: Scrapes from 6+ high-quality German healthcare directories
- **Intelligent Deduplication**: Avoids extracting companies already in your database
- **Selenium Support**: Handles JavaScript-heavy websites
- **Data Enrichment**: Automatically finds missing company websites
- **Flexible Configuration**: Run specific sources or all sources
- **Comprehensive Logging**: Detailed progress tracking and error handling
- **Multiple Output Formats**: CSV and JSON export

## 📊 Data Sources

### Primary Sources (High Quality)
1. **BVMed** - German Medical Technology Association (~300 companies)
2. **SPECTARIS** - German Industry Association for Optics/Medical Tech (~400 companies)
3. **Digital Health Hub Berlin** - Startup ecosystem (~80 companies)
4. **BioM** - Bavaria Biotech Cluster (~200 companies)
5. **eHealth Initiative Germany** - Digital health network (~200 companies)
6. **Healthcare Blogs** - Startup articles and mentions

### Additional Sources Available
- Regional health clusters (BioRegion Stern, BioRN)
- Government directories (GTAI)
- Trade show directories (MEDICA, ConhIT)
- VC portfolios (EQT, Earlybird, Rocket Internet)
- Academic spin-offs (Helmholtz, Max Planck)

## � Requirements

- Python 3.8+
- Chrome browser (for Selenium)
- ChromeDriver (automatically managed)

## 🛠️ Installation

1. **Clone or download the files**
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Install ChromeDriver** (if not already installed):
   ```bash
   # ChromeDriver will be automatically downloaded by webdriver-manager
   # No manual installation required
   ```

## 🏃‍♂️ Usage

### Basic Usage
```bash
python run_scraper.py
```

### Advanced Usage
```bash
# Run without Selenium (faster, but may miss some data)
python run_scraper.py --no-selenium

# Scrape specific sources only
python run_scraper.py --sources bvmed spectaris

# Limit number of companies
python run_scraper.py --max-companies 500

# Custom output directory
python run_scraper.py --output-dir /path/to/results
```

### Available Source Options
- `bvmed` - BVMed Medical Technology Association
- `spectaris` - SPECTARIS Industry Association
- `digital_health_hub` - Digital Health Hub Berlin
- `biom` - BioM Bavaria Biotech Cluster
- `ehealth` - eHealth Initiative Germany
- `blogs` - Healthcare startup blogs

## 📁 Output Files

Results are saved in the `output/` directory (configurable):

- **enhanced_healthcare_companies.csv** - Spreadsheet format
- **enhanced_healthcare_companies.json** - JSON format

### Data Fields
- `name` - Company name
- `website` - Company website URL
- `description` - Company description
- `location` - Location/address
- `city` - Extracted city
- `category` - Business category
- `tags` - Source tags and classifications
- `source_directory` - Original source URL
- `domain` - Extracted domain name
- `employees` - Employee count (if available)
- `funding` - Funding information (if available)
- `founded` - Founded date (if available)
- `phone` - Phone number (if available)
- `email` - Email address (if available)

## 🔧 Configuration

### Your Existing Companies
The scraper includes your existing companies to avoid duplicates:
- Edit the `_load_known_companies()` method in `enhanced_healthcare_scraper.py`
- Add your company domains to the `known_websites` set

### Rate Limiting
Default delays between requests:
- 3-5 seconds between different sources
- 1-2 seconds between individual requests
- Configurable in the scraper code

## 📊 Performance

### Expected Results
- **BVMed**: 200-300 medical device companies
- **SPECTARIS**: 300-400 optics/medical companies
- **Digital Health Hub**: 50-80 startups
- **BioM**: 150-200 biotech companies
- **eHealth Initiative**: 150-200 digital health companies
- **Healthcare Blogs**: 50-100 startup mentions

### Runtime
- **Full extraction**: 10-15 minutes (with Selenium)
- **Without Selenium**: 3-5 minutes (may miss some data)
- **Single source**: 1-3 minutes

## 🛡️ Best Practices

### Legal Compliance
- Respects robots.txt files
- Implements reasonable rate limiting
- Follows website terms of service
- GDPR compliant data handling

### Technical Considerations
- Uses headless browser for JavaScript sites
- Implements retry logic for failed requests
- Comprehensive error handling
- Memory efficient processing

## 📈 Extending the Scraper

### Adding New Sources
1. Create a new extraction method in `EnhancedHealthcareScraper`
2. Add the method to the `extraction_methods` list
3. Update the `source_mapping` in `run_scraper.py`

Example:
```python
def extract_from_new_source(self) -> List[HealthcareCompany]:
    companies = []
    # Your extraction logic here
    return companies
```

### Customizing Data Fields
1. Modify the `HealthcareCompany` dataclass
2. Update extraction methods to populate new fields
3. Adjust output formatting if needed

## 🐛 Troubleshooting

### Common Issues

1. **Selenium not working**:
   ```bash
   # Install Chrome and ChromeDriver
   # Or run without Selenium:
   python run_scraper.py --no-selenium
   ```

2. **Rate limiting errors**:
   - Increase delays in the scraper code
   - Run fewer sources at once

3. **No companies extracted**:
   - Check website structure changes
   - Verify internet connection
   - Review logs for specific errors

4. **Memory issues**:
   - Use `--max-companies` to limit results
   - Process sources individually

### Debug Mode
Enable debug logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📄 License

This scraper is for educational and research purposes. Please respect website terms of service and implement appropriate rate limiting.

## 🤝 Contributing

1. Fork the repository
2. Add new data sources
3. Improve extraction logic
4. Submit pull requests

## 📞 Support

For questions or issues:
1. Check the troubleshooting section
2. Review the logs for specific errors
3. Test with individual sources first
4. Verify website accessibility

## 📊 Example Output

```
� EXTRACTION COMPLETED SUCCESSFULLY!
============================================================
📊 EXTRACTION SUMMARY
============================================================
Total companies extracted: 847
Companies with websites: 692 (81.7%)
Companies with descriptions: 634 (74.9%)
Output saved to: output/

📈 BREAKDOWN BY CATEGORY:
  Medical Technology: 312 companies
  Digital Health: 178 companies
  Biotechnology: 156 companies
  eHealth: 134 companies
  Healthcare Startup: 67 companies

🏢 SAMPLE COMPANIES:
  1. Siemens Healthineers AG
     🌐 https://www.siemens-healthineers.com
     📍 Erlangen, Germany
     🏷️  Medical Technology

  2. Ada Health GmbH
     🌐 https://ada.com
     📍 Berlin, Germany
     🏷️  Digital Health
```

## 🔄 Updates

The scraper is designed to be easily maintainable:
- Website structure changes can be quickly adapted
- New sources can be added without major changes
- Rate limiting and error handling can be fine-tuned
- Output formats can be extended

For the latest updates and additional sources, check the `additional_healthcare_sources.md` file.