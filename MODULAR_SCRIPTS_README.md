# Modular Digital Health Startup Data Collection Scripts

## Overview

The monolithic data collection script has been refactored into four standalone, minimal scripts for better maintainability and debugging.

## 🧩 Script Architecture

### 1. **discover_urls.py**
- **Purpose**: Collects startup URLs from hardcoded lists and curated sources
- **Input**: None (contains hardcoded data)
- **Output**: `final_startup_urls.json`
- **Features**:
  - Merges hardcoded URLs with additional curated sources
  - Deduplicates URLs automatically
  - Outputs sorted list of unique URLs

### 2. **extract_company_names.py**
- **Purpose**: Extracts company names from startup URLs
- **Input**: `final_startup_urls.json`
- **Output**: `company_name_mapping.json`
- **Features**:
  - Uses ground truth data for known companies
  - Falls back to web scraping (OpenGraph, schema.org, title tags)
  - Domain name mapping for difficult cases
  - Parallel processing for speed

### 3. **extract_products.py**
- **Purpose**: Extracts product names from startup websites
- **Input**: `final_startup_urls.json`
- **Output**: `product_names.json`
- **Features**:
  - Ground truth product data for known companies
  - Searches product-specific pages (/products, /solutions, etc.)
  - Smart product name detection using keywords
  - Extracts up to 5 products per company

### 4. **extract_locations.py**
- **Purpose**: Finds German/European city locations
- **Input**: `final_startup_urls.json`
- **Output**: `finding_ort.json`
- **Features**:
  - Comprehensive city mapping (100+ German/European cities)
  - Searches contact/impressum pages
  - Extracts from structured data (schema.org)
  - Regex patterns for German postal codes

### 5. **merge_data.py** (Bonus)
- **Purpose**: Merges all data into a single CSV file
- **Input**: All JSON outputs from above scripts
- **Output**: `digital_health_startups_complete.csv`
- **Features**:
  - Creates complete dataset with all fields
  - Adds data coverage indicators
  - Provides summary statistics

## 🚀 Usage

### Step-by-Step Execution

```bash
# Step 1: Discover all startup URLs
python3 discover_urls.py

# Step 2: Extract company names
python3 extract_company_names.py

# Step 3: Extract product information
python3 extract_products.py

# Step 4: Extract locations
python3 extract_locations.py

# Step 5: (Optional) Merge all data into CSV
python3 merge_data.py
```

### Run All Scripts
```bash
# Create a simple runner script
python3 discover_urls.py && \
python3 extract_company_names.py && \
python3 extract_products.py && \
python3 extract_locations.py && \
python3 merge_data.py
```

## 📊 Output Files

| File | Description | Format |
|------|-------------|--------|
| `final_startup_urls.json` | List of all discovered URLs | JSON array |
| `company_name_mapping.json` | URL to company name mapping | JSON object |
| `product_names.json` | URL to product list mapping | JSON object |
| `finding_ort.json` | URL to city/location mapping | JSON object |
| `digital_health_startups_complete.csv` | Complete merged dataset | CSV |

## ✨ Benefits of Modular Structure

1. **Easy Debugging**: Each script focuses on one task
2. **No Overlap**: Each script has clear inputs/outputs
3. **Partial Re-runs**: Re-run only failed stages
4. **Parallel Development**: Different scripts can be improved independently
5. **Resource Efficiency**: Run only what you need
6. **Clear Dependencies**: Linear pipeline with explicit data flow

## 🛠️ Customization

### Adding New URLs
Edit `discover_urls.py` and add URLs to either:
- `get_hardcoded_urls()` - for verified URLs
- `get_additional_urls()` - for curated discoveries

### Improving Extraction
Each extraction script can be enhanced independently:
- Add new ground truth data
- Improve regex patterns
- Add new extraction strategies
- Enhance parallel processing

### Adding New Cities
Edit `extract_locations.py` and add cities to the `city_mappings` dictionary.

## 🐛 Troubleshooting

### Script Fails
- Check the log output for specific errors
- Ensure input files exist (except for discover_urls.py)
- Verify network connectivity for web scraping
- Check Python dependencies (requests, beautifulsoup4, lxml)

### Low Coverage
- Add more ground truth data
- Improve extraction patterns
- Check if websites are blocking requests
- Try different user agents

### Missing Dependencies
```bash
sudo apt-get install python3-requests python3-bs4 python3-lxml
```

## 📈 Data Quality Metrics

After running all scripts, check coverage:
- Company names: ~89% coverage expected
- Products: ~57% coverage expected  
- Locations: ~19% coverage expected (can be improved)

## 🔄 Future Improvements

1. Add web search integration for discovering new startups
2. Implement ML-based name extraction
3. Add geocoding for better location data
4. Create automated testing suite
5. Add data validation and quality checks