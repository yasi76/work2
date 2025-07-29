#!/usr/bin/env python3
"""
Auto-detecting Ort-finding script that finds and uses the latest startups_products JSON file.
"""

import json
import csv
import requests
from bs4 import BeautifulSoup
import re
import time
from urllib.parse import urlparse, urljoin
from collections import defaultdict
import os
from datetime import datetime
import glob

# Hardcoded URL to city mappings
url_to_ort = {
    "https://www.ada.com": "Berlin",
    "https://www.amboss.com": "Berlin",
    "https://www.clue.com": "Berlin",
    "https://www.keleya.de": "Berlin",
    "https://www.mediteo.com": "Berlin",
    "https://www.nelly.com": "Berlin",
    "https://www.preventicus.com": "Berlin",
    "https://www.tinnitracks.com": "Hamburg",
    "https://www.vivy.com": "Berlin",
    "https://www.zanadio.de": "Hamburg",
    "https://www.caspar-health.com": "Berlin",
    "https://www.medikura.com": "Köln",
    "https://www.selfapy.de": "Berlin",
    "https://www.teleclinic.com": "München",
    "https://www.thryve.health": "Berlin",
    "https://www.kaia-health.com": "München",
    "https://www.mindable.health": "Berlin",
    "https://www.somnio.de": "Leipzig",
    "https://www.vitadock.com": "Berlin",
    "https://www.m-sense.de": "Berlin",
    "https://www.neolexon.de": "München",
    "https://www.novego.de": "Hamburg",
    "https://www.pink-gegen-brustkrebs.de": "Köln",
    "https://www.rehappy.de": "Duisburg",
    "https://www.velibra.de": "Berlin",
}

# Common German cities for validation
german_cities = {
    "Berlin", "Hamburg", "München", "Köln", "Frankfurt", "Stuttgart", "Düsseldorf",
    "Dortmund", "Essen", "Leipzig", "Bremen", "Dresden", "Hannover", "Nürnberg",
    "Duisburg", "Bochum", "Wuppertal", "Bielefeld", "Bonn", "Münster", "Karlsruhe",
    "Mannheim", "Augsburg", "Wiesbaden", "Aachen", "Mönchengladbach", "Gelsenkirchen",
    "Braunschweig", "Chemnitz", "Kiel", "Krefeld", "Halle", "Magdeburg", "Freiburg",
    "Oberhausen", "Lübeck", "Erfurt", "Mainz", "Rostock", "Kassel", "Hagen",
    "Hamm", "Saarbrücken", "Mülheim", "Potsdam", "Ludwigshafen", "Oldenburg",
    "Leverkusen", "Osnabrück", "Solingen", "Heidelberg", "Herne", "Neuss",
    "Darmstadt", "Paderborn", "Regensburg", "Ingolstadt", "Würzburg", "Fürth",
    "Wolfsburg", "Ulm", "Heilbronn", "Pforzheim", "Göttingen", "Bottrop",
    "Trier", "Recklinghausen", "Reutlingen", "Bremerhaven", "Koblenz", "Bergisch Gladbach",
    "Jena", "Remscheid", "Erlangen", "Moers", "Siegen", "Hildesheim", "Salzgitter"
}

def find_latest_startups_file():
    """Find the latest startups_products JSON file"""
    # Pattern to match startups_products files
    pattern = "startups_products_*.json"
    files = glob.glob(pattern)
    
    if not files:
        print("No startups_products_*.json files found")
        return None
    
    # Sort by modification time or by filename (which includes timestamp)
    files.sort(reverse=True)
    
    latest_file = files[0]
    print(f"Found latest startups file: {latest_file}")
    
    # Extract timestamp from filename if possible
    match = re.search(r'(\d{8}_\d{6})', latest_file)
    if match:
        timestamp = match.group(1)
        print(f"  Timestamp: {timestamp}")
    
    return latest_file

def normalize_url(url):
    """Normalize URL for consistent comparison"""
    if not url:
        return ""
    
    # Remove protocol and www
    url = url.lower().strip()
    url = re.sub(r'^https?://', '', url)
    url = re.sub(r'^www\.', '', url)
    
    # Remove trailing slash
    url = url.rstrip('/')
    
    return url

def extract_city_from_text(text, city_set):
    """Extract city name from text using the provided city set"""
    if not text:
        return None
    
    text = text.replace('\n', ' ').replace('\r', ' ')
    
    # Look for cities in the text
    for city in city_set:
        # Case-insensitive search with word boundaries
        pattern = r'\b' + re.escape(city) + r'\b'
        if re.search(pattern, text, re.IGNORECASE):
            return city
    
    # Try to find patterns like "PLZ City" (German postal code pattern)
    plz_pattern = r'\b(\d{5})\s+([A-Za-zäöüÄÖÜß\-]+(?:\s+[A-Za-zäöüÄÖÜß\-]+)*)\b'
    matches = re.findall(plz_pattern, text)
    for plz, potential_city in matches:
        # Check if the potential city is in our city set
        for city in city_set:
            if city.lower() == potential_city.lower():
                return city
    
    return None

def scrape_page(url, timeout=10):
    """Scrape a single page and return its text content"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=timeout, allow_redirects=True)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove script and style elements
        for script in soup(['script', 'style']):
            script.decompose()
        
        # Get text
        text = soup.get_text()
        
        # Also specifically look for address-related tags
        address_tags = soup.find_all(['address', 'div', 'p', 'span'], 
                                    class_=re.compile(r'address|contact|impressum|location', re.I))
        
        for tag in address_tags:
            text += ' ' + tag.get_text()
        
        return text
        
    except Exception as e:
        print(f"Error scraping {url}: {str(e)}")
        return None

def find_city_for_url(base_url, city_set):
    """Try to find city information for a URL by checking various pages"""
    # Pages to check for city information
    pages_to_check = [
        '',  # Homepage
        '/impressum',
        '/imprint',
        '/kontakt',
        '/contact',
        '/about',
        '/ueber-uns',
        '/about-us',
        '/datenschutz',
        '/privacy',
        '/legal',
        '/rechtliches'
    ]
    
    for page in pages_to_check:
        full_url = urljoin(base_url, page)
        print(f"  Checking: {full_url}")
        
        text = scrape_page(full_url)
        if text:
            city = extract_city_from_text(text, city_set)
            if city:
                print(f"  Found city: {city}")
                return city
        
        # Rate limiting
        time.sleep(0.5)
    
    return None

def load_urls_from_json_files():
    """Load all URLs from available JSON files"""
    all_urls = {}
    
    # First, try to find the latest startups_products file
    latest_file = find_latest_startups_file()
    
    # Build list of JSON files to check
    json_files = []
    
    if latest_file:
        json_files.append(latest_file)
    
    # Add other standard files
    json_files.extend([
        'startups_products_20250729_132707.json',  # Specific file mentioned
        'ultimate_startup_discovery_20250722_102338.json',
        'enhanced_fixed_products.json',
        'enhanced_products.json',
        'products.json',
        'startups.json',
        'companies.json'
    ])
    
    # Remove duplicates while preserving order
    seen = set()
    unique_files = []
    for f in json_files:
        if f not in seen:
            seen.add(f)
            unique_files.append(f)
    
    json_files = unique_files
    
    for json_file in json_files:
        if os.path.exists(json_file):
            print(f"\nLoading URLs from {json_file}...")
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    # Handle different JSON structures
                    if isinstance(data, list):
                        for item in data:
                            if isinstance(item, dict):
                                url = item.get('url') or item.get('website') or item.get('site_url')
                                name = item.get('company_name') or item.get('name') or item.get('startup_name')
                                if url and name:
                                    all_urls[url] = name
                    elif isinstance(data, dict):
                        # Could be a dict of URLs or a single object
                        if 'startups' in data:
                            for startup in data['startups']:
                                url = startup.get('url') or startup.get('website')
                                name = startup.get('company_name') or startup.get('name')
                                if url and name:
                                    all_urls[url] = name
                        else:
                            # Try to extract from dict directly
                            for key, value in data.items():
                                if isinstance(value, dict):
                                    url = value.get('url') or value.get('website')
                                    name = value.get('company_name') or value.get('name') or key
                                    if url:
                                        all_urls[url] = name
                                elif isinstance(value, str) and value.startswith('http'):
                                    # Simple key-value mapping
                                    all_urls[value] = key
                                        
                print(f"  Loaded {len(all_urls)} unique URLs so far")
                        
            except Exception as e:
                print(f"  Error loading {json_file}: {str(e)}")
        else:
            if json_file != latest_file:  # Don't warn about auto-detected file
                print(f"  File not found: {json_file}")
    
    return all_urls

def main():
    """Main function to find and save city information for all URLs"""
    print("Starting Ort (city) finding process (Auto-detecting version)...")
    print(f"Timestamp: {datetime.now().strftime('%Y%m%d_%H%M%S')}")
    
    # Load all URLs from JSON files
    print("\n1. Loading URLs from JSON files...")
    url_to_company = load_urls_from_json_files()
    
    if not url_to_company:
        print("No URLs found in JSON files. Creating sample data...")
        # Add some sample URLs if no files found
        url_to_company = {
            "https://www.ada.com": "Ada Health",
            "https://www.kaia-health.com": "Kaia Health",
            "https://www.teleclinic.com": "TeleClinic"
        }
    
    print(f"\nTotal unique URLs to process: {len(url_to_company)}")
    
    # Results storage
    results = []
    city_distribution = defaultdict(int)
    
    # Process each URL
    print("\n2. Processing URLs...")
    for i, (url, company_name) in enumerate(url_to_company.items(), 1):
        print(f"\n[{i}/{len(url_to_company)}] Processing {company_name}: {url}")
        
        normalized_url = normalize_url(url)
        
        # Check if we have a hardcoded mapping
        ort = None
        for hardcoded_url, hardcoded_ort in url_to_ort.items():
            if normalize_url(hardcoded_url) == normalized_url:
                ort = hardcoded_ort
                print(f"  Found hardcoded mapping: {ort}")
                break
        
        # If not found in hardcoded mappings, try to scrape
        if not ort:
            print(f"  No hardcoded mapping, attempting to scrape...")
            ort = find_city_for_url(url, german_cities)
            
            if ort:
                print(f"  Successfully scraped city: {ort}")
            else:
                print(f"  Could not find city information")
                ort = "Unknown"
        
        # Store result
        result = {
            "company_name": company_name,
            "url": url,
            "normalized_url": normalized_url,
            "ort": ort,
            "source": "hardcoded" if ort in url_to_ort.values() else "scraped"
        }
        results.append(result)
        city_distribution[ort] += 1
        
        # Rate limiting between URLs
        if i < len(url_to_company):
            time.sleep(1)
    
    # Save results to JSON
    print("\n3. Saving results...")
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    json_output_file = f'finding_ort_{timestamp}.json'
    with open(json_output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"  Saved JSON results to {json_output_file}")
    
    # Also save to standard filename for compatibility
    with open('finding_ort.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"  Saved JSON results to finding_ort.json")
    
    # Save results to CSV
    csv_output_file = f'finding_ort_{timestamp}.csv'
    with open(csv_output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['company_name', 'url', 'normalized_url', 'ort', 'source'])
        writer.writeheader()
        writer.writerows(results)
    print(f"  Saved CSV results to {csv_output_file}")
    
    # Also save to standard filename
    with open('finding_ort.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['company_name', 'url', 'normalized_url', 'ort', 'source'])
        writer.writeheader()
        writer.writerows(results)
    print(f"  Saved CSV results to finding_ort.csv")
    
    # Print summary statistics
    print("\n4. Summary Statistics:")
    print(f"  Total URLs processed: {len(results)}")
    print(f"  Cities found: {sum(1 for r in results if r['ort'] != 'Unknown')}")
    print(f"  Unknown locations: {sum(1 for r in results if r['ort'] == 'Unknown')}")
    
    print("\n  City Distribution:")
    for city, count in sorted(city_distribution.items(), key=lambda x: x[1], reverse=True):
        print(f"    {city}: {count}")
    
    # Save failed URLs for retry
    failed_urls = [r for r in results if r['ort'] == 'Unknown']
    if failed_urls:
        failed_file = f'failed_ort_urls_{timestamp}.json'
        with open(failed_file, 'w', encoding='utf-8') as f:
            json.dump(failed_urls, f, ensure_ascii=False, indent=2)
        print(f"\n  Saved {len(failed_urls)} failed URLs to {failed_file} for later retry")
        
        # Also save to standard filename
        with open('failed_ort_urls.json', 'w', encoding='utf-8') as f:
            json.dump(failed_urls, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()