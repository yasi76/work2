# Digital Health Extraction Pipeline - Summary

## What Was Done

I've created a structured extraction pipeline by separating company name extraction and product extraction into two distinct, specialized scripts:

### 1. Updated `extract_company_names.py`
- **Focus**: Exclusively extracts company names from validated startup URLs
- **Key Features**:
  - Multiple extraction strategies (OpenGraph, schema.org, NLP, URL parsing)
  - Domain-to-name mapping support
  - Refetch capability for better accuracy
  - JavaScript rendering support (optional)
  - Detailed extraction statistics

### 2. Created `extract_products.py` (New)
- **Focus**: Specialized product extraction with type classification
- **Key Features**:
  - Multi-page crawling (checks /products, /solutions, etc.)
  - Product type classification (app, software, wearable, service, platform, etc.)
  - Built-in ground truth validation
  - Context-aware extraction strategies
  - Detailed validation metrics

### 3. Documentation
- **README_extraction.md**: Complete usage guide for both scripts
- **test_extraction.py**: Automated test script to verify the pipeline

## Key Improvements

1. **Separation of Concerns**: Company names and products are now extracted by specialized scripts
2. **Ground Truth Integration**: The product extractor includes your provided ground truth data for validation
3. **Enhanced Product Classification**: Products are automatically classified into types based on keywords and context
4. **Multi-Page Support**: The product extractor crawls multiple pages per company for comprehensive coverage
5. **Better Error Handling**: Both scripts handle various edge cases and provide detailed logging

## Usage Workflow

```bash
# Step 1: Extract company names
python extract_company_names.py validated_startups.json --refetch

# Step 2: Extract products with validation
python extract_products.py startups_with_names.json --js

# Optional: Run tests
python test_extraction.py
```

## Output Structure

### Company Names Output
- JSON file with company names and extraction methods
- CSV for easy analysis
- Text file with name-URL pairs
- Statistics file showing extraction success rates

### Products Output
- JSON with detailed product information per company
- CSV with flattened product data
- Statistics including ground truth validation accuracy
- Product type distribution analysis

## Ground Truth Validation

The product extractor validates against your provided ground truth:
- Tracks which known products were found
- Reports missed products
- Calculates overall accuracy percentage

This helps identify areas where extraction can be improved and ensures quality control.

## Next Steps

1. **Run Full Extraction**: Process your complete validated startup dataset
2. **Review Statistics**: Check extraction accuracy and coverage
3. **Iterate**: Update extraction strategies based on missed products
4. **Expand Ground Truth**: Add more known products for better validation