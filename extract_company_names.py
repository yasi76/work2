#!/usr/bin/env python3
"""
Enhanced Company Name Extractor for Digital Health Startups
Reads the output from evaluate_health_startups.py and extracts/updates company names
Features: NLP extraction, advanced metadata parsing, domain mapping, metrics tracking
"""

import json
import csv
import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urlparse
import logging
from typing import Dict, List, Optional, Tuple
import argparse
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import Counter
import os

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

# Try to import optional dependencies
try:
    import spacy
    nlp = spacy.load("en_core_web_sm")
    HAS_SPACY = True
except:
    HAS_SPACY = False
    logger.info("spaCy not available. Install with: pip install spacy && python -m spacy download en_core_web_sm")

try:
    from playwright.sync_api import sync_playwright
    HAS_PLAYWRIGHT = True
except:
    HAS_PLAYWRIGHT = False
    logger.info("Playwright not available. Install with: pip install playwright && playwright install")


class CompanyNameExtractor:
    def __init__(self, timeout: int = 10, use_js: bool = False):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        self.use_js = use_js and HAS_PLAYWRIGHT
        self.domain_name_map = self._load_domain_mappings()
        self.extraction_stats = Counter()
        
    def _load_domain_mappings(self) -> Dict[str, str]:
        """Load domain to company name mappings from config file"""
        mapping_file = 'domain_name_map.json'
        if os.path.exists(mapping_file):
            try:
                with open(mapping_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                logger.warning(f"Could not load {mapping_file}")
        
        # Default mappings for known tricky domains
        return {
            'getnutrio.com': 'Nutrio',
            'shop.getnutrio.com': 'Nutrio',
            'visioncheckout.com': 'Vision Checkout',
            'de.becureglobal.com': 'BeCure Global',
            'telemed24online.de': 'TeleMed24 Online',
            # Add more as discovered
        }
    
    def is_valid_url_entry(self, entry: any) -> bool:
        """Validate that the entry has the required URL field"""
        return isinstance(entry, dict) and 'url' in entry and isinstance(entry['url'], str)
    
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
            self.extraction_stats['existing_data'] += 1
            return startup_data
        
        try:
            logger.info(f"Fetching {url} for name extraction")
            
            if self.use_js:
                # Use Playwright for JS-heavy sites
                html_content = self._fetch_with_playwright(url)
                soup = BeautifulSoup(html_content, 'html.parser')
            else:
                # Use regular requests
                response = self.session.get(url, timeout=self.timeout, allow_redirects=True)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                else:
                    raise Exception(f"HTTP {response.status_code}")
            
            name, method = self._extract_company_name_with_method(soup, startup_data.get('page_title', ''), url, startup_data)
            startup_data['company_name'] = name
            startup_data['name_extraction_method'] = method
            self.extraction_stats[method] += 1
                
        except Exception as e:
            logger.warning(f"Error fetching {url}: {str(e)}")
            startup_data['company_name'] = self.extract_name_from_validated_data(startup_data)
            startup_data['name_extraction_method'] = 'error_fallback'
            self.extraction_stats['error_fallback'] += 1
        
        return startup_data
    
    def _fetch_with_playwright(self, url: str) -> str:
        """Fetch page content using Playwright for JS rendering"""
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.set_viewport_size({"width": 1920, "height": 1080})
            
            try:
                page.goto(url, wait_until='networkidle', timeout=self.timeout * 1000)
                # Wait a bit for dynamic content
                page.wait_for_timeout(2000)
                content = page.content()
            finally:
                browser.close()
                
        return content
    
    def _extract_company_name_with_method(self, soup: BeautifulSoup, title: str, url: str, startup_data: Dict) -> Tuple[str, str]:
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
        
        # Strategy 6: Look for schema.org organization data (enhanced)
        schema_scripts = soup.find_all('script', type='application/ld+json')
        for schema_script in schema_scripts:
            try:
                schema_data = json.loads(schema_script.string)
                
                # Handle direct Organization type
                if isinstance(schema_data, dict):
                    if schema_data.get('@type') == 'Organization' and schema_data.get('name'):
                        return schema_data['name'], 'schema.org'
                    
                    # Handle @graph structure
                    if '@graph' in schema_data:
                        for entity in schema_data['@graph']:
                            if isinstance(entity, dict) and entity.get('@type') == 'Organization' and entity.get('name'):
                                return entity['name'], 'schema.org_graph'
                
                # Handle array of entities
                elif isinstance(schema_data, list):
                    for entity in schema_data:
                        if isinstance(entity, dict) and entity.get('@type') == 'Organization' and entity.get('name'):
                            return entity['name'], 'schema.org_array'
            except:
                pass
        
        # Strategy 7: Use spaCy NLP if available
        if HAS_SPACY:
            # Try to extract from title using NLP
            if title:
                org_name = self._extract_org_with_spacy(title)
                if org_name:
                    return org_name, 'spacy_org'
            
            # Try first heading
            h1 = soup.find('h1')
            if h1 and h1.text:
                org_name = self._extract_org_with_spacy(h1.text.strip())
                if org_name:
                    return org_name, 'spacy_h1'
        
        # Strategy 8: Look for specific patterns in content
        # Check for "About Us" sections
        about_patterns = ['about us', 'über uns', 'qui sommes-nous', 'about']
        for pattern in about_patterns:
            about_elem = soup.find(text=re.compile(pattern, re.IGNORECASE))
            if about_elem:
                parent = about_elem.parent
                if parent:
                    text = parent.get_text(strip=True)
                    if HAS_SPACY:
                        org_name = self._extract_org_with_spacy(text[:500])  # First 500 chars
                        if org_name:
                            return org_name, 'spacy_about'
        
        # Strategy 9: Extract from URL domain with mapping
        name = self._extract_from_url(url)
        return name, 'url_domain'
    
    def _extract_org_with_spacy(self, text: str) -> Optional[str]:
        """Use spaCy NLP to extract organization names"""
        if not HAS_SPACY or not text:
            return None
            
        doc = nlp(text)
        for ent in doc.ents:
            if ent.label_ == "ORG":
                # Clean up the organization name
                org_name = ent.text.strip()
                # Remove common suffixes
                org_name = re.sub(r'\s+(GmbH|AG|Ltd|Inc|LLC|Corp)\.?\s*$', '', org_name, flags=re.IGNORECASE)
                if org_name and len(org_name) > 2:
                    return org_name
        return None
    
    def _clean_title_to_name(self, title: str) -> str:
        """Enhanced title cleaning with NLP-aware patterns"""
        if not title:
            return "Unknown"
        
        # Common patterns to clean from titles
        clean_patterns = [
            # Remove common page indicators
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
            # Remove common marketing phrases
            r'(?i)\s*[-–—]\s*Transform(ing)?\s+Healthcare.*$',
            r'(?i)\s*[-–—]\s*Digital\s+Health\s+Solutions?.*$',
            r'(?i)\s*[-–—]\s*The\s+Future\s+of.*$',
            r'(?i)\s*[-–—]\s*Your\s+Partner\s+in.*$',
        ]
        
        cleaned_title = title.strip()
        
        # Apply cleaning patterns
        for pattern in clean_patterns:
            cleaned_title = re.sub(pattern, '', cleaned_title, flags=re.IGNORECASE).strip()
        
        # Additional cleaning for common suffixes
        suffixes_to_remove = [
            'GmbH', 'AG', 'SE', 'Ltd', 'Limited', 'Inc', 'LLC', 'Corp', 'Corporation',
            'B.V.', 'N.V.', 'S.A.', 'S.L.', 'AB', 'AS', 'A/S', 'KG', 'OHG', 'e.V.',
            'UG', 'haftungsbeschränkt'
        ]
        
        for suffix in suffixes_to_remove:
            pattern = r'\s+' + re.escape(suffix) + r'\s*\.?\s*$'
            cleaned_title = re.sub(pattern, '', cleaned_title, flags=re.IGNORECASE).strip()
        
        # Check if we still have a reasonable name
        if cleaned_title and len(cleaned_title) > 2 and len(cleaned_title) < 50:
            return cleaned_title
        
        return "Unknown"
    
    def _extract_from_url(self, url: str) -> str:
        """Enhanced URL extraction with domain mapping"""
        if not url:
            return "Unknown"
        
        parsed_url = urlparse(url)
        domain = parsed_url.netloc.lower()
        
        # Check domain mapping first
        if domain in self.domain_name_map:
            return self.domain_name_map[domain]
        
        # Remove common prefixes
        domain = re.sub(r'^(www\.|app\.|portal\.|my\.|shop\.)', '', domain)
        
        # Check cleaned domain in mapping
        if domain in self.domain_name_map:
            return self.domain_name_map[domain]
        
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
            
            # Handle camelCase domains (e.g., "teleMed24online" -> "TeleMed24 Online")
            camel_case_pattern = r'([a-z])([A-Z])'
            if re.search(camel_case_pattern, name):
                name = re.sub(camel_case_pattern, r'\1 \2', name)
                # Also handle numbers
                name = re.sub(r'([a-zA-Z])(\d)', r'\1 \2', name)
                name = re.sub(r'(\d)([a-zA-Z])', r'\1 \2', name)
                # Capitalize each word
                return ' '.join(word.capitalize() for word in name.split())
            
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
    
    def get_extraction_stats(self) -> Dict[str, int]:
        """Return extraction statistics"""
        return dict(self.extraction_stats)


def save_domain_mappings(mappings: Dict[str, str], filepath: str = 'domain_name_map.json'):
    """Save domain mappings to file"""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(mappings, f, indent=2, ensure_ascii=False)
    logger.info(f"Saved domain mappings to {filepath}")


def process_validated_file(input_file: str, output_prefix: str, refetch: bool = False, 
                          max_workers: int = 10, use_js: bool = False):
    """Process a validated JSON file and extract company names"""
    
    # Load the validated data
    logger.info(f"Loading validated data from {input_file}")
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Handle different input formats
    if isinstance(data, dict):
        # Handle wrapped format with 'urls' key
        if 'urls' in data:
            startups = data['urls']
        else:
            # Handle summary file format
            startups = []
            for key, value in data.items():
                if isinstance(value, dict) and 'url' in value:
                    startups.append(value)
                elif isinstance(value, str) and (key.startswith('http') or '.' in key):
                    startups.append({'url': key})
    elif isinstance(data, list):
        startups = data
    else:
        raise ValueError("Unsupported JSON structure")
    
    # Convert string items to dictionaries if needed
    processed_startups = []
    extractor = CompanyNameExtractor(use_js=use_js)
    
    for item in startups:
        if isinstance(item, str):
            processed_startups.append({'url': item})
        elif extractor.is_valid_url_entry(item):
            processed_startups.append(item)
        else:
            logger.warning(f"Skipping invalid item: {item}")
    
    startups = processed_startups
    logger.info(f"Processing {len(startups)} valid startup entries")
    
    if refetch:
        # Process with parallel fetching
        logger.info(f"Refetching pages to extract company names (JS rendering: {use_js})...")
        
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
            extractor.extraction_stats['existing_data'] += 1
    
    # Get extraction statistics
    stats = extractor.get_extraction_stats()
    
    # Log summary with more detail
    logger.info("\n" + "="*50)
    logger.info("EXTRACTION SUMMARY")
    logger.info("="*50)
    logger.info(f"Total startups processed: {len(startups)}")
    logger.info("\nExtraction method breakdown:")
    for method, count in sorted(stats.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / len(startups)) * 100 if startups else 0
        logger.info(f"  {method}: {count} ({percentage:.1f}%)")
    
    # Count successful extractions
    successful = sum(1 for s in startups if s.get('company_name') and s['company_name'] != 'Unknown')
    logger.info(f"\nSuccessful name extractions: {successful}/{len(startups)} ({(successful/len(startups)*100):.1f}%)")
    
    # Save results
    output_json = f"{output_prefix}_with_names.json"
    output_csv = f"{output_prefix}_with_names.csv"
    
    # Save JSON
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(startups, f, indent=2, ensure_ascii=False)
    logger.info(f"\nSaved JSON with names to {output_json}")
    
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
    
    # Save extraction statistics
    stats_file = f"{output_prefix}_extraction_stats.json"
    with open(stats_file, 'w', encoding='utf-8') as f:
        json.dump({
            'total_processed': len(startups),
            'successful_extractions': successful,
            'extraction_methods': stats,
            'success_rate': f"{(successful/len(startups)*100):.1f}%" if startups else "0%"
        }, f, indent=2)
    logger.info(f"Saved extraction statistics to {stats_file}")


def main():
    parser = argparse.ArgumentParser(description='Extract company names from validated startup URLs')
    parser.add_argument('input_file', help='Validated JSON file from evaluate_health_startups.py')
    parser.add_argument('--output-prefix', default='startups', help='Output file prefix')
    parser.add_argument('--refetch', action='store_true', help='Refetch URLs to extract names (slower but more accurate)')
    parser.add_argument('--max-workers', type=int, default=10, help='Maximum parallel workers for refetching')
    parser.add_argument('--js', action='store_true', help='Use headless browser for JavaScript-heavy sites (requires playwright)')
    parser.add_argument('--update-domain-map', type=str, help='Update domain mappings from JSON file')
    
    args = parser.parse_args()
    
    # Update domain mappings if requested
    if args.update_domain_map:
        try:
            with open(args.update_domain_map, 'r', encoding='utf-8') as f:
                new_mappings = json.load(f)
            save_domain_mappings(new_mappings)
            logger.info(f"Updated domain mappings from {args.update_domain_map}")
        except Exception as e:
            logger.error(f"Failed to update domain mappings: {e}")
            return
    
    process_validated_file(args.input_file, args.output_prefix, args.refetch, args.max_workers, args.js)


if __name__ == "__main__":
    main()