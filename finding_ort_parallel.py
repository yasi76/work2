#!/usr/bin/env python3
"""
Enhanced parallel version of the Ort-finding script.
Features parallel processing, better error handling, and retry logic.
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
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from typing import Dict, List, Tuple, Optional
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Thread-safe rate limiter
class RateLimiter:
    def __init__(self, max_per_second=2):
        self.max_per_second = max_per_second
        self.min_interval = 1.0 / max_per_second
        self.last_call = 0
        self.lock = threading.Lock()
    
    def wait_if_needed(self):
        with self.lock:
            current_time = time.time()
            time_since_last = current_time - self.last_call
            if time_since_last < self.min_interval:
                time.sleep(self.min_interval - time_since_last)
            self.last_call = time.time()

# Global rate limiter
rate_limiter = RateLimiter(max_per_second=2)

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

def normalize_url(url: str) -> str:
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

def extract_city_from_text(text: str, city_set: set) -> Optional[str]:
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

def scrape_page(url: str, timeout: int = 10) -> Optional[str]:
    """Scrape a single page and return its text content"""
    rate_limiter.wait_if_needed()
    
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
        
    except requests.exceptions.Timeout:
        logger.warning(f"Timeout scraping {url}")
        return None
    except requests.exceptions.RequestException as e:
        logger.warning(f"Request error scraping {url}: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error scraping {url}: {str(e)}")
        return None

def find_city_for_url(base_url: str, city_set: set) -> Optional[str]:
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
        logger.debug(f"Checking: {full_url}")
        
        text = scrape_page(full_url)
        if text:
            city = extract_city_from_text(text, city_set)
            if city:
                logger.info(f"Found city {city} at {full_url}")
                return city
    
    return None

def process_url_batch(url_batch: List[Tuple[str, str]], city_set: set) -> List[Dict]:
    """Process a batch of URLs and return results"""
    results = []
    
    for url, company_name in url_batch:
        normalized_url = normalize_url(url)
        
        # Check if we have a hardcoded mapping
        ort = None
        for hardcoded_url, hardcoded_ort in url_to_ort.items():
            if normalize_url(hardcoded_url) == normalized_url:
                ort = hardcoded_ort
                logger.info(f"Found hardcoded mapping for {company_name}: {ort}")
                break
        
        # If not found in hardcoded mappings, try to scrape
        if not ort:
            logger.info(f"Scraping city for {company_name} ({url})")
            ort = find_city_for_url(url, city_set)
            
            if ort:
                logger.info(f"Successfully scraped city for {company_name}: {ort}")
            else:
                logger.warning(f"Could not find city for {company_name}")
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
    
    return results

def load_urls_from_json_files() -> Dict[str, str]:
    """Load all URLs from available JSON files"""
    all_urls = {}
    
    # List of JSON files to check
    json_files = [
        'ultimate_startup_discovery_20250722_102338.json',
        'enhanced_fixed_products.json',
        'enhanced_products.json',
        'products.json',
        'startups.json',
        'companies.json'
    ]
    
    for json_file in json_files:
        if os.path.exists(json_file):
            logger.info(f"Loading URLs from {json_file}...")
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
                                        
                logger.info(f"Loaded {len(all_urls)} unique URLs so far")
                        
            except Exception as e:
                logger.error(f"Error loading {json_file}: {str(e)}")
        else:
            logger.debug(f"File not found: {json_file}")
    
    return all_urls

def main():
    """Main function to find and save city information for all URLs"""
    start_time = time.time()
    
    logger.info("Starting Ort (city) finding process...")
    logger.info(f"Timestamp: {datetime.now().strftime('%Y%m%d_%H%M%S')}")
    
    # Load all URLs from JSON files
    logger.info("Loading URLs from JSON files...")
    url_to_company = load_urls_from_json_files()
    
    if not url_to_company:
        logger.warning("No URLs found in JSON files. Creating sample data...")
        # Add some sample URLs if no files found
        url_to_company = {
            "https://www.ada.com": "Ada Health",
            "https://www.kaia-health.com": "Kaia Health",
            "https://www.teleclinic.com": "TeleClinic",
            "https://www.doctolib.de": "Doctolib",
            "https://www.jameda.de": "Jameda"
        }
    
    logger.info(f"Total unique URLs to process: {len(url_to_company)}")
    
    # Convert to list for batch processing
    url_list = list(url_to_company.items())
    
    # Process URLs in parallel
    results = []
    batch_size = 5
    max_workers = 10
    
    logger.info(f"Processing URLs with {max_workers} parallel workers...")
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit tasks in batches
        futures = []
        for i in range(0, len(url_list), batch_size):
            batch = url_list[i:i+batch_size]
            future = executor.submit(process_url_batch, batch, german_cities)
            futures.append(future)
        
        # Collect results with progress tracking
        completed = 0
        for future in as_completed(futures):
            try:
                batch_results = future.result()
                results.extend(batch_results)
                completed += len(batch_results)
                logger.info(f"Progress: {completed}/{len(url_list)} URLs processed")
            except Exception as e:
                logger.error(f"Error processing batch: {str(e)}")
    
    # Calculate statistics
    city_distribution = defaultdict(int)
    for result in results:
        city_distribution[result['ort']] += 1
    
    # Save results to JSON
    logger.info("Saving results...")
    json_output_file = 'finding_ort.json'
    with open(json_output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    logger.info(f"Saved JSON results to {json_output_file}")
    
    # Save results to CSV
    csv_output_file = 'finding_ort.csv'
    with open(csv_output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['company_name', 'url', 'normalized_url', 'ort', 'source'])
        writer.writeheader()
        writer.writerows(results)
    logger.info(f"Saved CSV results to {csv_output_file}")
    
    # Print summary statistics
    logger.info("Summary Statistics:")
    logger.info(f"  Total URLs processed: {len(results)}")
    logger.info(f"  Cities found: {sum(1 for r in results if r['ort'] != 'Unknown')}")
    logger.info(f"  Unknown locations: {sum(1 for r in results if r['ort'] == 'Unknown')}")
    
    logger.info("City Distribution:")
    for city, count in sorted(city_distribution.items(), key=lambda x: x[1], reverse=True)[:10]:
        logger.info(f"  {city}: {count}")
    
    # Save failed URLs for retry
    failed_urls = [r for r in results if r['ort'] == 'Unknown']
    if failed_urls:
        failed_file = 'failed_ort_urls.json'
        with open(failed_file, 'w', encoding='utf-8') as f:
            json.dump(failed_urls, f, ensure_ascii=False, indent=2)
        logger.info(f"Saved {len(failed_urls)} failed URLs to {failed_file} for later retry")
    
    # Execution time
    elapsed_time = time.time() - start_time
    logger.info(f"Total execution time: {elapsed_time:.2f} seconds")

if __name__ == "__main__":
    main()