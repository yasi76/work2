# Digital Health Startup Extraction Pipeline

This repository contains two specialized scripts for extracting company names and product information from digital health startup websites.

## Overview

The extraction pipeline consists of two separate scripts:

1. **`extract_company_names.py`** - Extracts company names from validated startup URLs
2. **`extract_products.py`** - Extracts product names and types from company websites with advanced features

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

# Use caching to avoid re-downloading pages
python extract_products.py startups_with_names.json --js

# Disable caching for fresh extraction
python extract_products.py startups_with_names.json --no-cache

# Save HTML snippets for manual validation
python extract_products.py startups_with_names.json --save-snippets

# Clear cache before running
python extract_products.py startups_with_names.json --clear-cache

# Full example with all options
python extract_products.py startups_with_names.json --js --output-prefix digital_health --max-workers 10 --save-snippets
```

#### Output Files:
- `products_products.json` - Detailed product data per company with confidence scores
- `products_products.csv` - Flattened CSV with all products and confidence
- `products_product_stats.json` - Extraction statistics, validation, and confidence distribution

## Enhanced Product Extraction Features

### 1. Multi-Page Crawling with Sitemap Support
The product extractor checks multiple sources:
- Homepage
- Sitemap.xml discovery for product pages
- Common product paths: `/products`, `/solutions`, `/services`, etc.
- Multi-language paths: `/produkte`, `/leistungen`, `/produits`, `/productos`

### 2. Advanced Product Type Classification
Products are classified into categories with multi-language support:
- **App** - Mobile applications (keywords: app, application, mobile, anwendung)
- **Software** - SaaS, web-based tools (keywords: software, saas, cloud, plattform)
- **Wearable** - Devices, sensors, monitors (keywords: wearable, device, sensor, gerät)
- **Service** - Consulting, therapy, coaching (keywords: service, dienstleistung, beratung)
- **Platform** - Comprehensive systems (keywords: platform, plattform, portal)
- **Hardware** - Physical equipment, kits (keywords: hardware, equipment, ausstattung)
- **AI Tool** - AI/ML-based solutions (keywords: ai, ki, künstliche intelligenz)

### 3. Confidence Scoring
Each extracted product has a confidence score (0-1) based on:
- Extraction method (schema.org: 0.95, meta tags: 0.9, product cards: 0.8)
- Product name characteristics (length, capitalization, trademark symbols)
- Context relevance
- Generic name filtering

### 4. Ground Truth Validation with Fuzzy Matching
The extractor includes built-in ground truth data to validate accuracy:
- URL normalization for consistent matching (removes www, trailing slashes)
- Fuzzy string matching (85% similarity threshold)
- Tracks which known products were found vs missed
- Calculates extraction accuracy percentage

### 5. Duplicate Detection and Fuzzy Deduplication
- Detects similar product names using fuzzy string matching
- Merges products with >85% name similarity
- Keeps the version with highest confidence
- Tracks alternative names found

### 6. Enhanced Schema.org Support
Extended schema types for better medical/health product detection:
- Product, SoftwareApplication, MobileApplication, WebApplication
- MedicalDevice, MedicalEntity, MedicalService
- CreativeWork, Service, DigitalDocument, Dataset

### 7. HTML Caching
- Caches downloaded HTML for 24 hours to avoid re-downloading
- Significantly speeds up re-runs and testing
- Cache stored in `.cache/` directory
- Can be disabled with `--no-cache` or cleared with `--clear-cache`

### 8. Multi-Language Support
- Product keywords in English, German, French, Spanish
- Generic name filtering in multiple languages
- Language-aware product type classification

### 9. Extraction Strategies
Multiple strategies with different confidence levels:
- Product cards and tiles (0.8 confidence)
- Heading analysis with keywords (0.7 confidence)
- Meta tag extraction (0.9 confidence)
- Schema.org structured data (0.95 confidence)
- List item extraction with context (0.6 confidence)
- NLP entity recognition if spaCy installed (0.5-0.7 confidence)

## Testing

### Run Integration Tests
```bash
# Run the test script
python test_extraction.py
```

### Run Unit Tests
```bash
# Run unit tests for product extraction
python test_product_extraction.py
```

Unit tests cover:
- URL normalization
- Product name validation
- Fuzzy matching and deduplication
- Product type classification
- Ground truth matching
- Schema.org extraction

## Example Workflow

```bash
# 1. Validate startup URLs (using existing script)
python evaluate_health_startups.py startup_urls.json

# 2. Extract company names with refetch
python extract_company_names.py validated_output.json --refetch

# 3. Extract products with all enhancements
python extract_products.py startups_with_names.json --js --save-snippets

# 4. Check results and statistics
cat products_product_stats.json | jq .
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

### Enhanced Products Output
```json
{
  "company_name": "Example Health",
  "url": "https://example.com",
  "normalized_url": "https://example.com",
  "product_names": ["Example App", "Example Platform"],
  "product_types": {
    "Example App": "app",
    "Example Platform": "platform"
  },
  "products": [
    {
      "name": "Example App",
      "type": "app",
      "source_url": "https://example.com/products",
      "confidence": 0.85,
      "extraction_method": "product_card",
      "alternative_names": ["ExampleApp"],
      "merged_from": 2
    }
  ],
  "confidence_scores": {
    "Example App": 0.85,
    "Example Platform": 0.92
  },
  "ground_truth_found": ["Example App"],
  "ground_truth_missed": [],
  "pages_checked": 3
}
```

## Tips for Better Results

1. **Use JavaScript rendering** (`--js` flag) for modern single-page applications
2. **Enable caching** during development to speed up iterations
3. **Save snippets** (`--save-snippets`) to manually validate extractions
4. **Check confidence scores** - products with <0.5 confidence may need review
5. **Review fuzzy matches** - check the `alternative_names` field for merged products
6. **Update domain mappings** for tricky domain-to-name mappings:
   ```bash
   python extract_company_names.py input.json --update-domain-map custom_mappings.json
   ```

## Troubleshooting

- **Low extraction rate**: Try using `--js` flag for JavaScript-heavy sites
- **Timeout errors**: Increase timeout in the code or reduce `--max-workers`
- **Missing products**: Check if products are in sitemap.xml or on subpages not in the default list
- **Low confidence scores**: Review products with confidence <0.5 for false positives
- **Cache issues**: Use `--clear-cache` to start fresh

## Improvements Made

1. **URL Normalization**: Consistent matching by removing www, trailing slashes, and lowercasing
2. **Confidence Scoring**: Each product has a confidence score based on extraction method and validation
3. **Fuzzy Matching**: Similar product names are merged (e.g., "Health App" and "HealthApp")
4. **Enhanced Schema Support**: Detects MedicalDevice, CreativeWork, and other health-related types
5. **Multi-Language**: Supports German, French, Spanish keywords and filtering
6. **HTML Caching**: Speeds up development by caching downloaded pages
7. **Sitemap Discovery**: Automatically finds product pages from sitemap.xml
8. **Generic Name Filtering**: Filters out "our app", "unsere app", etc. in multiple languages
9. **Snippet Saving**: Option to save extraction context for manual validation
10. **Comprehensive Testing**: Unit tests for all major functionality

## Ground Truth Format

To add your own ground truth for validation, modify the `_load_ground_truth()` method in `extract_products.py`:

```python
product_url_dict = {
    "Product Name": "https://company-url.com",
    # Add more products...
}
```

The ground truth is automatically normalized for consistent matching.