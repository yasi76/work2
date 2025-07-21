#!/usr/bin/env python3
"""
Extract company names from validated startup URLs
Reads the output from evaluate_health_startups.py and extracts/updates company names
"""

import json
import csv
import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urlparse
import logging
from typing import Dict, List, Optional
import argparse
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# User agent
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}


class CompanyNameExtractor:
    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
    
    def extract_name_from_validated_data(self, startup_data: Dict) -> str:
        """Extract company name from already validated data"""
        
        # First check if we already have a good company name
        if startup_data.get('company_name') and startup_data['company_name'] != 'Unknown':
            return startup_data['company_name']
        
        # If the site is not live, try to extract from URL
        if not startup_data.get('is_live', False):
            url = startup_data.get('final_url') or startup_data.get('url', '')
            return self._extract_from_url(url)
        
        # Try to extract from existing metadata
        title = startup_data.get('page_title', '')
        url = startup_data.get('final_url') or startup_data.get('url', '')
        
        # Clean the title
        if title:
            cleaned_name = self._clean_title_to_name(title)
            if cleaned_name and cleaned_name != 'Unknown':
                return cleaned_name
        
        # Fall back to URL extraction
        return self._extract_from_url(url)
    
    def fetch_and_extract_name(self, startup_data: Dict) -> Dict:
        """Fetch the page again and extract company name with all strategies"""
        url = startup_data.get('final_url') or startup_data.get('url', '')
        
        if not url or not startup_data.get('is_live', False):
            # Can't fetch, use existing data
            startup_data['company_name'] = self.extract_name_from_validated_data(startup_data)
            startup_data['name_extraction_method'] = 'existing_data'
            return startup_data
        
        try:
            logger.info(f"Fetching {url} for name extraction")
            response = self.session.get(url, timeout=self.timeout, allow_redirects=True)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                name, method = self._extract_company_name_with_method(soup, startup_data.get('page_title', ''), url, startup_data)
                startup_data['company_name'] = name
                startup_data['name_extraction_method'] = method
            else:
                startup_data['company_name'] = self.extract_name_from_validated_data(startup_data)
                startup_data['name_extraction_method'] = 'existing_data_fallback'
                
        except Exception as e:
            logger.warning(f"Error fetching {url}: {str(e)}")
            startup_data['company_name'] = self.extract_name_from_validated_data(startup_data)
            startup_data['name_extraction_method'] = 'error_fallback'
        
        return startup_data
    
    def _extract_company_name_with_method(self, soup: BeautifulSoup, title: str, url: str, startup_data: Dict) -> tuple[str, str]:
        """Extract company name and return the method used"""
        
        # Strategy 1: Check if name already exists in startup_data
        if 'name' in startup_data and startup_data['name']:
            name = startup_data['name'].strip()
            if name and name.lower() not in ['healthcare company', 'unknown', 'n/a', '']:
                return name, 'existing_field'
        
        # Strategy 2: Try OpenGraph site_name
        og_site_name = soup.find('meta', attrs={'property': 'og:site_name'})
        if og_site_name and og_site_name.get('content'):
            name = og_site_name['content'].strip()
            if name:
                return name, 'og:site_name'
        
        # Strategy 3: Try application-name meta tag
        app_name = soup.find('meta', attrs={'name': 'application-name'})
        if app_name and app_name.get('content'):
            name = app_name['content'].strip()
            if name:
                return name, 'application-name'
        
        # Strategy 4: Try og:title as well
        og_title = soup.find('meta', attrs={'property': 'og:title'})
        if og_title and og_title.get('content'):
            cleaned = self._clean_title_to_name(og_title['content'])
            if cleaned and cleaned != 'Unknown':
                return cleaned, 'og:title'
        
        # Strategy 5: Clean the title tag
        if title:
            cleaned = self._clean_title_to_name(title)
            if cleaned and cleaned != 'Unknown':
                return cleaned, 'title_tag'
        
        # Strategy 6: Look for schema.org organization data
        schema_script = soup.find('script', type='application/ld+json')
        if schema_script:
            try:
                schema_data = json.loads(schema_script.string)
                if isinstance(schema_data, dict):
                    if schema_data.get('@type') == 'Organization' and schema_data.get('name'):
                        return schema_data['name'], 'schema.org'
            except:
                pass
        
        # Strategy 7: Extract from URL domain as last resort
        name = self._extract_from_url(url)
        return name, 'url_domain'
    
    def _clean_title_to_name(self, title: str) -> str:
        """Clean a title string to extract company name"""
        if not title:
            return "Unknown"
        
        # Common patterns to clean from titles
        clean_patterns = [
            r'\s*[-–—|•]\s*Home\s*$',
            r'\s*[-–—|•]\s*Welcome\s*$',
            r'\s*[-–—|•]\s*Official\s*(Website|Site)\s*$',
            r'\s*[-–—|•]\s*Homepage\s*$',
            r'\s*[-–—|•]\s*Start\s*$',
            r'\s*[-–—|•]\s*Startseite\s*$',  # German
            r'\s*[-–—|•]\s*Accueil\s*$',     # French
            r'^Welcome to\s*',
            r'^Willkommen bei\s*',            # German
            r'\s*\|.*$',  # Remove everything after pipe
            r'\s*[-–—](?!.*[-–—]).*$',  # Remove everything after last dash (but keep compound names)
            r'\s*[•·].*$',  # Remove everything after bullet
        ]
        
        cleaned_title = title.strip()
        
        # Apply cleaning patterns
        for pattern in clean_patterns:
            cleaned_title = re.sub(pattern, '', cleaned_title, flags=re.IGNORECASE).strip()
        
        # Additional cleaning for common suffixes
        suffixes_to_remove = [
            'GmbH', 'AG', 'SE', 'Ltd', 'Limited', 'Inc', 'LLC', 'Corp', 'Corporation',
            'B.V.', 'N.V.', 'S.A.', 'S.L.', 'AB', 'AS', 'A/S'
        ]
        
        for suffix in suffixes_to_remove:
            pattern = r'\s+' + re.escape(suffix) + r'\s*\.?\s*$'
            cleaned_title = re.sub(pattern, '', cleaned_title, flags=re.IGNORECASE).strip()
        
        # Check if we still have a reasonable name
        if cleaned_title and len(cleaned_title) > 2 and len(cleaned_title) < 50:
            return cleaned_title
        
        return "Unknown"
    
    def _extract_from_url(self, url: str) -> str:
        """Extract company name from URL as fallback"""
        if not url:
            return "Unknown"
        
        parsed_url = urlparse(url)
        domain = parsed_url.netloc.lower()
        
        # Remove common prefixes
        domain = re.sub(r'^(www\.|app\.|portal\.|my\.)', '', domain)
        
        # Get the main part before TLD
        domain_parts = domain.split('.')
        if domain_parts:
            name = domain_parts[0]
            
            # Handle hyphenated domains
            if '-' in name:
                # Convert "my-health-app" to "My Health App"
                parts = name.split('-')
                name = ' '.join(part.capitalize() for part in parts)
                return name
            
            # Capitalize properly
            if name and len(name) > 1:
                # Handle special cases like "ada" -> "ADA" (if all lowercase and short)
                if len(name) <= 3:
                    return name.upper()
                else:
                    # Try to detect camelCase or similar
                    if name.islower():
                        return name[0].upper() + name[1:]
                    else:
                        # Preserve existing capitalization
                        return name
        
        return "Unknown"


def process_validated_file(input_file: str, output_prefix: str, refetch: bool = False, max_workers: int = 10):
    """Process a validated JSON file and extract company names"""
    
    # Load the validated data
    logger.info(f"Loading validated data from {input_file}")
    with open(input_file, 'r', encoding='utf-8') as f:
        startups = json.load(f)
    
    logger.info(f"Processing {len(startups)} startups")
    
    extractor = CompanyNameExtractor()
    
    if refetch:
        # Process with parallel fetching
        logger.info("Refetching pages to extract company names...")
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_startup = {
                executor.submit(extractor.fetch_and_extract_name, startup): i 
                for i, startup in enumerate(startups)
            }
            
            for future in as_completed(future_to_startup):
                idx = future_to_startup[future]
                try:
                    startups[idx] = future.result()
                except Exception as e:
                    logger.error(f"Error processing startup: {str(e)}")
    else:
        # Just extract from existing data
        logger.info("Extracting names from existing data...")
        for startup in startups:
            startup['company_name'] = extractor.extract_name_from_validated_data(startup)
            startup['name_extraction_method'] = 'existing_data'
    
    # Count extraction methods
    method_counts = {}
    for startup in startups:
        method = startup.get('name_extraction_method', 'unknown')
        method_counts[method] = method_counts.get(method, 0) + 1
    
    # Log summary
    logger.info("\nExtraction method summary:")
    for method, count in sorted(method_counts.items(), key=lambda x: x[1], reverse=True):
        logger.info(f"  {method}: {count}")
    
    # Save results
    output_json = f"{output_prefix}_with_names.json"
    output_csv = f"{output_prefix}_with_names.csv"
    
    # Save JSON
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(startups, f, indent=2, ensure_ascii=False)
    logger.info(f"Saved JSON with names to {output_json}")
    
    # Save CSV
    if startups:
        # Prepare for CSV (flatten matched_keywords if it's a list)
        for startup in startups:
            if isinstance(startup.get('matched_keywords'), list):
                startup['matched_keywords'] = ', '.join(startup['matched_keywords'])
        
        keys = startups[0].keys()
        with open(output_csv, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(startups)
        logger.info(f"Saved CSV with names to {output_csv}")
    
    # Create a simple names list
    names_file = f"{output_prefix}_company_names.txt"
    with open(names_file, 'w', encoding='utf-8') as f:
        for startup in startups:
            if startup.get('is_live') and startup.get('is_health_related'):
                name = startup.get('company_name', 'Unknown')
                url = startup.get('final_url') or startup.get('url', '')
                f.write(f"{name}\t{url}\n")
    logger.info(f"Saved company names list to {names_file}")


def main():
    parser = argparse.ArgumentParser(description='Extract company names from validated startup URLs')
    parser.add_argument('input_file', help='Validated JSON file from evaluate_health_startups.py')
    parser.add_argument('--output-prefix', default='startups', help='Output file prefix')
    parser.add_argument('--refetch', action='store_true', help='Refetch URLs to extract names (slower but more accurate)')
    parser.add_argument('--max-workers', type=int, default=10, help='Maximum parallel workers for refetching')
    
    args = parser.parse_args()
    
    process_validated_file(args.input_file, args.output_prefix, args.refetch, args.max_workers)


if __name__ == "__main__":
    main()