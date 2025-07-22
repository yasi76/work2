# Digital Health Startup Discovery System

A Python toolkit for discovering and analyzing digital health startups in Germany and Europe.

## Overview

This system provides automated tools to:
- 🔍 Discover digital health startup websites
- ✅ Validate URLs and check health relevance
- 🏢 Extract company names intelligently
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

### 4. `evaluate_name_extraction.py`
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

## Workflow Example

```bash
# 1. Discover startups
python ultimate_startup_discovery.py

# 2. Validate discovered URLs
python evaluate_health_startups.py discovered_startups_*.json

# 3. Extract company names
python extract_company_names.py *_validated.json --refetch

# 4. Evaluate accuracy (optional)
python evaluate_name_extraction.py *_with_names.json
```

## Data Format

```json
{
  "url": "https://example.health",
  "company_name": "Example Health GmbH",
  "is_live": true,
  "is_health_related": true,
  "health_score": 0.85,
  "page_title": "Example Health - Digital Solutions",
  "extraction_method": "og:site_name"
}
```

## Tips

- Use `--refetch` for better name extraction accuracy
- Check logs for debugging information
- Process large files with increased timeouts
- Respect rate limits (2s delay by default)

## License

MIT License