# Finding Ort (Location) Script

This Python script finds the location (Ort) for startup URLs by first checking a hardcoded mapping, then scraping web pages if needed.

## Features

- Uses a hardcoded mapping of URLs to German cities for known startups
- For unknown URLs, scrapes the website to find location information
- Tries multiple pages: main page, /impressum, /kontakt, /contact, /about-us, /ueber-uns
- Uses regex to extract city names from German postal code patterns (PLZ + Stadt)
- Matches against a comprehensive list of 500+ German cities
- Saves results in both JSON and CSV formats

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Prepare your input file `enhanced_products.json` with the following format:
```json
[
  {
    "company_name": "Company Name",
    "url": "https://www.example.com"
  }
]
```

2. Run the script:
```bash
python finding_ort.py
```

3. The script will generate two output files:
   - `finding_ort.json`: A mapping of URL to city (Ort)
   - `finding_ort.csv`: A CSV file with columns: company_name, url, ort

## Files

- `finding_ort.py`: Main script
- `enhanced_products.json`: Input file with startup data
- `german_cities.txt`: List of German cities for matching (500+ cities)
- `requirements.txt`: Python dependencies
- `finding_ort.json`: Output JSON mapping
- `finding_ort.csv`: Output CSV file

## How it Works

1. The script first loads a hardcoded mapping of 52 known URLs to their cities
2. For each startup in the input file:
   - If the URL is in the hardcoded mapping, it uses that city
   - Otherwise, it scrapes the website to find location information
3. Web scraping strategy:
   - Fetches the main page and looks for address information
   - If not found, tries common pages like /impressum, /kontakt, etc.
   - Looks for German postal code patterns (5 digits + city name)
   - Searches for city names in address tags and the entire page content
4. Results are saved in both JSON and CSV formats

## Notes

- The script includes a delay between requests to be polite to servers
- URLs are normalized (lowercase, trailing slash removed) for comparison
- If no location is found, the city is marked as "Unknown"
- The script uses a comprehensive list of German cities for accurate matching