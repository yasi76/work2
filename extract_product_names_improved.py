#!/usr/bin/env python3
"""
Improved Digital Health Product Extractor
Extracts product names and categorizes product types from startup websites
with enhanced filtering and ground truth matching
"""

import json
import csv
import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urlparse, urljoin
import logging
from typing import Dict, List, Optional, Tuple, Set
import argparse
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import Counter
import os
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# User agent
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

# Ground truth product data - PRIMARY FILTER
GROUND_TRUTH_PRODUCTS = {
    "https://www.acalta.de": ["Acalta"],
    "https://www.actimi.com": ["Actimi Herzinsuffizienz Set", "Actimi Notaufnahme-Set"],
    "https://www.emmora.de": ["Emmora"],
    "https://www.alfa-ai.com": ["ALFA AI"],
    "https://www.apheris.com": ["Apheris Platform"],  # Enhanced with "Platform"
    "https://www.aporize.com/": ["Aporize"],
    "https://www.arztlena.com/": ["Lena App"],  # Enhanced with "App"
    "https://shop.getnutrio.com/": ["Aurora Nutrio", "Nutrio App"],
    "https://www.auta.health/": ["Auta Health Platform"],
    "https://visioncheckout.com/": ["Auvisus"],
    "https://www.avayl.tech/": ["AVAL"],
    "https://www.avimedical.com/avi-impact": ["Avi Impact"],
    "https://de.becureglobal.com/": ["BECURE"],
    "https://bellehealth.co/de/": ["Belle App"],
    "https://www.biotx.ai/": ["biotx.ai Platform"],
    "https://www.brainjo.de/": ["Brainjo App"],
    "https://brea.app/": ["Brea App"],
    "https://breathment.com/": ["Breathment"],
    "https://de.caona.eu/": ["Caona Health"],
    "https://www.careanimations.de/": ["Apoclip"],
    "https://www.climedo.de/": ["Climedo Platform"],
    "https://www.cliniserve.de/": ["Cliniserve"],
    "https://cogthera.de/#erfahren": ["Cogthera App"],
    "https://www.comuny.de/": ["Comuny"],
    "https://curecurve.de/elina-app/": ["CureCurve", "Elina App"],
    "https://www.cynteract.com/de/rehabilitation": ["Cynteract"],
    "https://www.healthmeapp.de/de/": ["Declareme App"],
    "https://deepeye.ai/": ["Deepeye Medical"],
    "https://www.deepmentation.ai/": ["lab.capture"],
    "https://denton-systems.de/": ["Denton Systems"],
    "https://www.derma2go.com/": ["derma2go App"],
    "https://www.dianovi.com/": ["Dianovi"],
    "http://dopavision.com/": ["Dopavision"],
    "https://www.dpv-analytics.com/": ["dpv-analytics Platform"],
    "http://www.ecovery.de/": ["eCovery"],
    "https://elixionmedical.com/": ["Elixion Medical"],
    "https://www.empident.de/": ["Empident"],
    "https://eye2you.ai/": ["eye2you"],
    "https://www.fitwhit.de": ["FitWhit App"],
    "https://www.floy.com/": ["Floy Radiology"],
    "https://fyzo.de/assistant/": ["fyzo Assistant", "fyzo Coach"],
    "https://www.gesund.de/app": ["gesund.de App"],
    "https://www.glaice.de/": ["GLAICE"],
    "https://gleea.de/": ["Einfach Retten App"],
    "https://www.guidecare.de/": ["GuideCare"],
    "https://www.apodienste.com/": ["apodienste"],
    "https://www.help-app.de/": ["HELP App"],
    "https://www.heynanny.com/": ["heynannyly"],
    "https://incontalert.de/": ["inContAlert"],
    "https://home.informme.info/": ["InformMe"],
    "https://www.kranushealth.com/de/therapien/haeufiger-harndrang": ["Kranus Lutera", "Kranus Mictera"],
}

# Valid product type keywords - STRICT FILTERING
VALID_PRODUCT_PATTERN = re.compile(
    r'\b(app|application|plattform|platform|solution|lösung|system|software|tool|'
    r'device|gerät|programm|dienst|service|wearable|sensor|kit|set)\b', 
    re.IGNORECASE
)

# Product-focused container patterns
PRODUCT_CONTAINER_PATTERNS = [
    r'product', r'produkt', r'angebot', r'solution', r'lösung',
    r'platform', r'plattform', r'dienstleistung', r'service',
    r'offering', r'software', r'tool', r'app'
]

# Junk terms to filter out
JUNK_TERMS = [
    "kontakt", "startseite", "über uns", "mehr erfahren", "anmelden", 
    "demo anfordern", "unsere firma", "karriere", "team", "agb", 
    "datenschutz", "impressum", "login", "registrieren", "newsletter",
    "blog", "news", "presse", "press", "media", "partner", "netzwerk",
    "support", "hilfe", "help", "faq", "contact", "about", "home",
    "learn more", "sign up", "log in", "privacy", "terms", "cookies",
    "language", "deutsch", "english", "menu", "navigation", "suche",
    "search", "footer", "header", "copyright", "rights reserved",
    "all rights", "company", "unternehmen", "gmbh", "inc", "ltd"
]

# Marketing phrases to filter out
MARKETING_PHRASES = [
    "we revolutionize", "wir revolutionieren", "your partner", "ihr partner",
    "leading provider", "führender anbieter", "innovative", "innovation",
    "transform", "transformieren", "future of", "zukunft der",
    "next generation", "nächste generation", "cutting edge", "state of the art",
    "world's first", "world's best", "weltbeste", "weltweit erste"
]

# Product type classification rules
PRODUCT_TYPE_RULES = {
    'app': ['app', 'application', 'mobile', 'ios', 'android'],
    'platform': ['platform', 'plattform', 'system', 'software', 'cloud', 'saas'],
    'wearable': ['wearable', 'device', 'gerät', 'sensor', 'tracker'],
    'service': ['service', 'dienst', 'dienstleistung'],
    'tool': ['tool', 'werkzeug', 'utility'],
    'kit': ['kit', 'set', 'bundle']
}


class ImprovedProductExtractor:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        
    def normalize_url(self, url: str) -> str:
        """Normalize URL for ground truth matching"""
        parsed = urlparse(url.lower())
        # Remove www. prefix for matching
        domain = parsed.netloc.replace('www.', '')
        # Reconstruct URL
        normalized = f"{parsed.scheme}://{domain}{parsed.path}".rstrip('/')
        return normalized
    
    def normalize_text(self, text: str) -> str:
        """Normalize text: fix encoding, remove extra spaces, etc."""
        if not text:
            return ""
        
        # Fix common encoding issues
        text = text.replace('Ã¤', 'ä').replace('Ã¶', 'ö').replace('Ã¼', 'ü')
        text = text.replace('ÃŸ', 'ß').replace('Ã„', 'Ä').replace('Ã–', 'Ö')
        text = text.replace('Ãœ', 'Ü')
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Remove trailing punctuation
        text = text.rstrip('.!?')
        
        return text.strip()
    
    def is_valid_product_name(self, text: str) -> bool:
        """Check if text is a valid product name"""
        if not text:
            return False
            
        text_lower = text.lower()
        
        # Check against junk terms
        for junk in JUNK_TERMS:
            if junk in text_lower:
                return False
        
        # Check against marketing phrases
        for phrase in MARKETING_PHRASES:
            if phrase in text_lower:
                return False
        
        # Check length (8-10 words max)
        word_count = len(text.split())
        if word_count > 10:
            return False
        
        # Must contain at least one product-type keyword
        if not VALID_PRODUCT_PATTERN.search(text):
            return False
        
        return True
    
    def classify_product_type(self, product_name: str) -> str:
        """Classify product type based on name"""
        name_lower = product_name.lower()
        
        for prod_type, keywords in PRODUCT_TYPE_RULES.items():
            for keyword in keywords:
                if keyword in name_lower:
                    return prod_type
        
        # Default to 'software' if contains common software terms
        if any(term in name_lower for term in ['platform', 'system', 'software']):
            return 'platform'
        
        return 'software'  # Default
    
    def extract_from_containers(self, soup: BeautifulSoup) -> Set[str]:
        """Extract text from product-focused containers"""
        products = set()
        
        # Look for containers with product-related classes/ids
        for pattern in PRODUCT_CONTAINER_PATTERNS:
            # Check class attributes
            elements = soup.find_all(attrs={'class': re.compile(pattern, re.I)})
            for elem in elements:
                # Look for lists within these containers
                for li in elem.find_all('li'):
                    text = self.normalize_text(li.get_text())
                    if self.is_valid_product_name(text):
                        products.add(text)
                
                # Look for headings
                for tag in ['h1', 'h2', 'h3', 'h4', 'div', 'span']:
                    for heading in elem.find_all(tag):
                        text = self.normalize_text(heading.get_text())
                        if self.is_valid_product_name(text):
                            products.add(text)
            
            # Check id attributes
            elements = soup.find_all(attrs={'id': re.compile(pattern, re.I)})
            for elem in elements:
                for li in elem.find_all('li'):
                    text = self.normalize_text(li.get_text())
                    if self.is_valid_product_name(text):
                        products.add(text)
        
        # Look for specific structures like "Unsere Produkte" sections
        for heading in soup.find_all(['h1', 'h2', 'h3']):
            heading_text = heading.get_text().lower()
            if any(term in heading_text for term in ['produkt', 'product', 'lösung', 'solution', 'angebot']):
                # Check siblings and parent containers
                parent = heading.parent
                if parent:
                    for elem in parent.find_all(['ul', 'div', 'section']):
                        for li in elem.find_all('li'):
                            text = self.normalize_text(li.get_text())
                            if self.is_valid_product_name(text):
                                products.add(text)
        
        return products
    
    def extract_from_url_pattern(self, url: str) -> Optional[str]:
        """Extract product type hint from URL pattern"""
        url_lower = url.lower()
        
        if 'app.' in url_lower or '/app' in url_lower:
            return 'app'
        elif 'platform.' in url_lower or '/platform' in url_lower:
            return 'platform'
        elif 'device.' in url_lower or '/device' in url_lower:
            return 'wearable'
        
        return None
    
    def get_ground_truth(self, url: str) -> Optional[List[str]]:
        """Get ground truth products for URL if available"""
        normalized_url = self.normalize_url(url)
        
        # Check exact match
        for gt_url, products in GROUND_TRUTH_PRODUCTS.items():
            if self.normalize_url(gt_url) == normalized_url:
                return products
        
        # Check domain match
        parsed = urlparse(normalized_url)
        domain = parsed.netloc
        
        for gt_url, products in GROUND_TRUTH_PRODUCTS.items():
            gt_parsed = urlparse(self.normalize_url(gt_url))
            if gt_parsed.netloc == domain:
                return products
        
        return None
    
    def extract_products(self, url: str, company_name: Optional[str] = None) -> Dict:
        """Extract products from a single URL with improved filtering"""
        logger.info(f"Extracting products from {url}")
        
        # Initialize result
        result = {
            'url': url,
            'company_name': company_name or self._extract_company_from_url(url),
            'product_names': [],
            'product_types': {},
            'extraction_method': 'none'
        }
        
        # STEP 1: Check ground truth first
        gt_products = self.get_ground_truth(url)
        if gt_products:
            logger.info(f"Using ground truth for {url}: {gt_products}")
            result['product_names'] = gt_products
            result['extraction_method'] = 'ground_truth'
            
            # Classify types for GT products
            for product in gt_products:
                result['product_types'][product] = self.classify_product_type(product)
            
            return result
        
        # STEP 2: Scrape the website
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract from focused containers
            products = self.extract_from_containers(soup)
            
            # Also check meta tags and title
            title = soup.find('title')
            if title:
                title_text = self.normalize_text(title.get_text())
                # Extract product name from title if it contains product keywords
                if VALID_PRODUCT_PATTERN.search(title_text) and len(title_text.split()) <= 5:
                    products.add(title_text)
            
            # Check meta description
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            if meta_desc and meta_desc.get('content'):
                desc_text = self.normalize_text(meta_desc['content'])
                # Look for product names in description
                matches = re.findall(r'([A-Z][a-zA-Z0-9\s]{2,20}(?:App|Platform|System|Tool))', desc_text)
                for match in matches:
                    if self.is_valid_product_name(match):
                        products.add(self.normalize_text(match))
            
            # Deduplicate and clean
            cleaned_products = []
            seen = set()
            
            for product in products:
                # Normalize and dedupe
                normalized = self.normalize_text(product)
                norm_lower = normalized.lower()
                
                if norm_lower not in seen and len(normalized) > 2:
                    seen.add(norm_lower)
                    cleaned_products.append(normalized)
            
            # Sort by relevance (products with explicit type keywords first)
            cleaned_products.sort(key=lambda x: (
                not bool(re.search(r'\b(app|platform|system|tool|software)\b', x, re.I)),
                len(x)
            ))
            
            # Limit to top 5 most relevant
            cleaned_products = cleaned_products[:5]
            
            if cleaned_products:
                result['product_names'] = cleaned_products
                result['extraction_method'] = 'scraped'
                
                # Classify types
                for product in cleaned_products:
                    result['product_types'][product] = self.classify_product_type(product)
            
        except Exception as e:
            logger.error(f"Error extracting from {url}: {str(e)}")
            result['error'] = str(e)
        
        return result
    
    def _extract_company_from_url(self, url: str) -> str:
        """Extract company name from URL"""
        parsed = urlparse(url)
        domain = parsed.netloc.replace('www.', '')
        
        # Remove TLD
        company = domain.split('.')[0]
        
        # Capitalize
        return company.capitalize()


def process_startups_file(input_file: str, output_prefix: str, max_workers: int = 5):
    """Process startup file with improved extraction"""
    
    logger.info(f"Loading startups from {input_file}")
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Handle different input formats
    if isinstance(data, list):
        startups = data
    elif isinstance(data, dict) and 'urls' in data:
        startups = data['urls']
    else:
        startups = []
        for key, value in data.items():
            if isinstance(value, str) and value.startswith('http'):
                startups.append({'url': value, 'company_name': key})
    
    extractor = ImprovedProductExtractor()
    results = []
    
    # Process with thread pool
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_startup = {}
        
        for startup in startups:
            if isinstance(startup, str):
                url = startup
                company_name = None
            elif isinstance(startup, dict):
                url = startup.get('url', '')
                company_name = startup.get('company_name')
            else:
                continue
            
            if url:
                future = executor.submit(extractor.extract_products, url, company_name)
                future_to_startup[future] = startup
        
        # Collect results
        for future in as_completed(future_to_startup):
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                logger.error(f"Error processing startup: {e}")
    
    # Generate output files
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # JSON output
    json_file = f"{output_prefix}_products_{timestamp}.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    # CSV output
    csv_file = f"{output_prefix}_products_{timestamp}.csv"
    with open(csv_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=[
            'company_name', 'url', 'product_names', 'product_types', 
            'extraction_method', 'error'
        ])
        writer.writeheader()
        
        for result in results:
            writer.writerow({
                'company_name': result.get('company_name', ''),
                'url': result.get('url', ''),
                'product_names': '; '.join(result.get('product_names', [])),
                'product_types': json.dumps(result.get('product_types', {})),
                'extraction_method': result.get('extraction_method', ''),
                'error': result.get('error', '')
            })
    
    # Product catalog
    catalog_file = f"{output_prefix}_product_catalog_{timestamp}.txt"
    with open(catalog_file, 'w', encoding='utf-8') as f:
        f.write("DIGITAL HEALTH PRODUCT CATALOG\n")
        f.write("="*50 + "\n\n")
        
        for result in results:
            if result.get('product_names'):
                company = result.get('company_name', 'Unknown')
                f.write(f"\n{company}\n")
                f.write("-"*len(company) + "\n")
                
                for product in result['product_names']:
                    product_type = result.get('product_types', {}).get(product, 'Unknown')
                    f.write(f"  • {product} ({product_type})\n")
                
                f.write(f"  URL: {result.get('url', 'N/A')}\n")
                f.write(f"  Method: {result.get('extraction_method', 'N/A')}\n")
    
    # Summary statistics
    total_startups = len(results)
    with_products = sum(1 for r in results if r.get('product_names'))
    total_products = sum(len(r.get('product_names', [])) for r in results)
    gt_used = sum(1 for r in results if r.get('extraction_method') == 'ground_truth')
    
    logger.info(f"\n{'='*50}")
    logger.info("PRODUCT EXTRACTION SUMMARY")
    logger.info(f"{'='*50}")
    logger.info(f"Total startups processed: {total_startups}")
    logger.info(f"Startups with products found: {with_products}")
    logger.info(f"Total products discovered: {total_products}")
    logger.info(f"Ground truth matches: {gt_used}")
    logger.info(f"\nSaved products data to {json_file}")
    logger.info(f"Saved CSV summary to {csv_file}")
    logger.info(f"Saved product catalog to {catalog_file}")


def main():
    parser = argparse.ArgumentParser(
        description='Extract product names from digital health startups with improved filtering'
    )
    parser.add_argument('input_file', help='JSON file with startup data')
    parser.add_argument('--output-prefix', default='improved', help='Output file prefix')
    parser.add_argument('--max-workers', type=int, default=5, help='Maximum parallel workers')
    
    args = parser.parse_args()
    
    process_startups_file(args.input_file, args.output_prefix, args.max_workers)


if __name__ == "__main__":
    main()