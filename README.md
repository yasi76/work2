# Company Name Extractor from URLs

A robust Python solution to extract company names from URLs using multiple methods in priority order. The tool provides both basic and advanced extraction capabilities with confidence scoring.

## Features

### Basic Extractor (`extract_company_name.py`)
- Multiple extraction methods in priority order
- Handles URLs with or without protocol
- Graceful fallback to domain-based extraction
- Session management for better performance

### Advanced Extractor (`extract_company_name_advanced.py`)
- All features from basic extractor plus:
- Confidence scoring (0-1) for each extraction
- Parallel processing for multiple URLs
- JSON-LD and Schema.org support
- Twitter metadata extraction
- Enhanced title cleaning with scoring
- CSV and JSON export capabilities
- Batch processing from files

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Or install manually
pip install requests beautifulsoup4 lxml
```

## Quick Start

### Basic Usage

```python
from extract_company_name import CompanyNameExtractor

# Create extractor
extractor = CompanyNameExtractor()

# Extract company name
result = extractor.extract_company_name("https://floy.health")
print(result['final_result'])  # Output: "Floy"
```

### Advanced Usage

```python
from extract_company_name_advanced import AdvancedCompanyNameExtractor

# Create extractor
extractor = AdvancedCompanyNameExtractor()

# Extract with confidence score
result = extractor.extract_all_methods("https://stripe.com")
print(f"{result['final_result']} (confidence: {result['confidence_score']:.0%})")
# Output: "Stripe (confidence: 90%)"

# Process multiple URLs in parallel
urls = ["https://github.com", "https://stripe.com", "https://floy.health"]
results = extractor.process_urls_parallel(urls)

# Export to CSV
extractor.export_results(results, 'companies.csv')
```

## Extraction Methods (Priority Order)

1. **og:site_name** (95% confidence) - Most reliable for modern websites
2. **JSON-LD structured data** (90% confidence) - Schema.org Organization data
3. **Twitter:site** (85% confidence) - Twitter card metadata
4. **application-name** (85% confidence) - HTML5 application name
5. **Title tag** (75% confidence) - Cleaned and analyzed page title
6. **H1 tags** (70% confidence) - Scored based on location and content
7. **Logo alt text** (65% confidence) - Analyzed logo images
8. **Schema.org microdata** (80% confidence) - Inline structured data
9. **Domain-based** (30-50% confidence) - Fallback from URL structure

## Examples

Run the example script to see all features:

```bash
python example_usage.py
```

This will demonstrate:
- Basic extraction
- Advanced extraction with confidence scores
- Batch processing from file
- Parallel processing
- Filtering by confidence level
- CSV/JSON export

## API Reference

### CompanyNameExtractor

```python
extractor = CompanyNameExtractor(timeout=10)

# Extract company name
result = extractor.extract_company_name(url)
# Returns: {
#     'og_site_name': str or None,
#     'application_name': str or None,
#     'title': str or None,
#     'cleaned_title': str or None,
#     'h1': str or None,
#     'logo_alt': str or None,
#     'domain_based': str or None,
#     'final_result': str or None
# }

# Process multiple URLs
results = extractor.process_urls(urls, delay=1.0)
```

### AdvancedCompanyNameExtractor

```python
extractor = AdvancedCompanyNameExtractor(
    timeout=10,
    use_gpt_cleaning=False,  # Optional GPT enhancement
    openai_api_key=None
)

# Extract with all methods
result = extractor.extract_all_methods(url)
# Returns: {
#     'final_result': str or None,
#     'confidence_score': float (0-1),
#     'extraction_method': str,
#     'timestamp': str,
#     # ... all extraction attempts
# }

# Parallel processing
results = extractor.process_urls_parallel(urls, max_workers=5)

# Export results
extractor.export_results(results, 'output.csv')
```

## Best Practices

1. **For single URLs**: Use basic extractor for simplicity
2. **For bulk processing**: Use advanced extractor with parallel processing
3. **For production**: Review low confidence results (<50%) manually
4. **Rate limiting**: Add delays when processing many URLs from same domain
5. **Error handling**: Check for 'error' key in results when using parallel processing

## Common Issues

1. **SSL Certificate errors**: Some sites have invalid certificates
   - Solution: Domain-based extraction still works as fallback

2. **Generic titles**: Some sites have unhelpful titles like "Home"
   - Solution: Advanced extractor uses multiple methods

3. **Complex domains**: URLs like "get-company.app" need smart parsing
   - Solution: Advanced domain extraction handles prefixes/suffixes

## Output Examples

```
URL: https://floy.health
Company Name: Floy
Confidence: 75%
Method: title

URL: https://stripe.com
Company Name: Stripe
Confidence: 90%
Method: json-ld

URL: https://github.com
Company Name: GitHub
Confidence: 95%
Method: og:site_name
```

## License

MIT License - Feel free to use in your projects!

## Contributing

Improvements welcome! Some ideas:
- Add more extraction methods
- Improve title cleaning patterns
- Add language-specific handling
- Integrate real GPT cleaning
- Add more company indicators