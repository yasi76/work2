# Split Scripts for Digital Health Startup Data Extraction

This repository now contains **four standalone, minimal scripts** that were split from the monolithic `ultimate_startup_discovery.py` script. Each script has a specific purpose and outputs a JSON file for the next stage.

## 🚀 Scripts Overview

### 1. `discover_urls.py`
**Purpose**: Collects URLs using hardcoded, ground truth, and search sources  
**Outputs**: `final_startup_urls.json`  
**Description**: Discovers and consolidates startup URLs from multiple sources with confidence scoring

### 2. `extract_company_names.py`
**Purpose**: Extracts clean company names from startup websites  
**Inputs**: `final_startup_urls.json`  
**Outputs**: `company_name_mapping.json`  
**Description**: Uses webpage scraping and domain analysis to extract company names

### 3. `extract_products.py`
**Purpose**: Extracts product names from web pages and ground truth data  
**Inputs**: `final_startup_urls.json`  
**Outputs**: `product_names.json`  
**Description**: Identifies and categorizes digital health products from startup websites

### 4. `extract_locations.py`
**Purpose**: Finds German/European city locations  
**Inputs**: `final_startup_urls.json`  
**Outputs**: `finding_ort.json`  
**Description**: Extracts location data using contact/impressum pages, structured data, and regex patterns

## 📋 Usage Instructions

Run the scripts in order:

```bash
# Step 1: Discover URLs
python3 discover_urls.py

# Step 2: Extract company names
python3 extract_company_names.py

# Step 3: Extract product names
python3 extract_products.py

# Step 4: Extract locations
python3 extract_locations.py
```

## 📊 Output Files

Each script generates a JSON file with structured data:

- `final_startup_urls.json` - List of discovered URLs with metadata
- `company_name_mapping.json` - URL to company name mapping
- `product_names.json` - Products found for each URL
- `finding_ort.json` - Location data for each startup

## ✨ Benefits

- **Modular**: Each script has a single responsibility
- **Debuggable**: Easy to identify issues in specific extraction steps
- **Reusable**: Can re-run individual steps without starting over
- **Maintainable**: Simple code that's easy to understand and modify

## 🔧 Requirements

```bash
pip install requests beautifulsoup4
```

## 🎯 Next Steps

After running all scripts, you can:
1. Merge the data into a final CSV/JSON dataset
2. Perform data quality checks
3. Build visualization or analysis tools
4. Create a searchable startup directory