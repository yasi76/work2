# Company Name Extractor for Digital Health Startups

This script extracts company names from validated startup URLs using multiple strategies, prioritizing accuracy and handling various edge cases.

## Features

- **Multi-Strategy Extraction**: Uses 7 different strategies to extract company names
- **Fast Processing**: Can extract names from existing validation data without refetching
- **Refetch Option**: Can re-visit websites for more accurate name extraction
- **Parallel Processing**: Uses concurrent requests for faster processing
- **Smart Cleaning**: Removes common suffixes, taglines, and noise from titles
- **Internationalization**: Handles German, French, and other European language patterns

## Installation

Uses the same dependencies as `evaluate_health_startups.py`:

```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage (Extract from existing data)

```bash
python extract_company_names.py validated_urls.json
```

### Advanced Usage (Refetch for accuracy)

```bash
python extract_company_names.py validated_urls.json --output-prefix companies --refetch --max-workers 20
```

### Command Line Arguments

- `input_file`: Validated JSON file from evaluate_health_startups.py (required)
- `--output-prefix`: Prefix for output files (default: "startups")
- `--refetch`: Refetch URLs to extract names (slower but more accurate)
- `--max-workers`: Maximum parallel workers for refetching (default: 10)

## Name Extraction Strategies (Priority Order)

1. **Existing Field**: Uses 'name' field from input data if available
2. **OpenGraph site_name**: `<meta property="og:site_name" content="Company Name"/>`
3. **Application Name**: `<meta name="application-name" content="Company Name"/>`
4. **OpenGraph Title**: `<meta property="og:title" content="Company Name - Tagline"/>`
5. **HTML Title Tag**: Cleaned and processed `<title>` tag content
6. **Schema.org**: Structured data from JSON-LD scripts
7. **URL Domain**: Extracted and formatted from domain name

## Output Files

The script generates three output files:

1. **`{prefix}_with_names.json`**: Complete data with extracted company names
2. **`{prefix}_with_names.csv`**: Same data in CSV format
3. **`{prefix}_company_names.txt`**: Simple list of company names and URLs (only health-related and live sites)

## Output Fields

Each entry includes all original fields plus:

- `company_name`: The extracted company name
- `name_extraction_method`: Which strategy was used to extract the name

## Title Cleaning Patterns

The script removes common patterns from titles:

- Taglines after separators (-, |, •, –, —)
- Common suffixes: Home, Welcome, Official Website, Homepage
- Multi-language patterns: Startseite (German), Accueil (French)
- Company type suffixes: GmbH, AG, Ltd, Inc, etc.

## URL-Based Extraction

When extracting from URLs as a fallback:

- Removes prefixes: www., app., portal., my.
- Handles hyphenated domains: `my-health-app.com` → "My Health App"
- Smart capitalization: `ada.com` → "ADA", `doctolib.de` → "Doctolib"

## Example Results

```json
{
  "url": "https://ada.com",
  "company_name": "Ada",
  "name_extraction_method": "og:site_name"
}
```

## Performance Notes

- **Without refetch**: Processes 1000+ URLs in seconds
- **With refetch**: ~200 URLs per minute (depends on network and server response times)
- Use refetch only when you need the most accurate names

## Tips

1. Run without `--refetch` first to quickly see what can be extracted from existing data
2. Use `--refetch` for final production runs when accuracy is critical
3. Increase `--max-workers` for faster processing (be mindful of rate limits)
4. Check the `name_extraction_method` field to understand the quality of extraction