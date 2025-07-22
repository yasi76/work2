# Digital Health Startup Extraction Pipeline

This repository contains two specialized scripts for extracting company names and product information from digital health startup websites.

## Overview

The extraction pipeline consists of two separate scripts:

1. **`extract_company_names.py`** - Extracts company names from validated startup URLs
2. **`extract_products.py`** - Extracts product names and types from company websites

## Prerequisites

### Required Dependencies
```bash
pip install requests beautifulsoup4
```

### Optional Dependencies (for enhanced extraction)
```bash
# For NLP-based extraction
pip install spacy
python -m spacy download en_core_web_sm

# For JavaScript-heavy websites
pip install playwright
playwright install
```

## Usage

### Step 1: Extract Company Names

First, extract company names from your validated startup data:

```bash
# Basic usage (uses existing metadata)
python extract_company_names.py validated_startups.json

# Refetch pages for more accurate extraction
python extract_company_names.py validated_startups.json --refetch

# Use JavaScript rendering for dynamic sites
python extract_company_names.py validated_startups.json --refetch --js

# Customize output prefix
python extract_company_names.py validated_startups.json --output-prefix health_startups
```

#### Output Files:
- `startups_with_names.json` - Full data with company names
- `startups_with_names.csv` - CSV format
- `startups_company_names.txt` - Simple list of names and URLs
- `startups_extraction_stats.json` - Extraction statistics

### Step 2: Extract Products

After extracting company names, extract product information:

```bash
# Basic usage
python extract_products.py startups_with_names.json

# Use JavaScript rendering
python extract_products.py startups_with_names.json --js

# Limit to first N companies (for testing)
python extract_products.py startups_with_names.json --limit 10

# Customize output and workers
python extract_products.py startups_with_names.json --output-prefix digital_health --max-workers 10
```

#### Output Files:
- `products_products.json` - Detailed product data per company
- `products_products.csv` - Flattened CSV with all products
- `products_product_stats.json` - Extraction statistics and validation

## Product Extraction Features

### 1. Multi-Page Crawling
The product extractor checks multiple pages per company:
- Homepage
- Common product pages: `/products`, `/solutions`, `/services`, etc.
- German pages: `/produkte`, `/leistungen`, `/angebote`

### 2. Product Type Classification
Products are classified into categories:
- **App** - Mobile applications
- **Software** - SaaS, web-based tools
- **Wearable** - Devices, sensors, monitors
- **Service** - Consulting, therapy, coaching
- **Platform** - Comprehensive systems
- **Hardware** - Physical equipment, kits
- **AI Tool** - AI/ML-based solutions

### 3. Ground Truth Validation
The extractor includes built-in ground truth data to validate accuracy:
- Tracks which known products were found
- Reports missed products
- Calculates extraction accuracy

### 4. Extraction Strategies
Multiple strategies for finding products:
- Product cards and tiles
- Heading analysis
- Meta tag extraction
- Schema.org structured data
- NLP entity recognition (if spaCy installed)
- Context-based classification

## Example Workflow

```bash
# 1. Validate startup URLs (using existing script)
python evaluate_health_startups.py startup_urls.json

# 2. Extract company names
python extract_company_names.py validated_output.json --refetch

# 3. Extract products
python extract_products.py startups_with_names.json --js

# 4. Check results
cat products_product_stats.json
```

## Output Format

### Company Names Output
```json
{
  "url": "https://example.com",
  "company_name": "Example Health",
  "name_extraction_method": "og:site_name",
  "is_live": true,
  "is_health_related": true
}
```

### Products Output
```json
{
  "company_name": "Example Health",
  "url": "https://example.com",
  "product_names": ["Example App", "Example Platform"],
  "product_types": {
    "Example App": "app",
    "Example Platform": "platform"
  },
  "ground_truth_found": ["Example App"],
  "ground_truth_missed": []
}
```

## Tips for Better Results

1. **Use JavaScript rendering** (`--js` flag) for modern single-page applications
2. **Run with refetch** for company names to get the most accurate data
3. **Check extraction statistics** to understand coverage and accuracy
4. **Update domain mappings** for tricky domain-to-name mappings:
   ```bash
   python extract_company_names.py input.json --update-domain-map custom_mappings.json
   ```

## Troubleshooting

- **Low extraction rate**: Try using `--js` flag for JavaScript-heavy sites
- **Timeout errors**: Increase timeout in the code or reduce `--max-workers`
- **Missing products**: Check if products are on subpages not in the default list

## Ground Truth Format

To add your own ground truth for validation, modify the `_load_ground_truth()` method in `extract_products.py`:

```python
product_url_dict = {
    "Product Name": "https://company-url.com",
    # Add more products...
}
```