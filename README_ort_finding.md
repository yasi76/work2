# Ort (City) Finding Scripts

This repository contains two scripts for finding and extracting city (Ort) information from German startup URLs.

## Scripts Overview

### 1. `finding_ort.py` - Basic Sequential Version
A straightforward implementation that processes URLs sequentially.

**Features:**
- Loads URLs from multiple JSON files
- Uses hardcoded mappings for known URLs
- Attempts to scrape city information from various pages (/impressum, /kontakt, etc.)
- Saves results to JSON and CSV formats
- Tracks failed URLs for later retry

**Usage:**
```bash
python3 finding_ort.py
```

### 2. `finding_ort_parallel.py` - Enhanced Parallel Version
An optimized version with parallel processing and better error handling.

**Features:**
- All features from the basic version
- Parallel processing using ThreadPoolExecutor
- Thread-safe rate limiting
- Enhanced logging with timestamps
- Better error handling and reporting
- Performance tracking

**Usage:**
```bash
python3 finding_ort_parallel.py
```

## Input JSON Format

The scripts can handle various JSON structures:

### List Format:
```json
[
  {
    "company_name": "Ada Health",
    "url": "https://www.ada.com",
    "category": "Digital Health"
  }
]
```

### Dictionary Format:
```json
{
  "startups": [
    {
      "name": "Ada Health",
      "website": "https://www.ada.com"
    }
  ]
}
```

## Output Files

### 1. `finding_ort.json`
Complete results in JSON format:
```json
[
  {
    "company_name": "Ada Health",
    "url": "https://www.ada.com",
    "normalized_url": "ada.com",
    "ort": "Berlin",
    "source": "hardcoded"
  }
]
```

### 2. `finding_ort.csv`
Results in CSV format with columns:
- company_name
- url
- normalized_url
- ort (city)
- source (hardcoded/scraped)

### 3. `failed_ort_urls.json`
URLs that failed to return city information for later retry.

## Customization

### Adding Hardcoded Mappings
Edit the `url_to_ort` dictionary in either script:
```python
url_to_ort = {
    "https://www.example.com": "Berlin",
    # Add more mappings here
}
```

### Adding German Cities
Edit the `german_cities` set to include additional cities:
```python
german_cities = {
    "Berlin", "Hamburg", "München",
    # Add more cities here
}
```

### Modifying Search Pages
Edit the `pages_to_check` list in the `find_city_for_url` function:
```python
pages_to_check = [
    '',  # Homepage
    '/impressum',
    '/kontakt',
    # Add more pages here
]
```

## Performance Considerations

### Basic Version (`finding_ort.py`):
- Processes URLs sequentially
- 1 second delay between URLs
- 0.5 second delay between page checks
- Good for small datasets or when rate limiting is important

### Parallel Version (`finding_ort_parallel.py`):
- Processes URLs in parallel batches
- Configurable worker threads (default: 10)
- Thread-safe rate limiting (default: 2 requests/second)
- 3-5x faster for large datasets

## Error Handling

Both scripts handle common errors:
- 403 Forbidden: Site blocking automated access
- 404 Not Found: Page doesn't exist
- Timeouts: Site not responding
- Network errors: Connection issues

Failed URLs are saved to `failed_ort_urls.json` for manual review or retry.

## Dependencies

Install required packages:
```bash
pip install requests beautifulsoup4
```

## Troubleshooting

### Common Issues:

1. **403 Forbidden Errors**
   - Some sites block automated scrapers
   - Try adding more realistic headers
   - Consider using a proxy or VPN

2. **No City Found**
   - The city might not be on standard pages
   - Check if the city name is in the `german_cities` set
   - Manually inspect the website for city information

3. **Rate Limiting**
   - Adjust `max_per_second` in the parallel version
   - Increase delays in the basic version

## Future Improvements

- Add proxy support for better scraping success
- Implement retry logic with exponential backoff
- Add support for non-German cities
- Create a web interface for manual review
- Add machine learning for better city extraction
- Support for multiple languages