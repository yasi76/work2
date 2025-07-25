# Enhanced Product Extraction Pipeline

This enhanced version addresses the key issues identified in the original extraction pipeline:
- **High false negatives** - Now uses JS rendering and UI pattern detection
- **Weak product name extraction** - Enhanced with fuzzy matching and better filtering
- **Improved classification** - Uses embeddings and context-aware classification
- **Better ground truth matching** - Fuzzy matching with multiple algorithms

## Key Improvements

### 1. JavaScript Rendering Support
- **Auto mode**: Tries HTML first, falls back to JS if no products found
- **Always mode**: Always uses JS rendering (for SPAs)
- **Never mode**: HTML only (fastest)
- Supports both Playwright (recommended) and Selenium

### 2. Advanced Product Detection
- **UI Pattern Selectors**: Detects common patterns like `.product-card`, `.product-tile`
- **Structured Data**: Enhanced schema.org support including MedicalDevice
- **Smart Heading Analysis**: Context-aware confidence scoring
- **Link Pattern Detection**: Finds products in navigation and links
- **NLP Extraction**: Uses spaCy for entity recognition

### 3. Fuzzy Ground Truth Matching
- **Multiple algorithms**: Token set ratio, partial ratio, Jaccard similarity
- **75% threshold**: Configurable similarity threshold
- **Token matching**: Handles word order variations
- Shows exactly which GT products were found/missed

### 4. Enhanced Classification
- **Embedding-based**: Uses sentence transformers for semantic similarity
- **Context-aware**: Analyzes surrounding text for better classification
- **Multi-language**: Keywords in English, German, French, Spanish

## Installation

### Basic Installation
```bash
pip install -r requirements_enhanced.txt
```

### Post-Installation Setup
```bash
# For NLP support
python -m spacy download en_core_web_sm

# For JavaScript rendering (choose one)
playwright install chromium  # Recommended
# OR download ChromeDriver for Selenium
```

## Usage

### Basic Usage
```bash
# Auto mode - tries HTML first, then JS if needed
python extract_products_enhanced.py companies.json

# Always use JS rendering (for SPAs)
python extract_products_enhanced.py companies.json --js always

# HTML only (fastest)
python extract_products_enhanced.py companies.json --js never
```

### Advanced Options
```bash
# Process with all features
python extract_products_enhanced.py companies.json \
  --js auto \
  --output-prefix results \
  --max-workers 2 \
  --limit 10

# Clear cache and run fresh
python extract_products_enhanced.py companies.json --clear-cache

# Disable caching
python extract_products_enhanced.py companies.json --no-cache
```

## Output Files

### 1. `enhanced_products.json`
Detailed results with:
- Products found with confidence scores
- Extraction methods used
- Ground truth validation results
- JS rendering status

### 2. `enhanced_products.csv`
Flattened CSV with columns:
- company_name
- company_url
- product_name
- product_type
- confidence (0-1)
- extraction_method
- is_ground_truth

### 3. `enhanced_stats.json`
Comprehensive statistics:
- Ground truth accuracy
- Confidence distribution
- Missed products detail
- Extraction configuration

## Example Results

### Successful Extraction
```json
{
  "company_name": "Actimi",
  "products": [
    {
      "name": "Actimi Herzinsuffizienz Set",
      "type": "hardware",
      "confidence": 0.95,
      "method": "selector_.product-card",
      "context": "Remote monitoring solution for heart failure patients..."
    }
  ],
  "ground_truth_found": ["Actimi Herzinsuffizienz Set", "Actimi Notaufnahme-Set"],
  "ground_truth_missed": [],
  "js_rendering_used": true
}
```

### Ground Truth Validation
The extractor shows exactly which products were found:
```
Ground Truth Validation:
  Found: 45/50 (90.0%)
  Missed: 5/50 (10.0%)

Missed GT products:
  Kranus Health: Kranus Mictera
  DocRobin: DocRobin
  auvisus: auvisus
```

## Performance Tips

### 1. JS Rendering
- Use `--js auto` for best balance of speed and accuracy
- Limit workers to 2 when using JS rendering to avoid resource issues
- Consider `--js never` for initial testing

### 2. Caching
- HTML content is cached for 24 hours by default
- Use `--clear-cache` when website content changes
- Cache significantly speeds up re-runs

### 3. Parallel Processing
- Default: 3 workers
- With JS: Max 2 workers recommended
- Adjust based on your system resources

## Troubleshooting

### No products found
1. Check if site requires JS: `--js always`
2. Check product paths in browser
3. Add custom selectors if needed

### Low confidence scores
- Review products with confidence < 0.7
- May indicate generic or incorrect extractions

### Missing ground truth products
1. Check fuzzy matching threshold (default 75%)
2. Product might be on subpage not checked
3. Product name might have changed

### Browser issues
```bash
# Playwright issues
playwright install chromium
playwright install-deps

# Selenium issues
# Download ChromeDriver matching your Chrome version
```

## Extending the Extractor

### Add Custom Selectors
```python
self.product_selectors.extend([
    '.custom-product-class',
    '[data-custom-product]'
])
```

### Add Product Paths
```python
self.product_paths.extend([
    '/notre-gamme',  # French
    '/unsere-losungen'  # German
])
```

### Adjust Fuzzy Matching Threshold
```python
# In _fuzzy_match_ground_truth method
if best_score >= 0.75:  # Change from 0.75 to your preference
```

## Comparison with Original

| Feature | Original | Enhanced |
|---------|----------|----------|
| JS Rendering | ❌ No | ✅ Yes (Auto/Always/Never) |
| Fuzzy GT Matching | ❌ Basic | ✅ Advanced (Multiple algorithms) |
| UI Pattern Detection | ❌ Limited | ✅ Extensive selectors |
| Classification | Basic keywords | Embeddings + Context |
| False Negatives | High | Significantly reduced |
| Confidence Scoring | Basic | Multi-factor |

## Next Steps

1. **Fine-tune thresholds** based on your results
2. **Add more UI selectors** for specific sites
3. **Expand ground truth** for better validation
4. **Train custom embeddings** on health product names
5. **Add language detection** for better multi-language support