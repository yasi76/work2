# Digital Health Startup URL Evaluator

This Python script evaluates discovered digital health startup URLs to check if they are live, health-related, and relevant to the European/German digital health ecosystem.

## Features

- **Parallel Processing**: Evaluates multiple URLs concurrently for faster processing
- **Health Relevance Scoring**: Assigns scores (0-10) based on health-related keyword matches
- **Multi-language Support**: Recognizes health keywords in English, German, French, and Dutch
- **Region Detection**: Identifies DACH (Germany, Austria, Switzerland) and European startups
- **Suspicious Page Detection**: Flags parking pages, domain-for-sale, and other non-relevant pages
- **Comprehensive Error Handling**: Gracefully handles timeouts, SSL errors, and connection issues
- **Detailed Logging**: Creates a log file with all evaluation details
- **Multiple Output Formats**: Generates both JSON and CSV output files

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

```bash
python evaluate_health_startups.py input_file.json
```

### Advanced Usage

```bash
python evaluate_health_startups.py input_file.json --output-prefix health_startups --max-workers 20
```

### Command Line Arguments

- `input_file`: Path to input JSON or CSV file containing startup URLs (required)
- `--output-prefix`: Prefix for output files (default: "startups")
- `--max-workers`: Maximum number of parallel workers (default: 10)

## Input Format

The script accepts either JSON or CSV input files.

### JSON Format Options:

1. **Discovery script output format** (from `ultimate_startup_discovery.py`):
```json
{
  "discovery_timestamp": "2025-07-21T23:58:40",
  "total_urls_discovered": 150,
  "analysis": {...},
  "urls": [
    "https://example1.com",
    "https://example2.com"
  ]
}
```

2. **List of URLs (simple format)**:
```json
[
  "https://example1.com",
  "https://example2.com",
  "example3.com"
]
```

3. **List of objects with metadata (detailed format)**:
```json
[
  {
    "url": "https://example.com",
    "confidence": 0.95,
    "method": "web_search",
    "country": "DE",
    "category": "Digital Health"
  }
]
```

4. **Discovery output with detailed URLs**:
```json
{
  "discovery_timestamp": "2025-07-21T23:58:40",
  "urls": [
    {
      "url": "https://example.com",
      "confidence": 0.95,
      "method": "web_search"
    }
  ]
}
```

### CSV Format:
```csv
url,confidence,method,status_code,health_score,country,category
https://example.com,0.95,web_search,,,DE,Digital Health
```

The script automatically detects the format and handles all cases. Optional fields from the discovery phase will be preserved in the output.

## Output Files

The script generates three output files:

1. **`{prefix}_validated.json`**: Complete evaluation results in JSON format
2. **`{prefix}_validated.csv`**: Complete evaluation results in CSV format
3. **`{prefix}_summary.json`**: Summary statistics of the evaluation

## Output Fields

Each evaluated startup will have the following fields:

- `url`: Original URL
- `status_code`: HTTP response status code
- `final_url`: Final URL after redirects
- `page_title`: Page title from HTML
- `meta_description`: Meta description content
- `health_relevance_score`: Score from 0-10 based on health keyword matches
- `is_live`: Boolean indicating if the website is accessible
- `is_health_related`: Boolean (True if health_relevance_score >= 3)
- `language`: Detected language code
- `region`: DACH, Europe, or Unknown
- `matched_keywords`: List of health-related keywords found
- `is_suspicious`: Boolean indicating if it's a parking/suspicious page
- `error`: Error message if evaluation failed
- `evaluation_timestamp`: ISO timestamp of when the URL was evaluated

## Health Keywords

The script searches for health-related keywords in multiple languages:

- **English**: health, medical, care, therapy, doctor, patient, wellness, mental, clinical, pharma, medicine, hospital, diagnostic, treatment, healthcare, telemedicine, digital health, biotech, medtech, ehealth, mhealth
- **German**: gesundheit, medizin, pflege, therapie, arzt, ärztin, patient, wellness, mental, klinik, pharma, krankenhaus, diagnostik, behandlung, gesundheitswesen, telemedizin, digital health, biotech, medtech, ehealth, mhealth, praxis, apotheke, gesundheitsapp
- **French**: santé, médical, soin, thérapie, médecin, patient, bien-être, mental, clinique, pharma, hôpital, diagnostic, traitement, télémédecine
- **Dutch**: gezondheid, medisch, zorg, therapie, arts, patiënt, welzijn, mentaal, kliniek, ziekenhuis, behandeling

## Performance

- The script uses parallel processing to evaluate multiple URLs simultaneously
- Default configuration uses 10 workers
- Typically processes ~200 URLs in under 10 minutes
- Each URL has a 10-second timeout to prevent hanging on slow sites

## Logging

The script creates a `startup_evaluation.log` file with detailed information about:
- Each URL evaluation
- Errors and warnings
- Summary statistics

## Example Summary Output

```json
{
  "total_evaluated": 150,
  "live_websites": 120,
  "health_related": 95,
  "suspicious_pages": 5,
  "evaluation_time_seconds": 245.67,
  "average_time_per_url": 1.64,
  "region_distribution": {
    "DACH": 65,
    "Europe": 30,
    "Unknown": 55
  },
  "error_distribution": {
    "Timeout": 15,
    "Connection Error": 10,
    "SSL Error": 5
  }
}
```

## Tips for Best Results

1. **Input Quality**: Ensure URLs in the input file are properly formatted
2. **Network Speed**: Run on a system with good internet connectivity
3. **Parallel Workers**: Increase `--max-workers` for faster processing (but be mindful of rate limits)
4. **Log Monitoring**: Check the log file for detailed error information

## Troubleshooting

- **SSL Errors**: Some older websites may have certificate issues
- **Timeouts**: Increase the timeout in the code if needed (default: 10 seconds)
- **Rate Limiting**: If you encounter rate limiting, reduce the number of workers