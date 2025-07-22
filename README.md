# Digital Health Startup Discovery System

A Python toolkit for discovering and analyzing digital health startups in Germany and Europe.

## Overview

This system provides automated tools to:
- 🔍 Discover digital health startup websites
- ✅ Validate URLs and check health relevance
- 🏢 Extract company names intelligently
- 📦 Extract product names and categorize types
- 📊 Evaluate extraction accuracy

## Quick Start

```bash
# Install dependencies
pip install requests beautifulsoup4 lxml

# Run the discovery pipeline
python ultimate_startup_discovery.py
```

## Core Scripts

### 1. `ultimate_startup_discovery.py`
Discovers digital health startups from multiple sources.

**Usage:**
```bash
python ultimate_startup_discovery.py
```

**Output:**
- `discovered_startups_[timestamp].json` - Full data
- `discovered_startups_[timestamp].csv` - Simple CSV format

### 2. `evaluate_health_startups.py`
Validates URLs and checks if they're health-related.

**Usage:**
```bash
python evaluate_health_startups.py input.json
python evaluate_health_startups.py input.json --output-prefix validated
```

**Features:**
- HTTP status checking
- Health keyword matching (EN/DE)
- Metadata extraction
- Concurrent processing

### 3. `extract_company_names.py`
Extracts company names using multiple strategies.

**Usage:**
```bash
# Basic extraction
python extract_company_names.py validated.json

# Advanced extraction (refetch pages)
python extract_company_names.py validated.json --refetch

# With JavaScript support (requires playwright)
python extract_company_names.py validated.json --refetch --js
```

**Extraction Methods:**
- OpenGraph metadata
- Schema.org structured data
- HTML title cleaning
- NLP entity recognition (optional)
- Domain name parsing

### 4. `extract_product_names.py` 🆕
Discovers and categorizes digital health products.

**Usage:**
```bash
python extract_product_names.py startups_with_names.json
python extract_product_names.py startups_with_names.json --max-workers 10
```

**Features:**
- Multi-page crawling (checks /products, /solutions, etc.)
- Product type classification (app, software, wearable, service, etc.)
- Ground truth comparison
- Multiple extraction strategies

**Product Types Detected:**
- `app` - Mobile applications
- `software` - Web platforms, SaaS
- `wearable` - Devices, sensors, monitors
- `set` - Product bundles, kits
- `service` - Digital services, consulting
- `ai_tool` - AI/ML-based tools
- `assistant` - Digital assistants, coaches

### 5. `evaluate_name_extraction.py`
Evaluates extraction accuracy against ground truth.

**Usage:**
```bash
python evaluate_name_extraction.py extracted.json
```

**Output:**
- Accuracy metrics
- Method performance stats
- CSV/JSON reports
- Incorrect extractions list

## Configuration

### `domain_name_map.json`
Maps domains to company names for tricky cases:
```json
{
  "getnutrio.com": "Nutrio",
  "telemed24online.de": "TeleMed24 Online"
}
```

## Optional Features

### NLP Support
```bash
pip install spacy
python -m spacy download en_core_web_sm
```

### JavaScript Rendering
```bash
pip install playwright
playwright install
```

## Complete Workflow

```bash
# 1. Discover startups
python ultimate_startup_discovery.py

# 2. Validate discovered URLs
python evaluate_health_startups.py discovered_startups_*.json

# 3. Extract company names
python extract_company_names.py *_validated.json --refetch

# 4. Extract products
python extract_product_names.py *_with_names.json

# 5. Evaluate accuracy (optional)
python evaluate_name_extraction.py *_with_names.json
```

## Output Files

### Product Extraction Outputs
- `[prefix]_products_[timestamp].json` - Full product data
- `[prefix]_products_[timestamp].csv` - CSV summary
- `[prefix]_product_catalog_[timestamp].txt` - Readable catalog

### Product Data Format
```json
{
  "company_name": "fyzo GmbH",
  "url": "https://fyzo.de/",
  "product_names": ["fyzo Assistant", "fyzo Coach"],
  "product_types": {
    "fyzo Assistant": "app",
    "fyzo Coach": "service"
  },
  "ground_truth_products": ["fyzo Assistant", "fyzo coach"],
  "found_gt_products": ["fyzo Assistant"]
}
```

## Tips

- Use `--refetch` for better extraction accuracy
- Process product extraction with more workers for speed
- Check product-specific pages (/products, /solutions)
- Review the product catalog file for a clean overview
- Ground truth helps evaluate extraction quality

## License

MIT License